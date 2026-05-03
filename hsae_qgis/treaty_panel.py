"""
HSAE v6.0.3 — Treaty Analysis Panel
=====================================
Displays ATCI (Alkhedir Treaty Compliance Index) for any basin,
comparing current treaty status against UNWC 1997 obligations.
"""
from __future__ import annotations

try:
    from qgis.PyQt.QtWidgets import (
        QDockWidget,
        QWidget,
        QVBoxLayout,
        QComboBox,
        QPushButton,
        QHBoxLayout,
        QLabel)
    from qgis.PyQt.QtCore import QUrl
    from qgis.PyQt.QtWebEngineWidgets import QWebEngineView
    HAS_WEBENGINE = True
except ImportError:
    HAS_WEBENGINE = False

ARTICLES = [
    (5, "Equitable and Reasonable Utilization", "HIFD > 25%"),
    (7, "Obligation Not to Cause Significant Harm", "ATDI > 20%"),
    (9, "Regular Exchange of Data and Information", "ATDI > 40%"),
    (11, "Information Concerning Planned Measures", "ATDI > 35%"),
    (12, "Notification Concerning Planned Measures", "ATDI > 45%"),
    (17, "Consultations and Negotiations", "ATDI > 50%"),
    (20, "Protection and Preservation of Ecosystems", "HIFD > 30%"),
    (21, "Prevention, Reduction of Pollution", "HIFD > 20%"),
    (33, "Settlement of Disputes", "ATDI > 55%"),
    (35, "Emergency Situations", "ATDI > 70%"),
]


def _build_treaty_html(basin: dict) -> str:
    name = basin.get("name", "Basin")
    atdi = float(basin.get("atf_risk", basin.get("tdi", 0.4) * 100))
    hifd = round(atdi * 0.46, 1)

    rows = ""
    triggered = 0
    for art_n, art_title, threshold in ARTICLES:
        param, val_s = threshold.split(" > ")
        threshold_val = float(val_s.replace("%", ""))
        test_val = atdi if param == "ATDI" else hifd
        is_triggered = test_val > threshold_val
        if is_triggered:
            triggered += 1
        status_text = "⚡ TRIGGERED" if is_triggered else "✅ Compliant"
        status_col = "#dc2626" if is_triggered else "#16a34a"
        row_bg = "#FFF5F5" if is_triggered else "#F0FFF4"
        rows += f"""
      <tr style='background:{row_bg}'>
        <td style='padding:6px 10px;font-weight:700;color:#0B3D8E;
                   white-space:nowrap'>Art. {art_n}</td>
        <td style='padding:6px 10px;font-size:11px'>{art_title}</td>
        <td style='padding:6px 10px;font-size:11px;color:#4A5568'>{threshold}</td>
        <td style='padding:6px 10px;font-weight:700;color:{status_col};
                   white-space:nowrap'>{status_text}</td>
      </tr>"""

    atci = round((triggered / len(ARTICLES)) * 100, 1)
    atci_col = "#dc2626" if atci > 60 else "#ea580c" if atci > 30 else "#16a34a"

    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"/>
<style>
  body{{margin:0;font-family:Arial,sans-serif;background:#f8fafc;color:#1A202C}}
  .hdr{{background:linear-gradient(135deg,#061F4A,#553C9A);color:#fff;padding:12px 16px}}
  .metric{{display:inline-block;background:rgba(255,255,255,0.15);border-radius:8px;
           padding:6px 14px;margin-right:10px;text-align:center}}
  .mv{{font-size:20px;font-weight:800}}.ml{{font-size:10px;opacity:0.8}}
  table{{width:100%;border-collapse:collapse;margin:12px;width:calc(100% - 24px)}}
  th{{background:#061F4A;color:#fff;padding:7px 10px;font-size:11px;text-align:left}}
</style></head>
<body>
<div class="hdr">
  <b>⚖️ Treaty Compliance Analysis — ATCI</b><br>
  <span style='font-size:11px;opacity:0.8'>{name} · Alkhedir Treaty Compliance Index · UNWC 1997</span>
  <div style='margin-top:10px'>
    <div class="metric">
      <div class="mv" style='color:{atci_col}'>{atci}%</div>
      <div class="ml">ATCI Score</div>
    </div>
    <div class="metric">
      <div class="mv">{triggered}/{len(ARTICLES)}</div>
      <div class="ml">Articles Triggered</div>
    </div>
    <div class="metric">
      <div class="mv">{atdi}%</div>
      <div class="ml">ATDI</div>
    </div>
    <div class="metric">
      <div class="mv">{hifd}%</div>
      <div class="ml">HIFD</div>
    </div>
  </div>
</div>
<table>
  <tr>
    <th>Article</th><th>Obligation</th>
    <th>Threshold</th><th>Status</th>
  </tr>
  {rows}
</table>
<p style='font-size:10px;color:#4A5568;margin:0 12px 12px'>
  ATCI (Alkhedir Treaty Compliance Index) = triggered articles / total articles × 100.
  Higher ATCI = more UNWC obligations breached. Seifeldin M.G. Alkhedir · ORCID: 0000-0003-0821-2991
</p>
</body></html>"""


class HSAETreatyPanel(QDockWidget):
    """Dockable treaty compliance analysis panel (ATCI)."""

    TITLE = "⚖️ HSAE Treaty Analysis (ATCI)"

    def __init__(self, iface, basins: list, parent=None):
        super().__init__(self.TITLE, parent)
        self.iface = iface
        self.basins = basins
        self.browser = None
        self.setObjectName("HSAETreatyPanelV603")
        self._build()

    def _build(self):
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Basin selector
        top = QHBoxLayout()
        top.addWidget(QLabel("Basin:"))
        self.combo = QComboBox()
        for b in self.basins:
            self.combo.addItem(b.get("name", "?"), b)
        top.addWidget(self.combo, 1)
        btn = QPushButton("Analyse")
        btn.clicked.connect(self._run)
        top.addWidget(btn)
        top_widget = QWidget()
        top_widget.setLayout(top)
        main_layout.addWidget(top_widget)

        if HAS_WEBENGINE:
            self.browser = QWebEngineView()
            main_layout.addWidget(self.browser)

        self.setWidget(container)
        if self.basins:
            self._run()

    def _run(self):
        basin = self.combo.currentData()
        if basin and self.browser:
            self.browser.setHtml(
                _build_treaty_html(basin), QUrl("about:blank"))

    def update_basin(self, basin: dict):
        idx = next((i for i, b in enumerate(self.basins)
                    if b.get("id") == basin.get("id")), -1)
        if idx >= 0:
            self.combo.setCurrentIndex(idx)
        self._run()
