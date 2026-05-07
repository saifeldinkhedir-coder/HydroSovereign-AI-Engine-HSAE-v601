"""
HSAE v6.0.8 — Interactive Basin Risk Map Panel
================================================
Pure Qt — no QWebEngineView required.
Shows all 26 basins with ATDI/AHIFD/CI risk table.
Opens full Leaflet map in browser when requested.
Author: Seifeldin M.G. Alkhedir · ORCID: 0000-0003-0821-2991
"""
from __future__ import annotations
import json
import os
import tempfile
from typing import Optional

try:
    from qgis.PyQt.QtWidgets import (
        QDockWidget, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QTableWidget, QTableWidgetItem,
        QHeaderView, QAbstractItemView, QFrame, QScrollArea)
    from qgis.PyQt.QtCore import Qt
    from qgis.PyQt.QtGui import QColor, QBrush, QFont
    HAS_QT = True
except ImportError:
    HAS_QT = False

from qgis.core import QgsMessageLog, Qgis

LIVE_APP = "https://hydrosovereign-ai-engine-hsae-v601-6euz2zxcmerkzxgordmvxf.streamlit.app"


def _risk_color(atdi: float) -> str:
    if atdi >= 60:
        return "#c0392b"
    elif atdi >= 40:
        return "#e67e22"
    elif atdi >= 25:
        return "#f1c40f"
    return "#27ae60"


def _risk_label(atdi: float) -> str:
    if atdi >= 60:
        return "CRITICAL"
    elif atdi >= 40:
        return "HIGH"
    elif atdi >= 25:
        return "MEDIUM"
    return "LOW"


