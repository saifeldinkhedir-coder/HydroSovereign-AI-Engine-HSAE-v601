"""
HSAE v6.0.13 — Treaty Analysis Panel (ATCI)
============================================
Pure Qt (no WebEngine) — works in all QGIS versions.
Displays ATCI Treaty Compliance Index for any basin.
"""
from __future__ import annotations
import random
from hsae_qgis.core.indices import compute_all


try:
    from qgis.PyQt.QtWidgets import (
        QDockWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QProgressBar,
        QGroupBox, QGridLayout, QScrollArea, QFrame)
    from qgis.PyQt.QtCore import Qt
    HAS_QT = True
except ImportError:
    HAS_QT = False

UNWC_ARTICLES = [
    ("Art. 5", "Equitable & reasonable utilisation"),
    ("Art. 6", "Factors for equitable utilisation"),
    ("Art. 7", "No significant harm obligation"),
    ("Art. 9", "Regular exchange of data & info"),
    ("Art. 11", "Prior notification of planned measures"),
    (
        "Art. 12", "Six-month reply period"),
    ("Art. 17", "Peaceful settlement / consultations"),
    ("Art. 20", "Protection & preservation of ecosystems"),
    ("Art. 21", "Prevention of water pollution"),
    ("Art. 33", "Dispute settlement mechanism"),
]


class HSAETreatyPanel(QDockWidget if HAS_QT else object):
    """Dock panel: ATCI analysis for selected basin."""

    def __init__(self, iface, basins: list):
        if not HAS_QT:
            return
        super().__init__("⚖️ HSAE — Treaty Analysis (ATCI)", iface.mainWindow())
        self.iface = iface
        self._basins = basins
        self.setMinimumWidth(440)
        self.setMinimumHeight(520)
        self.setFloating(True)

        root = QWidget()
        self.setWidget(root)
        main = QVBoxLayout(root)
        main.setSpacing(8)
        main.setContentsMargins(10, 10, 10, 10)

        # Title
        title = QLabel("<b style='font-size:13px;color:#0E6B6A'>"
                       "ATCI — Alkhedir Treaty Compliance Index</b>")
        title.setTextFormat(Qt.RichText)
        main.addWidget(title)

        sub = QLabel("Article-by-article assessment vs UNWC 1997")
        sub.setStyleSheet("color:#666;font-size:11px")
        main.addWidget(sub)

        # Basin selector
        row = QHBoxLayout()
        row.addWidget(QLabel("Basin:"))
        self._combo = QComboBox()
        for b in self._basins:
            self._combo.addItem(b.get("name", "Unknown"))
        row.addWidget(self._combo, 1)
        btn = QPushButton("▶  Analyse")
        btn.setStyleSheet(
            "background:#0E6B6A;color:white;padding:5px 12px;"
            "border-radius:5px;font-weight:bold")
        btn.clicked.connect(self._analyse)
        row.addWidget(btn)
        main.addLayout(row)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color:#ddd")
        main.addWidget(line)

        # Scroll area for results
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self._res_widget = QWidget()
        self._res_layout = QVBoxLayout(self._res_widget)
        self._res_layout.setSpacing(6)
        scroll.setWidget(self._res_widget)
        main.addWidget(scroll)

        # Placeholder
        ph = QLabel("<i style='color:#888'>Select a basin and press Analyse.</i>")
        ph.setTextFormat(Qt.RichText)
        self._res_layout.addWidget(ph)
        self._res_layout.addStretch()

    def _analyse(self) -> None:
        # Clear
        for i in reversed(range(self._res_layout.count())):
            w = self._res_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        idx = self._combo.currentIndex()
        basin = self._basins[idx] if idx < len(self._basins) else {}
        name = basin.get("name", "Unknown")
        disp = basin.get("dispute_level", 2)
        cap = float(basin.get("cap", basin.get("cap_bcm", basin.get("dam_capacity_bcm", 74))))
        _nc_raw = basin.get("country", basin.get("countries", None))
        nc = max(2, len(_nc_raw)) if isinstance(_nc_raw, list) else int(
            basin.get("n_countries", basin.get("num_countries", 3)))
        rc = float(basin.get("runoff_c", basin.get("riparian_cooperation", 0.38)))

        # Compute ATCI
        _r = compute_all(runoff_c=rc, cap_bcm=cap,
                         n_countries=int(nc), dispute_level=int(disp))
        atci = _r['atci']

        # Overall metric
        color = ("#c0392b" if atci > 60 else
                 "#e67e22" if atci > 40 else "#27ae60")
        status = ("HIGH RISK" if atci > 60 else
                  "MEDIUM RISK" if atci > 40 else "LOW RISK")

        hdr = QLabel(
            f"<b style='font-size:12px'>{name}</b>&nbsp;&nbsp;"
            f"<span style='color:{color};font-weight:bold'>"
            f"ATCI = {atci} — {status}</span>")
        hdr.setTextFormat(Qt.RichText)
        self._res_layout.addWidget(hdr)

        bar = QProgressBar()
        bar.setMinimum(0)
        bar.setMaximum(100)
        bar.setValue(int(atci))
        bar.setFormat(f"ATCI = {atci}")
        bar.setStyleSheet(
            f"QProgressBar::chunk{{background:{color};border-radius:3px}}")
        self._res_layout.addWidget(bar)

        # Article-by-article
        grp = QGroupBox("UNWC 1997 — Article Assessment")
        grp.setStyleSheet(
            "QGroupBox{font-weight:bold;color:#2C3E50;"
            "border:1px solid #bdc3c7;border-radius:4px;margin-top:8px}"
            "QGroupBox::title{subcontrol-origin:margin;left:8px}")
        g = QGridLayout(grp)
        g.setHorizontalSpacing(12)
        g.setVerticalSpacing(4)

        for row_i, (art, desc) in enumerate(UNWC_ARTICLES):
            # Simple rule-based compliance per article
            score = self._article_score(art, disp, cap, nc, rc)
            art_color = "#c0392b" if score < 40 else "#e67e22" if score < 65 else "#27ae60"
            art_status = "⚠ Non-compliant" if score < 40 else "~ Partial" if score < 65 else "✓ Compliant"

            lbl_art = QLabel(f"<b>{art}</b>")
            lbl_art.setTextFormat(Qt.RichText)
            lbl_desc = QLabel(desc)
            lbl_desc.setStyleSheet("color:#555;font-size:10px")
            lbl_stat = QLabel(
                f"<span style='color:{art_color}'>{art_status}</span>")
            lbl_stat.setTextFormat(Qt.RichText)

            g.addWidget(lbl_art, row_i, 0)
            g.addWidget(lbl_desc, row_i, 1)
            g.addWidget(lbl_stat, row_i, 2)

        self._res_layout.addWidget(grp)
        self._res_layout.addStretch()

    def _article_score(self, art, disp, cap, nc, rc):
        """Simple rule-based article score 0-100."""
        base = int(rc * 60 + (3 - disp) * 10)
        offsets = {
            "Art. 5": 10, "Art. 6": 8, "Art. 7": -int(disp * 15),
            "Art. 9": -5, "Art. 11": -int(cap / 10), "Art. 12": 5,
            "Art. 17": -int(disp * 8), "Art. 20": 5, "Art. 21": 0,
            "Art. 33": -int(disp * 5), }
        return max(5, min(95, base + offsets.get(art, 0) + random.randint(-3, 3)))
