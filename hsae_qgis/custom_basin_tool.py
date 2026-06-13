"""
custom_basin_tool.py — HSAE v6.0.12
=====================================
Add Custom Basin — User-Defined Basin Analyser
Allows analysis of any basin worldwide without pre-loading.

User inputs:
  · Basin / Dam name
  · Latitude & Longitude
  · Dam storage capacity (BCM)
  · Number of riparian countries
  · Dispute intensity (1–4)
  · Runoff coefficient (optional, auto-estimated from lat/lon)

Outputs:
  · All 6 AWSI indices (ATDI, AHIFD, AFSF, AHLB, ASI, ATCI)
  · Conflict Index, P(Negotiation), Risk level
  · Triggered UNWC articles
  · Option to add result to QGIS vector layer
  · Option to add to basins registry for session

Author:  Seifeldin M.G. Alkhedir · ORCID: 0000-0003-0821-2991
Version: 6.0.12
"""
from __future__ import annotations
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QPushButton, QLineEdit, QSpinBox,
    QDoubleSpinBox, QComboBox, QTextEdit,
    QGroupBox, QMessageBox, QWidget,
    QTabWidget
)
from qgis.PyQt.QtCore import Qt, pyqtSignal
from hsae_qgis.core.indices import compute_all

try:
    from qgis.core import (
        QgsVectorLayer, QgsFeature, QgsGeometry,
        QgsPointXY, QgsField, QgsProject
    )
    from qgis.PyQt.QtCore import QVariant
    HAS_QGIS = True
except ImportError:
    HAS_QGIS = False


# ── Climate-zone runoff estimator ─────────────────────────
def _country_list(raw):
    """Parse comma-separated country names, fallback to ['Unknown']."""
    parts = [c.strip() for c in raw.split(",") if c.strip()]
    return parts if parts else ["Unknown"]


def estimate_runoff_c(lat: float, lon: float) -> float:
    """Estimate basin runoff coefficient from lat/lon.

    Uses a simplified Koppen-Geiger zone lookup.
    Ranges: 0.05 (hyper-arid) to 0.55 (boreal).

    Returns
    -------
    float — estimated runoff coefficient (0.05–0.55)
    """
    alat = abs(lat)

    # ── Tropical humid belt (ITCZ, Congo, Amazon, SE Asia) ──
    if alat < 10:
        # Very wet tropics — high rc
        return 0.48

    # ── Arid / semi-arid corridors ──────────────────────────
    # N Africa Sahara: stops at ~25°E (Nile valley/East Africa excluded)
    is_n_africa = (15 < alat < 30 and -15 < lon < 25)   # Sahara
    is_arabia = (10 < alat < 35 and 42 < lon < 65)    # Arabian Peninsula (east of Red Sea)
    is_c_asia = (35 < alat < 50 and 50 < lon < 85)    # Karakum / Kyzylkum
    is_aus_arid = (lat < -20 and 115 < lon < 142)        # Australian interior
    is_sw_usa = (28 < alat < 40 and -120 < lon < -100)  # Mojave / Great Basin
    is_atacama = (lat < -18 and -75 < lon < -65)        # Atacama

    if any([is_n_africa, is_arabia, is_c_asia,
            is_aus_arid, is_sw_usa, is_atacama]):
        return 0.15   # Arid / hyper-arid

    # ── Sub-tropical (Mediterranean, savanna) ───────────────
    if alat < 35:
        return 0.28

    # ── Temperate mid-latitudes ──────────────────────────────
    if alat < 50:
        # Wetter if western Europe / East Asia
        if (-10 < lon < 30) or (120 < lon < 145):
            return 0.42
        return 0.38

    # ── Cool temperate / sub-boreal ─────────────────────────
    if alat < 60:
        return 0.48

    # ── Boreal / polar ───────────────────────────────────────
    return 0.55