class HSAEMapPanel(QDockWidget if HAS_QT else object):
    """Dock panel: Basin Risk Map (pure Qt table + browser fallback)."""

    def __init__(self, iface, basins: list):
        if not HAS_QT:
            return
        super().__init__("🗺️ HSAE — Basin Risk Map", iface.mainWindow())
        self.iface = iface
        self._basins = basins
        self.setMinimumWidth(560)
        self.setMinimumHeight(500)
        self.setFloating(True)

        root = QWidget()
        self.setWidget(root)
        main = QVBoxLayout(root)
        main.setSpacing(8)
        main.setContentsMargins(10, 10, 10, 10)

        # ── Title ─────────────────────────────────────────
        title = QLabel(
            "<b style='font-size:13px;color:#0E6B6A'>"
            "🗺️ Global Basin Risk Map — 26 Basins</b>")
        title.setTextFormat(Qt.RichText)
        main.addWidget(title)

        sub = QLabel(
            "ATDI · AHIFD · Conflict Index · UNWC 1997 Compliance")
        sub.setStyleSheet("color:#666;font-size:11px")
        main.addWidget(sub)

        # ── Buttons ───────────────────────────────────────
        btn_row = QHBoxLayout()

        btn_browser = QPushButton("🌐  Open Full Interactive Map (Browser)")
        btn_browser.setStyleSheet(
            "background:#0E6B6A;color:white;padding:6px 12px;"
            "border-radius:5px;font-weight:bold;font-size:11px")
        btn_browser.clicked.connect(self._open_in_browser)
        btn_row.addWidget(btn_browser)

        btn_app = QPushButton("☁️  Open Streamlit App")
        btn_app.setStyleSheet(
            "background:#2C3E50;color:white;padding:6px 12px;"
            "border-radius:5px;font-size:11px")
        btn_app.clicked.connect(lambda: __import__('webbrowser').open(LIVE_APP))
        btn_row.addWidget(btn_app)

        btn_refresh = QPushButton("↻  Refresh")
        btn_refresh.setStyleSheet(
            "background:#eee;color:#333;padding:6px 10px;"
            "border-radius:5px;font-size:11px")
        btn_refresh.clicked.connect(self._populate)
        btn_row.addWidget(btn_refresh)
        main.addLayout(btn_row)

        # ── Risk legend ───────────────────────────────────
        legend = QLabel(
            "<span style='color:#c0392b'>■ CRITICAL (≥60%)</span>&nbsp;&nbsp;"
            "<span style='color:#e67e22'>■ HIGH (≥40%)</span>&nbsp;&nbsp;"
            "<span style='color:#f1c40f'>■ MEDIUM (≥25%)</span>&nbsp;&nbsp;"
            "<span style='color:#27ae60'>■ LOW</span>")
        legend.setTextFormat(Qt.RichText)
        legend.setStyleSheet("font-size:10px;margin:2px 0")
        main.addWidget(legend)

        # ── Table ─────────────────────────────────────────
        self._table = QTableWidget()
        self._table.setColumnCount(6)
        self._table.setHorizontalHeaderLabels(
            ["Basin", "ATDI %", "AHIFD %", "CI", "Risk", "UNWC Art.7"])
        self._table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.Stretch)
        for col in range(1, 6):
            self._table.horizontalHeader().setSectionResizeMode(
                col, QHeaderView.ResizeToContents)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.setStyleSheet(
            "QTableWidget{border:1px solid #ddd;font-size:11px}"
            "QTableWidget::item{padding:3px}"
            "QHeaderView::section{background:#0E6B6A;color:white;"
            "font-weight:bold;padding:4px;border:none}")
        self._table.verticalHeader().setVisible(False)
        main.addWidget(self._table)

        self._populate()

    def _compute(self, basin: dict) -> dict:
        """Compute key indices for a basin."""
        disp = basin.get("dispute_level", 2)
        cap = basin.get("dam_capacity_bcm", 50)
        nc = basin.get("num_countries", 3)
        rc = basin.get("riparian_cooperation", 0.45)
        atdi = round(min(95, max(5,
            15 + disp * 12 + min(cap / 2, 20) + (nc - 2) * 8 + (1 - rc) * 10)), 1)
        ahifd = round(min(80, max(5,
            8 + min(cap / 3, 15) + (1 - rc) * 12 + disp * 5 + (nc - 2) * 3)), 1)
        ci = round(min(100, max(0,
            disp * 15 + (1 - rc) * 30 + (nc - 2) * 5 + min(cap / 5, 20))), 0)
        return {"atdi": atdi, "ahifd": ahifd, "ci": int(ci)}

    def _populate(self) -> None:
        """Fill the risk table with all 26 basins."""
        self._table.setRowCount(0)
        for basin in self._basins:
            try:
                d = self._compute(basin)
                name = basin.get("name", "Unknown")
                atdi = d["atdi"]
                ahifd = d["ahifd"]
                ci = d["ci"]
                risk = _risk_label(atdi)
                art7 = "⚠ Triggered" if atdi >= 40 else "✓ OK"
                color = _risk_color(atdi)

                row = self._table.rowCount()
                self._table.insertRow(row)

                items = [
                    (name, None),
                    (f"{atdi}%", color),
                    (f"{ahifd}%", None),
                    (str(ci), None),
                    (risk, color),
                    (art7, "#c0392b" if atdi >= 40 else "#27ae60"),
                ]
                for col, (text, fg) in enumerate(items):
                    item = QTableWidgetItem(text)
                    item.setTextAlignment(Qt.AlignCenter)
                    if fg:
                        item.setForeground(QBrush(QColor(fg)))
                    if col == 4:
                        font = QFont()
                        font.setBold(True)
                        item.setFont(font)
                        item.setBackground(QBrush(QColor(color + "22")))
                    self._table.setItem(row, col, item)
            except Exception:
                pass

        self._table.sortItems(1, Qt.DescendingOrder)

    def _build_leaflet_html(self) -> str:
        """Build a Leaflet.js HTML map of all basins."""
        marker_lines = []
        for b in self._basins:
            try:
                d = self._compute(b)
                lat = b.get("lat", 0)
                lon = b.get("lon", 0)
                name = b.get("name", "Unknown").replace("'", " ")
                color = _risk_color(d["atdi"])
                popup = name + " | ATDI:" + str(d["atdi"]) + "% | " + _risk_label(d["atdi"])
                marker_lines.append(
                    "L.circleMarker([" + str(lat) + "," + str(lon) + "],"
                    + "{radius:10,color:'" + color + "',fillColor:'" + color
                    + "',fillOpacity:0.8}).addTo(map)"
                    + ".bindPopup('" + popup + "');"
                )
            except Exception:
                pass

        markers_js = "\n".join(marker_lines)
        html = (
            "<!DOCTYPE html><html><head>"
            "<meta charset='utf-8'>"
            "<link rel='stylesheet' href='https://unpkg.com/leaflet@1.9/dist/leaflet.css'/>"
            "<script src='https://unpkg.com/leaflet@1.9/dist/leaflet.js'></script>"
            "<style>html,body,#map{margin:0;padding:0;height:100vh}</style>"
            "</head><body><div id='map'></div><script>"
            "var map=L.map('map').setView([20,30],2);"
            "L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',"
            "{attribution:'OpenStreetMap'}).addTo(map);"
            + markers_js
            + "</script></body></html>"
        )
        return html

    def _open_in_browser(self) -> None:
        """Save Leaflet map to temp file and open in browser."""
        try:
            html = self._build_leaflet_html()
            tmp = tempfile.NamedTemporaryFile(
                suffix=".html", delete=False, mode="w", encoding="utf-8")
            tmp.write(html)
            tmp.close()
            import webbrowser
            webbrowser.open(f"file://{tmp.name}")
        except Exception as e:
            QgsMessageLog.logMessage(
                f"HSAE Map error: {e}", "HSAE", Qgis.Warning)

    def update_basin(self, basin: dict) -> None:
        self._populate()
