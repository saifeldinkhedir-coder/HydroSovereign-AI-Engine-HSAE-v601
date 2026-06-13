"""
dialog_main.py — HSAE v6.0.12 Dashboard Dialog
===============================================
Shows all 26 basins with 6 computed indices:
ATDI · AHIFD · CI · ATCI · NSE · KGE · Risk
"""
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QTabWidget, QWidget, QTextEdit, QHeaderView
)
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QFont, QColor
import webbrowser
from hsae_qgis.core.indices import compute_all


def _compute_indices(b):
    """Compute all 6 HSAE indices for a basin dict."""
    disp = float(b.get("dispute_level", b.get("disp", 2)))
    cap = float(b.get("cap_bcm", b.get("cap", 10)))
    nc = float(b.get("n_countries", b.get("num_countries", 3)))
    rc = float(b.get("runoff_c", 0.35))
    _r = compute_all(runoff_c=rc, cap_bcm=cap, n_countries=int(nc), dispute_level=int(disp))
    atdi = _r['atdi']
    ahifd = _r['ahifd']
    afsf = _r['afsf']
    ahlb = _r['ahlb']
    asi = _r['asi']
    atci = _r['atci']
    ci = _r['ci']
    pneg = _r['pneg']
    nse = _r['nse']
    kge = _r['kge']

    # Risk from central engine (CRITICAL≥60 · HIGH≥40 · MODERATE≥25 · LOW)
    risk = _r['risk']

    region = b.get("continent", b.get("region", "—"))
    for emoji in ["🌍 ", "🌎 ", "🌏 ", "🌍", "🌎", "🌏"]:
        region = region.replace(emoji, "")

    countries = b.get("country", [])
    upstream = b.get("country_up", countries[0] if countries else "—")
    downstream = b.get("country_dn", "") or (
        " / ".join(countries[1:]) if len(countries) > 1 else "—")

    return {
        "atdi": atdi, "ahifd": ahifd, "ci": ci,
        "afsf": afsf, "ahlb": ahlb, "asi": asi, "pneg": pneg,
        "atci": atci, "nse": nse, "kge": kge,
        "risk": risk, "region": region,
        "upstream": upstream, "downstream": downstream,
    }


