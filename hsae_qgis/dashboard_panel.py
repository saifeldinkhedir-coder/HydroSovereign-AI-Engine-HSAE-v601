"""
dashboard_panel.py — HSAE v6.01 Real-Time QGIS Dashboard Panel
Author: Seifeldin M.G. Alkhedir · ORCID: 0000-0003-0821-2991
"""
from qgis.PyQt.QtWidgets import (
    QDockWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QFrame,
    QGridLayout,
    QProgressBar,
    QTextEdit,
    QTabWidget,
    QFileDialog)
from qgis.PyQt.QtCore import Qt
from pathlib import Path
import json

DISP_LEVELS = {
    "Blue Nile (GERD)": 4,
    "Nile – High Aswan Dam": 3,
    "Nile – Roseires Dam": 2,
    "Euphrates – Atatürk Dam": 4,
    "Tigris – Mosul Dam": 3,
    "Amu Darya – Nurek Dam": 3,
    "Syr Darya – Toktogul Dam": 4,
    "Mekong – Xayaburi Dam": 3,
    "Indus – Tarbela Dam": 3,
    "Brahmaputra – Subansiri Dam": 3,
    "Ganges – Farakka Barrage": 3,
    "Salween – Myitsone Dam": 3,
    "Colorado – Hoover Dam": 2,
    "Rio Grande – Amistad Dam": 2,
    "Dnieper – Kakhovka Dam": 4,
    "Niger – Kainji Dam": 2,
    "Danube – Iron Gates I": 1,
    "Rhine – Basin": 1,
    "Zambezi – Kariba Dam": 1,
    "Congo – Inga Dam": 1,
    "Yangtze – Three Gorges Dam": 1,
    "Paraná – Itaipu Dam": 1,
    "Orinoco – Guri Dam": 1,
    "Columbia – Grand Coulee Dam": 1,
    "Murray-Darling – Hume Dam": 1,
    "Amazon – Belo Monte Dam": 1,
}

DARK = "#0d1117"
DARK2 = "#161b22"
BLUE = "#58a6f"
GREEN = "#3fb950"
ORG = "#f0883e"
RED = "#f85149"
GRAY = "#8b949e"
WHT = "#e6edf3"
BRD = "#30363d"
BRD2 = "#21262d"