# ── Result display widget ─────────────────────────────────
class ResultWidget(QTextEdit):
    """Read-only rich-text result display."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setMinimumHeight(260)
        self.setStyleSheet("font-size:12px; background:#F8FAFB;")

    def show_result(self, name: str, lat: float, lon: float,
                    result: dict, rc: float) -> None:
        risk_color = {
            "CRITICAL": "#C0392B",
            "HIGH": "#E67E22",
            "MODERATE": "#F39C12",
            "LOW": "#27AE60",
        }.get(result["risk"], "#555")

        arts_html = " &nbsp;|&nbsp; ".join(result["articles"]) or "None triggered"

        html = f"""
        <h3 style='color:#003660;margin:4px 0'>
            🌊 {name}
        </h3>
        <p style='color:#555;margin:2px 0;font-size:11px'>
            Lat {lat:.4f}° &nbsp;|&nbsp; Lon {lon:.4f}°
            &nbsp;|&nbsp; Runoff c = {rc:.2f}
        </p>
        <hr style='border:1px solid #E2E8F0'>

        <table width='100%' cellspacing='4'>
        <tr>
          <td width='50%'>
            <b style='color:#C0392B'>ATDI</b>
            <span style='font-size:22px;color:#C0392B;font-weight:bold'>
              &nbsp;{result["atdi"]}%
            </span>
            <span style='font-size:10px;color:#777'>&nbsp;Art.7 threshold ≥40%</span>
          </td>
          <td width='50%'>
            <b style='color:#E67E22'>AHIFD</b>
            <span style='font-size:22px;color:#E67E22;font-weight:bold'>
              &nbsp;{result["ahifd"]}%
            </span>
            <span style='font-size:10px;color:#777'>&nbsp;flow deficit index</span>
          </td>
        </tr>
        <tr>
          <td><b>AFSF</b> &nbsp; {result["afsf"]}</td>
          <td><b>AHLB</b> &nbsp; {result["ahlb"]}</td>
        </tr>
        <tr>
          <td><b>ASI</b> &nbsp; {result["asi"]}</td>
          <td>
            <b>ATCI</b> &nbsp;
            <span style='font-size:16px;font-weight:bold;color:#00A3AD'>
              {result["atci"]}/100
            </span>
          </td>
        </tr>
        </table>
        <hr style='border:1px solid #E2E8F0'>

        <p>
          <b>CI</b> = {result["ci"]} &nbsp;&nbsp;
          <b>P(Neg)</b> = {result["pneg"]:.0%} &nbsp;&nbsp;
          <b style='color:{risk_color}'>Risk: {result["risk"]}</b>
        </p>
        <p style='font-size:11px;color:#555'>
          <b>NSE</b> ≈ {result["nse"]} &nbsp;|&nbsp;
          <b>KGE</b> ≈ {result["kge"]} &nbsp;
          <i>(pre-calibration estimates)</i>
        </p>
        <p style='font-size:11px;color:#003660'>
          <b>Triggered UNWC articles:</b> {arts_html}
        </p>
        """
        self.setHtml(html)


# ── Main Dialog ───────────────────────────────────────────
class CustomBasinDialog(QDialog):
    """Add Custom Basin — HSAE v6.0.12."""

    #: Emitted when a basin is added to the session registry
    basin_added = pyqtSignal(dict)

    # Dispute level labels
    DISP_LABELS = [
        "1 — Low (no active dispute)",
        "2 — Moderate (political tension)",
        "3 — High (negotiations stalled)",
        "4 — Critical (acute conflict)",
    ]

    def __init__(self, iface, session_basins: list, parent=None):
        super().__init__(parent or (iface.mainWindow() if iface else None))
        self.iface = iface
        self.session_basins = session_basins   # shared list from plugin
        self._last_result = None
        self._last_inputs = {}

        self.setWindowTitle("🌍  HSAE — Add Custom Basin")
        self.setMinimumWidth(620)
        self.setMinimumHeight(680)
        self._build_ui()

    # ── UI ────────────────────────────────────────────────
    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(8)

        # Header
        hdr = QLabel("🌍  Add Custom Basin — HSAE v6.0.12")
        hdr.setAlignment(Qt.AlignCenter)
        hdr.setStyleSheet(
            "font-size:15px;font-weight:bold;color:#003660;"
            "padding:6px;background:#F4F6F8;border-radius:4px")
        root.addWidget(hdr)

        sub = QLabel(
            "Analyse any transboundary basin worldwide using the 6 AWSI indices.")
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet("color:#4A5568;font-size:11px")
        root.addWidget(sub)

        tabs = QTabWidget()
        tabs.addTab(self._build_input_tab(), "  📥 Basin Input  ")
        tabs.addTab(self._build_help_tab(), "  ℹ️  Help  ")
        root.addWidget(tabs)

        # Result area
        res_box = QGroupBox("📊 AWSI Results")
        res_lay = QVBoxLayout(res_box)
        self._result_widget = ResultWidget()
        self._result_widget.setPlaceholderText(
            "Results will appear here after clicking  ▶ Analyse.")
        res_lay.addWidget(self._result_widget)
        root.addWidget(res_box)

        # Buttons row
        btn_row = QHBoxLayout()

        self._btn_analyse = QPushButton("▶  Analyse Basin")
        self._btn_analyse.setStyleSheet(
            "background:#00A3AD;color:white;font-weight:bold;"
            "padding:7px 20px;border-radius:5px;font-size:13px")
        self._btn_analyse.clicked.connect(self._on_analyse)
        btn_row.addWidget(self._btn_analyse)

        self._btn_add_layer = QPushButton("📌  Add to QGIS Layer")
        self._btn_add_layer.setEnabled(False)
        self._btn_add_layer.setStyleSheet(
            "background:#27AE60;color:white;font-weight:bold;"
            "padding:7px 16px;border-radius:5px")
        self._btn_add_layer.clicked.connect(self._on_add_layer)
        btn_row.addWidget(self._btn_add_layer)

        self._btn_add_registry = QPushButton("📋  Add to Session Registry")
        self._btn_add_registry.setEnabled(False)
        self._btn_add_registry.setStyleSheet(
            "background:#C89520;color:white;font-weight:bold;"
            "padding:7px 16px;border-radius:5px")
        self._btn_add_registry.clicked.connect(self._on_add_registry)
        btn_row.addWidget(self._btn_add_registry)

        btn_close = QPushButton("✖  Close")
        btn_close.setStyleSheet(
            "background:#C0392B;color:white;padding:7px 16px;border-radius:5px")
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)

        root.addLayout(btn_row)

    def _build_input_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setSpacing(10)

        # ── Basin identification ───────────────────────────
        id_box = QGroupBox("Basin / Dam Identification")
        id_form = QFormLayout(id_box)
        id_form.setLabelAlignment(Qt.AlignRight)

        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("e.g.  Euphrates — Atatürk Dam")
        id_form.addRow("Basin / Dam name *:", self._name_edit)

        coord_row = QHBoxLayout()
        self._lat_spin = QDoubleSpinBox()
        self._lat_spin.setRange(-90, 90)
        self._lat_spin.setDecimals(4)
        self._lat_spin.setSingleStep(0.1)
        self._lat_spin.setPrefix("Lat  ")
        self._lat_spin.valueChanged.connect(self._on_coord_changed)
        coord_row.addWidget(self._lat_spin)

        self._lon_spin = QDoubleSpinBox()
        self._lon_spin.setRange(-180, 180)
        self._lon_spin.setDecimals(4)
        self._lon_spin.setSingleStep(0.1)
        self._lon_spin.setPrefix("Lon  ")
        coord_row.addWidget(self._lon_spin)

        id_form.addRow("Coordinates *:", coord_row)
        lay.addWidget(id_box)

        # ── Hydrological parameters ─────────────────────────
        hy_box = QGroupBox("Hydrological Parameters")
        hy_form = QFormLayout(hy_box)
        hy_form.setLabelAlignment(Qt.AlignRight)

        self._cap_spin = QDoubleSpinBox()
        self._cap_spin.setRange(0.1, 1000.0)
        self._cap_spin.setDecimals(1)
        self._cap_spin.setSingleStep(1.0)
        self._cap_spin.setValue(10.0)
        self._cap_spin.setSuffix("  BCM")
        hy_form.addRow("Dam storage capacity *:", self._cap_spin)

        rc_row = QHBoxLayout()
        self._rc_spin = QDoubleSpinBox()
        self._rc_spin.setRange(0.05, 0.95)
        self._rc_spin.setDecimals(3)
        self._rc_spin.setSingleStep(0.01)
        self._rc_spin.setValue(0.35)
        rc_row.addWidget(self._rc_spin)

        self._rc_auto_btn = QPushButton("🌐 Auto-estimate from lat/lon")
        self._rc_auto_btn.setStyleSheet(
            "background:#E8F4F8;color:#003660;padding:3px 8px;border-radius:3px")
        self._rc_auto_btn.clicked.connect(self._auto_estimate_rc)
        rc_row.addWidget(self._rc_auto_btn)

        hy_form.addRow("Runoff coefficient (rc) *:", rc_row)
        lay.addWidget(hy_box)

        # ── Geopolitical parameters ─────────────────────────
        geo_box = QGroupBox("Geopolitical Parameters")
        geo_form = QFormLayout(geo_box)
        geo_form.setLabelAlignment(Qt.AlignRight)

        self._nc_spin = QSpinBox()
        self._nc_spin.setRange(2, 15)
        self._nc_spin.setValue(3)
        self._nc_spin.setSuffix("  countries")
        geo_form.addRow("Riparian country count *:", self._nc_spin)

        self._disp_combo = QComboBox()
        for label in self.DISP_LABELS:
            self._disp_combo.addItem(label)
        self._disp_combo.setCurrentIndex(1)
        geo_form.addRow("Dispute intensity *:", self._disp_combo)

        self._countries_edit = QLineEdit()
        self._countries_edit.setPlaceholderText(
            "e.g.  Turkey (upstream), Syria, Iraq (downstream)")
        geo_form.addRow("Country names (optional):", self._countries_edit)

        lay.addWidget(geo_box)

        # ── Note ────────────────────────────────────────────
        note = QLabel(
            "  * Required fields.  "
            "NSE / KGE are pre-calibration estimates — "
            "full SCE-UA calibration requires GRDC discharge data.")
        note.setWordWrap(True)
        note.setStyleSheet("color:#777;font-size:10px;padding:4px")
        lay.addWidget(note)
        lay.addStretch()
        return w

    def _build_help_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        txt = QTextEdit()
        txt.setReadOnly(True)
        txt.setHtml("""
        <h3 style='color:#003660'>How to use Add Custom Basin</h3>
        <ol>
        <li><b>Name:</b> Enter the basin or dam name.</li>
        <li><b>Coordinates:</b> Enter decimal lat/lon of the dam site
            (positive = N/E, negative = S/W).</li>
        <li><b>Capacity:</b> Dam storage in BCM (Billion Cubic Metres).
            Find this in the Global Dam Watch or GRanD database.</li>
        <li><b>Runoff coefficient:</b> The fraction of precipitation
            that becomes runoff (0.05–0.95). Click
            <i>Auto-estimate</i> for a climate-zone approximation.</li>
        <li><b>Countries:</b> Set the total number of riparian states
            sharing the basin.</li>
        <li><b>Dispute level:</b> 1 = cooperative, 4 = acute conflict.</li>
        <li>Click <b>▶ Analyse</b> to compute all 6 AWSI indices.</li>
        <li>Optionally <b>Add to QGIS Layer</b> or
            <b>Add to Session Registry</b>.</li>
        </ol>
        <h4>Data sources</h4>
        <ul>
        <li>Dam capacities: <a href='https://www.globaldamwatch.org'>
            Global Dam Watch</a> /
            <a href='https://sedac.ciesin.columbia.edu/data/set/grand-v1-dams-rev01'>
            GRanD v1</a></li>
        <li>Runoff coefficients: FAO AQUASTAT, HydroSHEDS</li>
        <li>Dispute levels: TFDD, ICOWater Project</li>
        </ul>
        <h4>AWSI Thresholds (UNWC 1997)</h4>
        <ul>
        <li><b>ATDI ≥ 40%</b> → Art. 7 No Significant Harm triggered</li>
        <li><b>AHIFD ≥ 25%</b> → Art. 9 Data Exchange obligation</li>
        <li><b>ASI &lt; 0.50</b> → Art. 5 Equitable Utilisation concern</li>
        <li><b>ATCI &lt; 60</b> → Arts. 5,7,9,11,17,33 composite concern</li>
        </ul>
        <p style='color:#777;font-size:11px'>
        Author: Seifeldin M.G. Alkhedir · ORCID: 0000-0003-0821-2991<br>
        DOI: 10.5281/zenodo.19180160</p>
        """)
        lay.addWidget(txt)
        return w

    # ── Slots ─────────────────────────────────────────────
    def _on_coord_changed(self) -> None:
        """Reset rc estimate hint when coords change."""
        pass  # could add live hint later

    def _auto_estimate_rc(self) -> None:
        """Estimate runoff coefficient from lat/lon."""
        lat = self._lat_spin.value()
        lon = self._lon_spin.value()
        rc = estimate_runoff_c(lat, lon)
        self._rc_spin.setValue(rc)
        QMessageBox.information(
            self,
            "Auto-Estimated Runoff Coefficient",
            f"Estimated rc = {rc:.3f} for\n"
            f"Lat {lat:.3f}°, Lon {lon:.3f}°\n\n"
            "Based on simplified Koppen-Geiger climate zones.\n"
            "Adjust manually if you have basin-specific data.")

    def _on_analyse(self) -> None:
        """Validate inputs and compute AWSI."""
        name = self._name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing Input",
                                "Please enter a Basin / Dam name.")
            return

        lat = self._lat_spin.value()
        lon = self._lon_spin.value()
        cap = self._cap_spin.value()
        rc = self._rc_spin.value()
        nc = self._nc_spin.value()
        disp = self._disp_combo.currentIndex() + 1  # 1-based

        # Compute all indices via central formula
        result = compute_all(
            runoff_c=rc,
            cap_bcm=cap,
            n_countries=nc,
            dispute_level=disp,
        )

        self._last_result = result
        self._last_inputs = {
            "name": name,
            "lat": lat,
            "lon": lon,
            "cap_bcm": cap,
            "runoff_c": rc,
            "n_countries": nc,
            "dispute_level": disp,
            "countries": self._countries_edit.text().strip(),
        }

        # Show results
        self._result_widget.show_result(name, lat, lon, result, rc)

        # Enable action buttons
        self._btn_add_layer.setEnabled(HAS_QGIS)
        self._btn_add_registry.setEnabled(True)

    def _on_add_layer(self) -> None:
        """Add basin as point to a QGIS memory vector layer."""
        if not self._last_result or not HAS_QGIS:
            return

        r = self._last_result
        inp = self._last_inputs

        # Create or reuse memory layer
        layer_name = "HSAE Custom Basins"
        existing = [
            lyr for lyr in QgsProject.instance().mapLayersByName(layer_name)
            if isinstance(lyr, QgsVectorLayer)
        ]

        if existing:
            layer = existing[0]
        else:
            layer = QgsVectorLayer(
                "Point?crs=EPSG:4326", layer_name, "memory")
            prov = layer.dataProvider()
            fields = [
                QgsField("name", QVariant.String),
                QgsField("lat", QVariant.Double),
                QgsField("lon", QVariant.Double),
                QgsField("cap_bcm", QVariant.Double),
                QgsField("runoff_c", QVariant.Double),
                QgsField("n_countries", QVariant.Int),
                QgsField("dispute_level", QVariant.Int),
                QgsField("atdi", QVariant.Double),
                QgsField("ahifd", QVariant.Double),
                QgsField("afsf", QVariant.Double),
                QgsField("ahlb", QVariant.Double),
                QgsField("asi", QVariant.Double),
                QgsField("atci", QVariant.Double),
                QgsField("ci", QVariant.Double),
                QgsField("pneg", QVariant.Double),
                QgsField("risk", QVariant.String),
                QgsField("articles", QVariant.String),
            ]
            prov.addAttributes(fields)
            layer.updateFields()
            QgsProject.instance().addMapLayer(layer)

        # Add feature
        feat = QgsFeature(layer.fields())
        feat.setGeometry(
            QgsGeometry.fromPointXY(
                QgsPointXY(inp["lon"], inp["lat"])))
        feat["name"] = inp["name"]
        feat["lat"] = inp["lat"]
        feat["lon"] = inp["lon"]
        feat["cap_bcm"] = inp["cap_bcm"]
        feat["runoff_c"] = inp["runoff_c"]
        feat["n_countries"] = inp["n_countries"]
        feat["dispute_level"] = inp["dispute_level"]
        feat["atdi"] = r["atdi"]
        feat["ahifd"] = r["ahifd"]
        feat["afsf"] = r["afsf"]
        feat["ahlb"] = r["ahlb"]
        feat["asi"] = r["asi"]
        feat["atci"] = r["atci"]
        feat["ci"] = r["ci"]
        feat["pneg"] = r["pneg"]
        feat["risk"] = r["risk"]
        feat["articles"] = ", ".join(r["articles"])

        layer.dataProvider().addFeature(feat)
        layer.updateExtents()
        layer.triggerRepaint()

        QMessageBox.information(
            self, "Added to QGIS Layer",
            f"✅  '{inp['name']}' added to layer\n"
            f"    '{layer_name}'\n\n"
            f"    ATDI = {r['atdi']}%  ·  Risk = {r['risk']}")

    def _on_add_registry(self) -> None:
        """Add basin to the session registry (used by other tools)."""
        if not self._last_result:
            return

        r = self._last_result
        inp = self._last_inputs

        # Build basin dict compatible with basins_50.json schema
        basin_dict = {
            "name": inp["name"],
            "lat": inp["lat"],
            "lon": inp["lon"],
            "cap_bcm": inp["cap_bcm"],
            "cap": inp["cap_bcm"],   # alias
            "runoff_c": inp["runoff_c"],
            "n_countries": inp["n_countries"],
            "dispute_level": inp["dispute_level"],
            "continent": "Custom",
            "region": "User-defined",
            "country": _country_list(inp["countries"]),
            # Pre-computed for quick access
            "_atdi": r["atdi"],
            "_ahifd": r["ahifd"],
            "_atci": r["atci"],
            "_risk": r["risk"],
            "_custom": True,
        }

        self.session_basins.append(basin_dict)
        self.basin_added.emit(basin_dict)

        QMessageBox.information(
            self, "Added to Session Registry",
            f"✅  '{inp['name']}' added to the session basin registry.\n\n"
            f"It will appear in all HSAE tools during this QGIS session.\n"
            f"ATDI = {r['atdi']}%  ·  AHIFD = {r['ahifd']}%  ·  "
            f"Risk = {r['risk']}")