class HSAEMainDialog(QDialog):

    def __init__(self, iface, basins):
        super().__init__(iface.mainWindow())
        self.iface = iface
        self.basins = basins
        self.setWindowTitle("🌊 HydroSovereign AI Engine v6.0.12")
        self.setMinimumSize(1000, 620)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()

        header = QLabel("🌊 HydroSovereign AI Engine — HSAE v6.0.12")
        header.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        header.setFont(font)
        layout.addWidget(header)

        sub = QLabel(
            "26 Basins · 6 Indices · ATDI · AHIFD · CI · ATCI · NSE · KGE  |  "
            "Author: Seifeldin M.G. Alkhedir · ORCID: 0000-0003-0821-2991")
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet("color:#555;font-size:11px")
        layout.addWidget(sub)

        tabs = QTabWidget()
        tabs.addTab(self._build_basins_tab(), "📊 26 Basins — All Indices")
        tabs.addTab(self._build_summary_tab(), "📈 Risk Summary")
        tabs.addTab(self._build_about_tab(), "ℹ About")
        layout.addWidget(tabs)

        btns = QHBoxLayout()
        for label, url in [
            ("🚀 Open Live App",
             "https://hydrosovereign-ai-engine-hsae-v6.0.8-6euz2zxcmerkzxgordmvxf.streamlit.app"),
            ("📦 GitHub Repo",
             "https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601"),
            ("🌐 Website",
             "https://saifeldinkhedir-coder.github.io/hydrosovereign.org/"),
        ]:
            btn = QPushButton(label)
            btn.setStyleSheet(
                "background:#0E6B6A;color:white;padding:5px 14px;"
                "border-radius:5px;font-weight:bold")
            btn.clicked.connect(lambda checked, u=url: webbrowser.open(u))
            btns.addWidget(btn)
        close = QPushButton("✖ Close")
        close.clicked.connect(self.accept)
        close.setStyleSheet(
            "background:#c0392b;color:white;padding:5px 14px;border-radius:5px")
        btns.addWidget(close)
        layout.addLayout(btns)

        self.setLayout(layout)

    def _build_basins_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        table = QTableWidget()
        table.setColumnCount(9)
        table.setHorizontalHeaderLabels(
            ["Basin", "Region", "ATDI%", "AHIFD%", "CI", "ATCI", "NSE", "KGE", "Risk"])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for c in range(1, 9):
            table.horizontalHeader().setSectionResizeMode(
                c, QHeaderView.ResizeToContents)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.setSortingEnabled(True)
        table.setStyleSheet(
            "QTableWidget{font-size:11px}"
            "QHeaderView::section{background:#0E6B6A;color:white;"
            "font-weight:bold;padding:4px;border:none}")
        table.verticalHeader().setVisible(False)
        table.setRowCount(len(self.basins))

        RISK_COLORS = {
            "CRITICAL": QColor("#F1948A"),
            "HIGH": QColor("#FADBD8"),
            "MODERATE": QColor("#FDEBD0"),
            "LOW": QColor("#D5F5E3"),
        }

        for i, b in enumerate(self.basins):
            d = _compute_indices(b)
            row_data = [
                b.get("name", ""),
                d["region"],
                str(d["atdi"]) + "%",
                str(d["ahifd"]) + "%",
                str(d["ci"]),
                str(d["atci"]),
                str(d["nse"]),
                str(d["kge"]),
                d["risk"],
            ]
            bg = RISK_COLORS.get(d["risk"], QColor("white"))
            bold = QFont()
            bold.setBold(True)
            for j, val in enumerate(row_data):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(0x84)
                if j >= 2:
                    item.setBackground(bg)
                if j == 8:
                    item.setFont(bold)
                table.setItem(i, j, item)

        layout.addWidget(table)
        widget.setLayout(layout)
        return widget

    def _build_summary_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        indices = [_compute_indices(b) for b in self.basins]
        critical = [b for b, d in zip(self.basins, indices) if d["risk"] == "CRITICAL"]
        high = [b for b, d in zip(self.basins, indices) if d["risk"] == "HIGH"]
        medium = [b for b, d in zip(self.basins, indices) if d["risk"] == "MODERATE"]
        low = [b for b, d in zip(self.basins, indices) if d["risk"] == "LOW"]

        avg_atdi = round(sum(d["atdi"] for d in indices) / len(indices), 1)
        avg_ahifd = round(sum(d["ahifd"] for d in indices) / len(indices), 1)
        avg_nse = round(sum(d["nse"] for d in indices) / len(indices), 2)
        avg_kge = round(sum(d["kge"] for d in indices) / len(indices), 2)

        html = f"""
        <h2 style='color:#0E6B6A'>📈 Risk Summary — {len(self.basins)} Basins</h2>
        <p><b>Platform averages:</b>
           ATDI={avg_atdi}% &nbsp;|&nbsp; AHIFD={avg_ahifd}%
           &nbsp;|&nbsp; NSE={avg_nse} &nbsp;|&nbsp; KGE={avg_kge}</p>
        <p><b>Formula (calibrated v6.0.12):</b> ATDI = 10 + min(cap/8.5, 11) + disp×4.8 + (nc−2)×2 + (1−rc)×6</p>
        <p><b>Thresholds (UNWC 1997):</b>
           ≥60% CRITICAL (Art.33 dispute zone) &nbsp;|&nbsp;
           ≥40% HIGH (Art.7 triggered) &nbsp;|&nbsp;
           ≥25% MODERATE (Art.5 attention) &nbsp;|&nbsp;
           &lt;25% LOW</p>
        <hr>
        <p><span style='color:#c0392b'>🔴 CRITICAL — {len(critical)} basins:</span><br>
        {" · ".join(b.get("name", "") for b in critical) or "—"}</p>
        <p><span style='color:#e67e22'>🟠 HIGH — {len(high)} basins:</span><br>
        {" · ".join(b.get("name", "") for b in high) or "—"}</p>
        <p><span style='color:#f39c12'>🟡 MODERATE — {len(medium)} basins:</span><br>
        {" · ".join(b.get("name", "") for b in medium) or "—"}</p>
        <p><span style='color:#27ae60'>🟢 LOW — {len(low)} basins:</span><br>
        {" · ".join(b.get("name", "") for b in low) or "—"}</p>
        """
        text = QTextEdit()
        text.setReadOnly(True)
        text.setHtml(html)
        layout.addWidget(text)
        widget.setLayout(layout)
        return widget

    def _build_about_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        text = QTextEdit()
        text.setReadOnly(True)
        text.setHtml("""
        <h2>🌊 HydroSovereign AI Engine — HSAE v6.0.12</h2>
        <p>Free, open-source platform automating satellite-based transboundary
        water law compliance for 26 globally contested river basins. GPL-3.0.</p>
        <p><b>6 Original Indices:</b> ATDI · AHIFD · AFSF · AHLB · ASI · ATCI</p>
        <p><b>17 Tools + 6 Processing Algorithms</b></p>
        <p><b>GeoAgent integration:</b> opengeos/GeoAgent PR #79 · merged May 2026</p>
        <p><b>Author:</b> Seifeldin M.G. Alkhedir<br>
        <b>ORCID:</b> 0000-0003-0821-2991<br>
        <b>Affiliation:</b> University of Khartoum<br>
        <b>Email:</b> saifeldinkhedir@gmail.com</p>
        <p><b>Publication:</b> Elsevier SoftwareX · SOFTX-D-26-00442 (under review)<br>
        <b>DOI:</b> 10.5281/zenodo.19180160</p>
        """)
        layout.addWidget(text)
        widget.setLayout(layout)
        return widget