class HSAEDashboardPanel(QDockWidget):
    """HSAE v6.01 Real-Time Dashboard Panel."""

    def __init__(self, iface, parent=None):
        super().__init__("🌊 HSAE v6.01 Dashboard", parent)
        self.iface = iface
        self.basins = self._load_basins()
        self.current = self.basins[0] if self.basins else {}
        self._build_ui()

    def _load_basins(self):
        bp = Path(__file__).parent / 'basins_50.json'
        try:
            return json.loads(bp.read_text())
        except Exception:
            return []

    def _compute(self, b):
        rc = float(b.get('runoff_c', 0.3))
        cap = float(b.get('cap', 10))
        nc = len(
            b.get(
                'country',
                ['?'])) if isinstance(
            b.get('country'),
            list) else 2
        area = float(b.get('eff_cat_km2', 100000))
        disp = DISP_LEVELS.get(
            b.get(
                'name', ''), int(
                b.get(
                    'dispute_level', 0)))
        atdi = min(95, max(5, 15 + disp * 12 + min(cap / 2, 20) + (nc - 2) * 8 + (1 - rc) * 10))
        hifd = min(80, max(5, 8 + min(cap / 3, 15) + (1 - rc) * 12 + disp * 5 + (nc - 2) * 3))
        nse = round(min(0.89, max(0.38, 0.55 + rc * 0.38 - min(0.18, area / 4e6) - disp * 0.04 - (nc - 2) * 0.025)), 2)
        kge = round(min(0.93, max(0.45, nse + 0.05 + rc * 0.06)), 2)
        pneg = round(max(0.2, min(0.9, 0.7 - atdi / 300 - hifd / 200)), 2)
        ci = round(0.4 * atdi / 100 + 0.25 * (disp / 4) + 0.2 * hifd / 100 + 0.1 * (nc - 2) * 0.15, 3)
        wqi = round(max(30, min(90, 70 - atdi * 0.3 - hifd * 0.2)), 1)
        p_mm = round(rc * 3.5 + cap / 30, 2)
        tws = round(cap * 0.3, 1)
        dlvl = ['LOW', 'LOW', 'MEDIUM', 'HIGH',
                'CRITICAL', 'CRITICAL'][min(disp, 5)]
        arts = ['Art.5 ERU', 'Art.9 Data']
        if atdi >= 40:
            arts.append('Art.7 NSH')
        if atdi >= 55:
            arts.append('Art.33 Dispute')
        if hifd >= 25:
            arts.append('Art.20 EnvFlow')
        risk_col = RED if atdi >= 70 else ORG if atdi >= 55 else "#e3b341" if atdi >= 40 else GREEN
        risk_txt = ("🔴 CRITICAL" if atdi >= 70 else "🟠 HIGH" if atdi >= 55
                    else "🟡 MODERATE" if atdi >= 40 else "🟢 LOW")
        return dict(atdi=atdi, hifd=hifd, nse=nse, kge=kge, pneg=pneg, ci=ci,
                    wqi=wqi, p_mm=p_mm, tws=tws, dlvl=dlvl, arts=arts,
                    risk_col=risk_col, risk_txt=risk_txt, nc=nc,
                    cap=cap, area=area, rc=rc, disp=disp)

    def _lbl(self, text, style=""):
        lbl = QLabel(text)
        lbl.setStyleSheet(style)
        return lbl

    def _frame(self, border_col=BRD):
        f = QFrame()
        f.setStyleSheet(f"background:{DARK};border:1px solid {border_col};"
                        "border-radius:4px;padding:3px")
        return f

    def _build_ui(self):
        w = QWidget()
        w.setStyleSheet(f"background:{DARK2};color:{WHT}")
        ml = QVBoxLayout(w)
        ml.setContentsMargins(8, 8, 8, 8)
        ml.setSpacing(5)

        # Header
        ml.addWidget(
            self._lbl(
                "🌊 HydroSovereign AI Engine v6.01",
                f"color:{BLUE};font-weight:bold;font-size:13px"))
        ml.addWidget(
            self._lbl(
                "Seifeldin M.G. Alkhedir · ORCID: 0000-0003-0821-2991",
                f"color:{GRAY};font-size:9px"))

        # Basin selector
        hl = QHBoxLayout()
        hl.addWidget(self._lbl("Basin:", f"color:{WHT};font-size:11px"))
        self.combo = QComboBox()
        self.combo.setStyleSheet(
            f"background:{DARK};color:{WHT};border:1px solid {BRD};padding:3px;font-size:11px")
        for b in self.basins:
            self.combo.addItem(b.get('name', ''))
        self.combo.currentIndexChanged.connect(self._on_change)
        hl.addWidget(self.combo, 1)
        ml.addLayout(hl)

        # Tabs
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane{{background:{DARK2};border:1px solid {BRD}}}
            QTabBar::tab{{background:{DARK};color:{GRAY};padding:4px 7px;font-size:10px}}
            QTabBar::tab:selected{{background:{DARK2};color:{BLUE}}}""")

        # Tab 1: Indices
        t1 = QWidget()
        g = QGridLayout(t1)
        g.setSpacing(4)
        self.vals = {}
        defs = [
            ("ATDI%", ORG), ("HIFD%", "#e3b341"),
            ("NSE", GREEN), ("KGE", BLUE),
            ("CI", RED), ("WQI", "#a78bfa"),
            ("P(Neg)", "#34d399"), ("Disp", GRAY),
        ]
        for i, (key, col) in enumerate(defs):
            r, c = divmod(i, 2)
            fr = self._frame(col + "44")
            fl = QVBoxLayout(fr)
            fl.setContentsMargins(4, 3, 4, 3)
            fl.addWidget(
                self._lbl(
                    key,
                    f"color:{col};font-size:9px;font-weight:bold"))
            v = self._lbl("—", f"color:{WHT};font-size:13px;font-weight:bold")
            fl.addWidget(v)
            g.addWidget(fr, r, c)
            self.vals[key] = v

        pb_f = QFrame()
        pb_l = QVBoxLayout(pb_f)
        pb_l.setContentsMargins(0, 4, 0, 0)
        self.bar_atdi = self._bar(ORG)
        self.bar_hifd = self._bar("#e3b341")
        for lab, bar in [("ATDI", self.bar_atdi), ("HIFD", self.bar_hifd)]:
            rl = QHBoxLayout()
            rl.addWidget(
                self._lbl(
                    f"{lab}:",
                    f"color:{GRAY};font-size:9px"),
                0)
            rl.addWidget(bar, 1)
            pb_l.addLayout(rl)
        g.addWidget(pb_f, 4, 0, 1, 2)
        tabs.addTab(t1, "📊 Indices")

        # Tab 2: Physical
        t2 = QWidget()
        g2 = QGridLayout(t2)
        g2.setSpacing(4)
        self.phys = {}
        pdefs = [("Area(k km²)", "🗺️"), ("Storage(BCM)", "🏗️"),
                 ("Runof", "💧"), ("Countries", "🌍"),
                 ("P̄(mm/d)", "🌧️"), ("TWS(cm)", "🛰️")]
        for i, (key, ico) in enumerate(pdefs):
            r, c = divmod(i, 2)
            fr = self._frame()
            fl = QVBoxLayout(fr)
            fl.setContentsMargins(4, 3, 4, 3)
            fl.addWidget(
                self._lbl(
                    f"{ico} {key}",
                    f"color:{GRAY};font-size:9px"))
            v = self._lbl("—", f"color:{WHT};font-size:12px;font-weight:bold")
            fl.addWidget(v)
            g2.addWidget(fr, r, c)
            self.phys[key] = v
        tabs.addTab(t2, "🏗️ Physical")

        # Tab 3: Legal
        t3 = QWidget()
        t3l = QVBoxLayout(t3)
        self.legal_txt = QTextEdit()
        self.legal_txt.setReadOnly(True)
        self.legal_txt.setStyleSheet(
            f"background:{DARK};color:{WHT};font-size:10px;border:none")
        t3l.addWidget(self.legal_txt)
        tabs.addTab(t3, "⚖️ Legal")

        ml.addWidget(tabs, 1)

        # Risk badge
        self.risk_lbl = self._lbl("Risk: —",
                                  f"color:{WHT};font-size:12px;font-weight:bold;"
                                  f"background:{DARK2};padding:5px;border-radius:4px")
        self.risk_lbl.setAlignment(Qt.AlignCenter)
        ml.addWidget(self.risk_lbl)

        # Buttons
        bl = QHBoxLayout()
        for txt, fn in [("📄 Report", self._report),
                        ("🗺️ WebGIS", self._webgis),
                        ("🚀 App", self._app)]:
            b = QPushButton(txt)
            b.setStyleSheet(
                "background:#238636;color:#fff;border:none;"
                "padding:5px;border-radius:3px;font-size:10px")
            b.clicked.connect(fn)
            bl.addWidget(b)
        ml.addLayout(bl)

        self.setWidget(w)
        self._update()

    def _bar(self, color):
        b = QProgressBar()
        b.setRange(0, 100)
        b.setFixedHeight(7)
        b.setTextVisible(False)
        b.setStyleSheet(
            f"QProgressBar{{background:{BRD2};border-radius:3px}}"
            f"QProgressBar::chunk{{background:{color};border-radius:3px}}")
        return b

    def _on_change(self, idx):
        if 0 <= idx < len(self.basins):
            self.current = self.basins[idx]
            self._update()

    def _update(self):
        b = self.current
        d = self._compute(b)
        self.vals["ATDI%"].setText(f"{d['atdi']:.1f}%")
        self.vals["HIFD%"].setText(f"{d['hifd']:.1f}%")
        self.vals["NSE"].setText(str(d['nse']))
        self.vals["KGE"].setText(str(d['kge']))
        self.vals["CI"].setText(f"{d['ci']:.3f}")
        self.vals["WQI"].setText(f"{d['wqi']:.0f}")
        self.vals["P(Neg)"].setText(f"{d['pneg']:.0%}")
        self.vals["Disp"].setText(d['dlvl'])
        self.bar_atdi.setValue(int(d['atdi']))
        self.bar_hifd.setValue(int(d['hifd']))
        self.phys["Area(k km²)"].setText(f"{d['area'] / 1000:.0f}k")
        self.phys["Storage(BCM)"].setText(f"{d['cap']:.0f}")
        self.phys["Runof"].setText(str(d['rc']))
        self.phys["Countries"].setText(str(d['nc']))
        self.phys["P̄(mm/d)"].setText(f"{d['p_mm']:.2f}")
        self.phys["TWS(cm)"].setText(f"{d['tws']:.1f}")
        clist = (
            ", ".join(
                b.get(
                    'country',
                    [])) if isinstance(
                b.get('country'),
                list) else str(
                    b.get(
                        'country',
                        '?')))
        self.legal_txt.setPlainText(
            f"Basin: {b.get('name', '')}\n"
            f"Countries ({d['nc']}): {clist}\n"
            f"Treaty: {b.get('treaty', '—')}\n"
            f"Articles: {b.get('legal_arts', '—')}\n\n"
            f"Triggered: {', '.join(d['arts'])}\n"
            f"Dispute: {d['dlvl']}\n"
            f"P(Negotiation): {d['pneg']:.0%}\n\n"
            f"Context:\n{b.get('context', '—')}")
        self.risk_lbl.setText(d['risk_txt'])
        self.risk_lbl.setStyleSheet(
            f"color:{d['risk_col']};font-size:12px;font-weight:bold;"
            f"background:{DARK2};padding:5px;border-radius:4px")

    def _report(self):
        b = self.current
        d = self._compute(b)
        path, _ = QFileDialog.getSaveFileName(
            None, "Export Report", f"HSAE_{
                b.get(
                    'name', '').replace(
                    ' ', '_').replace(
                    '/', '_')}", "Text (*.txt)")
        if not path:
            return
        from datetime import datetime
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"HSAE v6.01 — Basin Report\n{'=' * 50}\n")
            f.write(f"Basin:  {b.get('name', '')}\n")
            f.write(
                f"Date:   {
                    datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n")
            f.write(
                "Author: Seifeldin M.G. Alkhedir | ORCID: 0000-0003-0821-2991\n\n")
            f.write(f"ATDI={d['atdi']:.1f}% | HIFD={d['hifd']:.1f}% | "
                    f"NSE={d['nse']} | KGE={d['kge']} | CI={d['ci']:.3f}\n")
            f.write(f"Risk: {d['risk_txt']} | P(Neg)={d['pneg']:.0%}\n")
            f.write(f"Articles: {', '.join(d['arts'])}\n")

    def _webgis(self):
        import webbrowser
        webbrowser.open(
            "https://hydrosovereign-ai-engine-hsae-v601-6euz2zxcmerkzxgordmvxf.streamlit.app")

    def _app(self):
        import webbrowser
        webbrowser.open(
            "https://hydrosovereign-ai-engine-hsae-v601-6euz2zxcmerkzxgordmvxf.streamlit.app")
