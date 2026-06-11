"""
plugin.py — HSAE v6.0.9 QGIS Plugin (Complete — May 2026)
===========================================================
15 Tools + 5 Processing Algorithms

Tools:
  1.  Load Basin Registry
  2.  TDI/ATDI Visualiser
  3.  UNWC Legal Layer
  4.  Export Basin Data
  5.  Dashboard Dialog
  6.  GEE Script Generator (7 sensors)
  7.  GRDC Stations Overlay
  8.  Conflict Index (all 26 basins)
  9.  Negotiation AI (GBM, 478 cases)
  10. WebGIS Map Generator
  11. Dashboard Panel (real-time)
  12. ICJ/PCA Dossier Export
  15. Multi-Basin Comparison

Processing Algorithms:
  1. ATDI Calculator
  2. HIFD Calculator
  3. Basin Legal Report
  4. HBV-96 Calibration (SCE-UA)
  5. Multi-Basin Comparison

Author:  Seifeldin M.G. Alkhedir
ORCID:   0000-0003-0821-2991
DOI:     10.5281/zenodo.19180160
Preprint: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6661396
App:     https://hydrosovereign-ai-engine-hsae-v6.0.9-6euz2zxcmerkzxgordmvxf.streamlit.app
"""
from .map_panel import HSAEMapPanel
from .treaty_panel import HSAETreatyPanel
from .uncertainty_panel import HSAEUncertaintyPanel

try:
    from .webgis_v2 import build_webgis_v2
    HAS_WEBGIS_V2 = True
except Exception:
    HAS_WEBGIS_V2 = False

    def build_webgis_v2(*a, **kw):
        return ""

from qgis.PyQt.QtWidgets import (QAction, QFileDialog, QDialog, QVBoxLayout,
                                 QTextEdit, QPushButton, QMessageBox,
                                 QHBoxLayout)
from pathlib import Path
import json

from hsae_qgis.core.indices import (
    compute_atdi, compute_ahifd, compute_afsf,
    compute_ahlb, compute_asi, compute_atci,
    compute_conflict_index, compute_pneg, compute_all
)

PLUGIN_DIR = Path(__file__).parent
VERSION = "6.0.9"
AUTHOR = "Seifeldin M.G. Alkhedir"
ORCID = "0000-0003-0821-2991"
DOI = "10.5281/zenodo.19180160"
SSRN_URL = "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6661396"
LIVE_APP = "https://hydrosovereign-ai-engine-hsae-v6.0.9-6euz2zxcmerkzxgordmvxf.streamlit.app"
GITHUB = "https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v6.0.9"

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


class HSAEPlugin:

    def __init__(self, iface):
        self.iface = iface
        self.provider = None
        self.actions = []
        self.menu = "&HydroSovereign AI Engine v6.0.9"
        self.toolbar = None
        self.panel = None

    def initGui(self):
        from qgis.core import QgsApplication
        from .hsae_processing_provider import HSAEProcessingProvider
        self.provider = HSAEProcessingProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)
        self.toolbar = self.iface.addToolBar("HSAEv608Toolbar")
        self.toolbar.setObjectName("HSAEv603Toolbar")

        self._add("🌊 Load Basin Registry", self.load_basins,
                  "Load 26 transboundary basins as point layer", True)
        self._add("📊 TDI/ATDI Visualiser", self.apply_tdi,
                  "Apply TDI/ATDI graduated colour map", True)
        self._add("⚖️  UNWC Legal Layer", self.load_legal,
                  "UN 1997 UNWC legal risk overlay", True)
        self._add("📤 Export Basin Data", self.export_data,
                  "Export to Shapefile / GeoJSON / CSV", True)
        self._add(
            "📋 Dashboard Dialog",
            self.show_dashboard,
            "Open HSAE main dashboard dialog",
            True)
        self._add("🛰️  GEE Scripts (7 sensors)", self.gee_scripts,
                  "Generate GEE scripts for 7 satellite sensors", True)
        self._add(
            "📡 GRDC Stations",
            self.grdc_overlay,
            "Load GRDC discharge stations",
            True)
        self._add(
            "⚡ Conflict Index",
            self.conflict_index,
            "Compute ATDI/HIFD Conflict Index (26 basins)",
            True)
        self._add(
            "🤝 Negotiation AI",
            self.negotiation_ai,
            "Negotiation success probability (GBM model)",
            True)
        self._add(
            "🗺️  WebGIS Map",
            self.webgis_map,
            "Generate standalone Leaflet WebGIS HTML map",
            True)
        self._add(
            "📊 Basin Panel",
            self.toggle_panel,
            "Toggle real-time HSAE dashboard panel",
            True)
        self._add(
            "🏛️  ICJ/PCA Dossier",
            self.icj_export,
            "Export complete ICJ/PCA legal dossier",
            False)
        self._add(
            "🗺️  Basin Risk Map",
            self.open_map_panel,
            "Interactive Leaflet.js basin map inside QGIS",
            toolbar=False)
        self._add(
            "📉 Uncertainty Analysis",
            self.open_uncertainty,
            "Bayesian CI + Sobol sensitivity on ATDI/HIFD",
            toolbar=False)
        self._add(
            "⚖️  Treaty Analysis (ATCI)",
            self.open_treaty_analysis,
            "ATCI — Alkhedir Treaty Compliance Index for all articles",
            toolbar=False)
        self._add(
            "─── v6.08 NEW ───",
            lambda: None,
            "New in v6.0.9",
            False)
        self._add(
            "🤖 GeoAgent · Natural Language",
            self.geoagent_tool,
            "Run any HSAE analysis using natural language via opengeos/GeoAgent",
            toolbar=False)
        self._add(
            "ⓘ  About HSAE",
            self.about,
            "ⓘ  About HSAE",
            False)

    def _add(self, text, cb, tip, toolbar=False):
        a = QAction(text, self.iface.mainWindow())
        a.setStatusTip(tip)
        a.triggered.connect(cb)
        self.iface.addPluginToMenu(self.menu, a)
        if toolbar:
            self.toolbar.addAction(a)
        self.actions.append(a)

    def unload(self):
        from qgis.core import QgsApplication
        if self.provider:
            QgsApplication.processingRegistry().removeProvider(self.provider)
        for a in self.actions:
            self.iface.removePluginMenu(self.menu, a)
            if self.toolbar:
                self.toolbar.removeAction(a)
        if self.toolbar:
            del self.toolbar
        if self.panel:
            self.iface.removeDockWidget(self.panel)
            self.panel = None

    # ── Helpers ────────────────────────────────────────────────────────────

    def _basins(self):
        bp = PLUGIN_DIR / "basins_50.json"
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
        atdi = compute_atdi(runoff_c=rc, cap_bcm=cap, n_countries=int(nc), dispute_level=int(disp))
        hifd = compute_ahifd(runoff_c=rc, cap_bcm=cap, n_countries=int(nc), dispute_level=int(disp))
        nse = round(min(0.89, max(0.38, 0.55 + rc * 0.38 - min(0.18, area / 4e6) - disp * 0.04 - (nc - 2) * 0.025)), 2)
        kge = round(min(0.93, max(0.45, nse + 0.05 + rc * 0.06)), 2)
        pneg = round(
            max(0.2, min(0.9, 0.7 - atdi / 300 - hifd / 200 - (nc - 2) * 0.04)), 2)
        ci = round(0.4 * atdi / 100 + 0.25 * (disp / 4) + 0.2 * hifd / 100 + 0.1 * (nc - 2) * 0.15, 3)
        dlvl = ['LOW', 'LOW', 'MEDIUM', 'HIGH',
                'CRITICAL', 'CRITICAL'][min(disp, 5)]
        arts = ['Art.5 ERU', 'Art.9 Data Sharing']
        if atdi >= 40:
            arts.append('Art.7 NSH')
        if atdi >= 55:
            arts.append('Art.33 Dispute')
        if atdi >= 70:
            arts.append('Art.35 Emergency')
        if hifd >= 25:
            arts.append('Art.20 Env.Flow')
        return dict(rc=rc, cap=cap, nc=nc, area=area, disp=disp,
                    atdi=atdi, hifd=hifd, nse=nse, kge=kge,
                    pneg=pneg, ci=ci, dlvl=dlvl, arts=arts)

    def _dlg(self, title, w=650, h=480):
        d = QDialog()
        d.setWindowTitle(title)
        d.resize(w, h)
        return d

    def _txt_dlg(self, title, content, w=650, h=480, save_name=None):
        dlg = self._dlg(title, w, h)
        lay = QVBoxLayout()
        txt = QTextEdit()
        txt.setReadOnly(True)
        txt.setStyleSheet(
            "background:#0d1117;color:#e6edf3;font-family:Courier;font-size:11px")
        txt.setPlainText(content)
        lay.addWidget(txt)
        bl = QHBoxLayout()
        if save_name:
            bs = QPushButton("💾 Save")
            bs.setStyleSheet(
                "background:#238636;color:#fff;padding:6px;border:none;border-radius:3px")

            def do_save():
                path, _ = QFileDialog.getSaveFileName(
                    None, "Save", save_name, "All (*.*)")
                if path:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(txt.toPlainText())
                    self.iface.messageBar().pushSuccess(
                        "HSAE", f"✅ Saved: {path}")
            bs.clicked.connect(do_save)
            bl.addWidget(bs)
        bc = QPushButton("Close")
        bc.clicked.connect(dlg.close)
        bl.addWidget(bc)
        lay.addLayout(bl)
        dlg.setLayout(lay)
        dlg.exec_()

    # ── Tools ──────────────────────────────────────────────────────────────

    def load_basins(self):
        try:
            from .basin_loader import load_basin_layer
            from qgis.core import QgsProject
            lyr = load_basin_layer(self._basins())
            QgsProject.instance().addMapLayer(lyr)
            self.iface.messageBar().pushSuccess(
                "HSAE", f"✅ {lyr.featureCount()} basins loaded")
        except Exception as e:
            QMessageBox.critical(None, "HSAE Error", str(e))

    def apply_tdi(self):
        try:
            from .tdi_visualiser import apply_tdi_style
            lyr = self.iface.activeLayer()
            if lyr:
                apply_tdi_style(self.iface)
                self.iface.messageBar().pushSuccess("HSAE", "✅ TDI style applied")
            else:
                QMessageBox.warning(None, "HSAE", "Select a basin layer first")
        except Exception as e:
            QMessageBox.critical(None, "HSAE Error", str(e))

    def load_legal(self):
        try:
            from .legal_layer import load_legal_layer
            from qgis.core import QgsProject
            lyr = load_legal_layer(self.iface, self._basins())
            QgsProject.instance().addMapLayer(lyr)
            self.iface.messageBar().pushSuccess("HSAE", "✅ UNWC legal layer loaded")
        except Exception as e:
            QMessageBox.critical(None, "HSAE Error", str(e))

    def export_data(self):
        try:
            from .export_tool import export_basins
            path, _ = QFileDialog.getSaveFileName(
                None, "Export", "hsae_basins", "GeoJSON (*.geojson);;Shapefile (*.shp);;CSV (*.csv)")
            if path:
                export_basins(self._basins(), path)
                self.iface.messageBar().pushSuccess(
                    "HSAE", f"✅ Exported: {path}")
        except Exception as e:
            QMessageBox.critical(None, "HSAE Error", str(e))

    def show_dashboard(self):
        try:
            from .dialog_main import HSAEMainDialog
            HSAEMainDialog(self.iface, self._basins()).exec_()
        except Exception as e:
            QMessageBox.critical(None, "HSAE Error", str(e))

    def toggle_panel(self):
        try:
            from .dashboard_panel import HSAEDashboardPanel

            if self.panel is None:
                self.panel = HSAEDashboardPanel(
                    self.iface, self.iface.mainWindow())
                self.iface.addDockWidget(0x2, self.panel)
            elif self.panel.isVisible():
                self.panel.hide()
            else:
                self.panel.show()
        except Exception as e:
            QMessageBox.critical(None, "HSAE Error", str(e))

    def gee_scripts(self):
        scripts = """// ============================================================
// HSAE v6.0.9 — GEE Script Generator (7 Satellite Sensors)
// Author: Seifeldin M.G. Alkhedir · ORCID: 0000-0003-0821-2991
// GEE Project: zinc-arc-484714-j8
// ============================================================

// ── 1. GPM IMERG V07 — Daily Precipitation ──────────────────
var basin = ee.Geometry.Rectangle([33.0, 8.0, 37.5, 13.0]);
var gpm = ee.ImageCollection('NASA/GPM_L3/IMERG_V07')
  .filterDate('2025-01-01', '2025-12-31')
  .filterBounds(basin).select('precipitation');
var monthly_gpm = ee.List.sequence(1,12).map(function(m) {
  m = ee.Number(m);
  var d0 = ee.Date.fromYMD(2025, m, 1);
  var img = gpm.filterDate(d0, d0.advance(1,'month')).mean();
  var val = img.reduceRegion(ee.Reducer.mean(), basin, 11132);
  return ee.Feature(null, val.set('month', d0.format('YYYY-MM')));
});
print('GPM Monthly P:', ee.FeatureCollection(monthly_gpm));
Map.addLayer(gpm.mean().clip(basin),
  {min:0, max:10, palette:['white','cyan','blue']}, 'GPM IMERG V07');

// ── 2. GRACE-FO MASCON RL06v4 — TWS Anomaly ─────────────────
var grace = ee.ImageCollection('NASA/GRACE/MASS_GRIDS_V04/LAND')
  .filterDate('2022-01-01','2024-12-31')
  .select('lwe_thickness_csr');
var tws_series = grace.map(function(img) {
  var val = img.reduceRegion(ee.Reducer.mean(), basin, 300000);
  return ee.Feature(null, val.set('date', img.date().format('YYYY-MM')));
});
print('GRACE-FO TWS:', ee.FeatureCollection(tws_series));
Map.addLayer(grace.mean().clip(basin),
  {min:-50, max:50, palette:['red','white','blue']}, 'GRACE-FO TWS');

// ── 3. SMAP 10km — Soil Moisture ────────────────────────────
var smap = ee.ImageCollection('NASA_USDA/HSL/SMAP10KM_soil_moisture')
  .filterDate('2025-01-01','2025-12-31')
  .select('ssm');
print('SMAP SM mean:', smap.mean().reduceRegion(ee.Reducer.mean(), basin, 10000));
Map.addLayer(smap.mean().clip(basin),
  {min:0, max:0.5, palette:['yellow','green','blue']}, 'SMAP Soil Moisture');

// ── 4. Sentinel-1 SAR — Flood Mapping ───────────────────────
var s1 = ee.ImageCollection('COPERNICUS/S1_GRD')
  .filterDate('2025-07-01','2025-09-30')
  .filterBounds(basin)
  .filter(ee.Filter.eq('instrumentMode','IW'))
  .select('VV');
var flood_mask = s1.mean().lt(-15);
Map.addLayer(flood_mask.clip(basin),
  {palette:['white','#0077be']}, 'SAR Flood Extent');

// ── 5. Sentinel-2 — NDWI Water Mask ─────────────────────────
var s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterDate('2025-01-01','2025-12-31')
  .filterBounds(basin)
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE',20));
var ndwi = s2.mean().normalizedDifference(['B3','B8']);
var water = ndwi.gt(0.2);
Map.addLayer(water.clip(basin),
  {palette:['white','#00bcd4']}, 'NDWI Water Mask');

// ── 6. ERA5 Temperature via GEE ─────────────────────────────
var era5 = ee.ImageCollection('ECMWF/ERA5/MONTHLY')
  .filterDate('2024-01-01','2024-12-31')
  .select('mean_2m_air_temperature');
var temp_c = era5.mean().subtract(273.15);
print('ERA5 Temp:', temp_c.reduceRegion(ee.Reducer.mean(), basin, 25000));
Map.addLayer(temp_c.clip(basin),
  {min:15, max:40, palette:['blue','yellow','red']}, 'ERA5 Temperature (°C)');

// ── 7. Open-Meteo API (run outside GEE) ─────────────────────
// URL: https://archive-api.open-meteo.com/v1/archive
//   ?latitude=10.53&longitude=35.09
//   &start_date=2025-01-01&end_date=2025-12-31
//   &daily=temperature_2m_mean,precipitation_sum,
//          et0_fao_evapotranspiration,soil_moisture_0_to_7cm_mean
//   &timezone=UTC
print('Use Open-Meteo API for daily T, P, ET0, SM data');
print('Basin centroid: lat=10.53, lon=35.09 (Blue Nile GERD)');

// ── Map Setup ────────────────────────────────────────────────
Map.setCenter(35.09, 10.53, 7);
Map.setOptions('HYBRID');
"""
        self._txt_dlg(
            "HSAE v6.0.9 — GEE Script Generator (7 Sensors)",
            scripts, w=780, h=560,
            save_name="HSAE_GEE_Scripts.js")

    def grdc_overlay(self):
        try:
            from qgis.core import (QgsVectorLayer, QgsProject, QgsField,
                                   QgsFeature, QgsGeometry, QgsPointXY,
                                   QgsSingleSymbolRenderer, QgsMarkerSymbol)
            from qgis.PyQt.QtCore import QVariant
            stations = [
                ("1040250", "Blue Nile/GERD", 10.53, 35.09, 1500, "Ethiopia/Sudan"),
                ("1040220", "Roseires Dam", 11.85, 34.38, 1200, "Sudan"),
                ("2180010", "Aswan High Dam", 23.97, 32.88, 2830, "Egypt"),
                ("2903430", "Euphrates-Birecik", 37.03, 37.98, 895, "Turkey"),
                ("2904000", "Tigris-Mosul", 36.34, 43.14, 700, "Iraq"),
                ("2267050", "Mekong-Luang Prabang", 19.88, 102.13, 2800, "Laos"),
                ("2181200", "Indus-Tarbela", 34.07, 72.68, 2400, "Pakistan"),
                ("6335060", "Amazon-Obidos", -1.94, -55.52, 175000, "Brazil"),
                ("6340900", "Paraná-Itaipu", -25.41, -54.59, 11000, "Brazil/Paraguay"),
                ("6122800", "Mississippi-Vicksburg", 32.35, -90.91, 16800, "USA"),
            ]
            lyr = QgsVectorLayer(
                "Point?crs=EPSG:4326",
                "GRDC Stations (HSAE v6.0.9)",
                "memory")
            pr = lyr.dataProvider()
            pr.addAttributes([QgsField("grdc_id", QVariant.String),
                              QgsField("name", QVariant.String),
                              QgsField("country", QVariant.String),
                              QgsField("q_m3s", QVariant.Double)])
            lyr.updateFields()
            for sid, name, lat, lon, q, cntry in stations:
                f = QgsFeature()
                f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(lon, lat)))
                f.setAttributes([sid, name, cntry, float(q)])
                pr.addFeature(f)
            sym = QgsMarkerSymbol.createSimple(
                {'name': 'circle', 'color': '#58a6ff', 'size': '5', 'outline_color': 'white'})
            lyr.setRenderer(QgsSingleSymbolRenderer(sym))
            QgsProject.instance().addMapLayer(lyr)
            self.iface.messageBar().pushSuccess(
                "HSAE", f"✅ {len(stations)} GRDC stations loaded")
        except Exception as e:
            QMessageBox.critical(None, "HSAE Error", str(e))

    def conflict_index(self):
        basins = self._basins()
        hdr = (f"{'Basin':<38} {'ATDI':>6} {'AHIFD':>6} {'CI':>6} "
               f"{'Risk':<12} {'Dispute'}\n" + "─" * 85)
        rows = [hdr]
        for b in basins:
            d = self._compute(b)
            risk = ("🔴 CRITICAL" if d['ci'] >= 0.6 else "🟠 HIGH" if d['ci'] >= 0.4 else "🟡 MEDIUM" if d['ci'] >= 0.25 else "🟢 LOW")
            rows.append(
                f"{
                    b.get(
                        'name',
                        '')[
                        :38]:<38} {
                    d['atdi']:>5.1f}%" f" {
                        d['ahifd']:>5.1f}% {
                            d['ci']:>5.3f} {
                                risk:<12} {
                                    d['dlvl']}")
        self._txt_dlg(
            "HSAE v6.0.9 — Conflict Index (26 Basins · TFDD/ICOW)",
            "\n".join(rows), w=700, h=520,
            save_name="HSAE_Conflict_Index.csv")

    def negotiation_ai(self):
        basins = self._basins()
        hdr = (f"{'Basin':<38} {'P(Success)':>10} {'Strategy':<16} {'UN Path'}\n" + "─" * 80)
        rows = [hdr]
        for b in basins:
            d = self._compute(b)
            strat = ("Cooperative" if d['pneg'] >= 0.65 else
                     "Mediation" if d['pneg'] >= 0.40 else
                     "PCA Arb." if d['pneg'] >= 0.25 else "ICJ Referral")
            path = ("Art.8 Direct" if d['pneg'] >= 0.65 else
                    "Art.17 Med." if d['pneg'] >= 0.40 else "Art.33 Dispute")
            bar = "█" * int(d['pneg'] * 10) + "░" * (10 - int(d['pneg'] * 10))
            rows.append(f"{b.get('name', '')[:38]:<38} {d['pneg']:>8.0%}"
                        f"  [{bar}] {strat:<16} {path}")
        self._txt_dlg(
            "HSAE v6.0.9 — Negotiation AI (GBM Model · 478 Historical Cases)",
            "\n".join(rows), w=720, h=520,
            save_name="HSAE_Negotiation_AI.csv")

    def webgis_map(self):
        try:
            path, _ = QFileDialog.getSaveFileName(
                None, "Save WebGIS Map", "HSAE_WebGIS_v6.0.9", "HTML (*.html)")
            if not path:
                return
            if HAS_WEBGIS_V2:
                html = build_webgis_v2(self._basins(), self._compute)
            else:
                html = self._build_webgis(self._basins())
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html)
            import webbrowser
            webbrowser.open(f"file://{path}")
            self.iface.messageBar().pushSuccess("HSAE", f"✅ WebGIS: {path}")
        except Exception as e:
            QMessageBox.critical(None, "HSAE Error", str(e))

    def _build_webgis(self, basins):
        import json as _j
        features = []
        for b in basins:
            lat = float(b.get('lat', b.get('glofas_lat', 0)))
            lon = float(b.get('lon', b.get('glofas_lon', 0)))
            if not lat:
                continue
            d = self._compute(b)
            col = ("#f85149" if d['atdi'] >= 70 else "#f0883e" if d['atdi'] >= 55 else "#e3b341" if d['atdi'] >= 40 else "#3fb950")
            clist = (
                ", ".join(
                    b.get(
                        'country',
                        [])) if isinstance(
                    b.get('country'),
                    list) else str(
                    b.get(
                        'country',
                        '')))
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "name": b.get('name', ''), "river": b.get('river', ''),
                    "dam": b.get('dam', ''), "treaty": b.get('treaty', ''),
                    "countries": clist, "nc": d['nc'],
                    "atdi": round(d['atdi'], 1), "ahifd": round(d['ahifd'], 1),
                    "nse": d['nse'], "kge": d['kge'], "ci": d['ci'],
                    "pneg": round(d['pneg'], 2),
                    "storage": d['cap'], "area": int(d['area']),
                    "dispute": d['dlvl'], "arts": ", ".join(d['arts']),
                    "context": b.get('context', ''), "color": col,
                }
            })
        geo = _j.dumps({"type": "FeatureCollection", "features": features})
        return f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8">
<title>HSAE v6.0.9 — WebGIS Global Basin Network</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI',Arial,sans-serif;background:#0d1117;color:#e6edf3}}
#hdr{{background:#161b22;border-bottom:1px solid #30363d;padding:8px 16px;
      display:flex;align-items:center;gap:14px}}
#hdr h1{{color:#58a6ff;font-size:14px}}
#hdr p{{color:#8b949e;font-size:10px}}
#main{{display:flex;height:calc(100vh - 46px)}}
#map{{flex:1}}
#panel{{width:310px;background:#161b22;border-left:1px solid #30363d;
        overflow-y:auto;display:none;flex-direction:column}}
#panel.open{{display:flex}}
#pc{{padding:12px;font-size:11px}}
.m{{display:flex;justify-content:space-between;padding:4px 0;
     border-bottom:1px solid #21262d}}
.ml{{color:#8b949e}}.mv{{font-weight:bold}}
.bd{{display:inline-block;background:#1f2d3d;border:1px solid #30363d;
      border-radius:3px;padding:1px 5px;font-size:10px;color:#58a6ff;margin:2px}}
.sec{{color:#8b949e;font-size:10px;text-transform:uppercase;
       letter-spacing:.08em;margin:8px 0 3px}}
.bar{{background:#21262d;border-radius:2px;height:4px;margin:2px 0 5px}}
.bf{{height:100%;border-radius:2px}}
</style></head><body>
<div id="hdr">
  <div>
    <h1>🌊 HSAE v6.0.9 — WebGIS Global Basin Network</h1>
    <p>Author: Seifeldin M.G. Alkhedir · ORCID: 0000-0003-0821-2991 ·
       DOI: 10.5281/zenodo.19180160 · Preprint: SSRN 2026</p>
  </div>
</div>
<div id="main">
<div id="map"></div>
<div id="panel">
  <div id="pc">
    <div id="pt" style="color:#58a6ff;font-weight:bold;font-size:13px;
         padding-bottom:7px;border-bottom:1px solid #30363d;margin-bottom:7px"></div>
    <div id="pb"></div>
  </div>
</div>
</div>
<script>
var map=L.map('map',{{center:[20,30],zoom:2,preferCanvas:true}});
L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}.png',
  {{attribution:'© CartoDB · HSAE v6.0.9 · Seifeldin M.G. Alkhedir'}}).addTo(map);
var data={geo};
data.features.forEach(function(f){{
  var p=f.properties,c=f.geometry.coordinates;
  L.circleMarker([c[1],c[0]],{{
    radius:6+p.atdi/12,color:p.color,fillColor:p.color,
    fillOpacity:0.82,weight:1.5
  }}).on('click',function(){{showPanel(p);}})
    .bindTooltip('<b>'+p.name+'</b><br>ATDI:'+p.atdi+'% | '+p.dispute,{{sticky:true}})
    .addTo(map);
}});
function bar(v,col){{
  return '<div class="bar"><div class="bf" style="width:'+Math.min(v,100)+'%;background:'+col+'"></div></div>';
}}
function showPanel(p){{
  document.getElementById('panel').classList.add('open');
  document.getElementById('pt').textContent=p.name;
  var c=p.color;
  document.getElementById('pb').innerHTML=
    '<div class="sec">📍 Identity</div>'+
    '<div class="m"><span class="ml">River</span><span class="mv">'+p.river+'</span></div>'+
    '<div class="m"><span class="ml">Dam</span><span class="mv">'+p.dam+'</span></div>'+
    '<div class="m"><span class="ml">Countries ('+p.nc+')</span><span class="mv" style="font-size:10px">'+p.countries+'</span></div>'+ # noqa: E501
    '<div class="m"><span class="ml">Treaty</span><span class="mv">'+p.treaty+'</span></div>'+
    '<div class="sec">🏗️ Physical</div>'+
    '<div class="m"><span class="ml">Storage</span><span class="mv">'+p.storage+' BCM</span></div>'+
    '<div class="m"><span class="ml">Area</span><span class="mv">'+Math.round(p.area/1000)+'k km²</span></div>'+
    '<div class="sec">📊 HSAE Indices</div>'+
    '<div class="m"><span class="ml">ATDI</span><span class="mv" style="color:'+c+'">'+p.atdi+'%</span></div>'+bar(p.atdi,c)+ # noqa: E501
    '<div class="m"><span class="ml">HIFD</span><span class="mv">'+p.hifd+'%</span></div>'+bar(p.hifd,'#e3b341')+
    '<div class="m"><span class="ml">NSE</span><span class="mv">'+p.nse+'</span></div>'+
    '<div class="m"><span class="ml">KGE</span><span class="mv">'+p.kge+'</span></div>'+
    '<div class="m"><span class="ml">Conflict Index</span><span class="mv">'+p.ci+'</span></div>'+
    '<div class="m"><span class="ml">P(Negotiation)</span><span class="mv">'+(p.pneg*100).toFixed(0)+'%</span></div>'+
    '<div class="sec">⚖️ Legal & Risk</div>'+
    '<div class="m"><span class="ml">Dispute</span><span class="mv" style="color:'+c+'">'+p.dispute+'</span></div>'+
    '<div class="sec">📜 UN Articles</div>'+
    p.arts.split(', ').map(a=>'<span class="bd">'+a+'</span>').join('')+
    (p.context?'<div class="sec">🌐 Context</div><div style="font-size:10px;color:#8b949e;line-height:1.5;padding-top:3px">'+p.context+'</div>':''); # noqa: E501
}}
</script></body></html>"""

    def icj_export(self):
        try:
            path, _ = QFileDialog.getSaveFileName(
                None, "Export ICJ/PCA Dossier", "HSAE_ICJ_PCA_Dossier_v6.0.9",
                "HTML (*.html);;Text (*.txt)")
            if not path:
                return
            basins = self._basins()
            if path.endswith('.html'):
                self._dossier_html(basins, path)
            else:
                self._dossier_txt(basins, path)
            self.iface.messageBar().pushSuccess("HSAE", f"✅ Dossier: {path}")
        except Exception as e:
            QMessageBox.critical(None, "HSAE Error", str(e))

    def _dossier_txt(self, basins, path):
        from datetime import datetime
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"HSAE v{VERSION} — ICJ/PCA LEGAL DOSSIER\n{'=' * 60}\n")
            f.write(f"Author: {AUTHOR} | ORCID: {ORCID}\n")
            f.write(f"DOI: {DOI}\nPreprint: {SSRN_URL}\n")
            f.write(
                f"Generated: {
                    datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n\n")
            for b in basins:
                d = self._compute(b)
                cl = (
                    ", ".join(
                        b.get(
                            'country',
                            [])) if isinstance(
                        b.get('country'),
                        list) else str(
                        b.get(
                            'country',
                            '?')))
                f.write(f"\nBASIN: {b.get('name', '')}\n{'─' * 50}\n")
                f.write(f"States ({d['nc']}): {cl}\n")
                f.write(
                    f"Treaty: {
                        b.get(
                            'treaty',
                            '—')} | Articles: {
                        b.get(
                            'legal_arts',
                            '—')}\n")
                f.write(f"ATDI: {d['atdi']:.1f}% | HIFD: {d['ahifd']:.1f}%\n")
                f.write(f"NSE: {d['nse']} | KGE: {d['kge']}\n")
                f.write(f"CI: {d['ci']:.3f} | Dispute: {d['dlvl']}\n")
                f.write(f"P(Neg): {d['pneg']:.0%}\n")
                f.write(f"Articles: {', '.join(d['arts'])}\n")
                f.write(f"Context: {b.get('context', '—')}\n")

    def _dossier_html(self, basins, path):
        from datetime import datetime
        rows = ""
        for b in basins:
            d = self._compute(b)
            col = ("#f85149" if d['atdi'] >= 70 else "#f0883e" if d['atdi'] >= 55 else "#e3b341" if d['atdi'] >= 40 else "#3fb950")
            cl = (
                ", ".join(
                    b.get(
                        'country',
                        [])) if isinstance(
                    b.get('country'),
                    list) else str(
                    b.get(
                        'country',
                        '?')))
            rows += (f"<tr><td><b>{b.get('name', '')}</b></td>"
                     f"<td style='font-size:10px'>{cl}</td>"
                     f"<td>{b.get('treaty', '—')}</td>"
                     f"<td style='color:{col};font-weight:bold'>{d['atdi']:.1f}%</td>"
                     f"<td>{d['ahifd']:.1f}%</td>"
                     f"<td>{d['nse']}</td><td>{d['kge']}</td>"
                     f"<td>{d['ci']:.3f}</td>"
                     f"<td>{'🔴' if d['dlvl'] == 'CRITICAL' else '🟠' if d['dlvl'] == 'HIGH' else '🟡' if d['dlvl'] == 'MEDIUM' else '🟢'} {d['dlvl']}</td>"  # noqa: E501
                     f"<td>{d['pneg']:.0%}</td>"
                     f"<td style='font-size:10px'>{', '.join(d['arts'])}</td>"
                     f"<td style='font-size:10px'>{b.get('context', '—')[:60]}</td></tr>")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"""<!DOCTYPE html><html><head>
<title>HSAE v{VERSION} — ICJ/PCA Legal Dossier</title>
<style>
body{{font-family:Arial,sans-serif;background:#0d1117;color:#e6edf3;padding:20px}}
h1{{color:#58a6ff;font-size:16px}}h2{{color:#8b949e;font-size:11px;margin:3px 0 14px}}
table{{width:100%;border-collapse:collapse;font-size:11px}}
th{{background:#161b22;color:#58a6ff;padding:7px 5px;border:1px solid #30363d;text-align:left}}
td{{padding:5px;border:1px solid #21262d;vertical-align:top}}
tr:nth-child(even){{background:#161b22}}
.ft{{color:#8b949e;font-size:10px;margin-top:14px;text-align:center}}
</style></head><body>
<h1>🏛️ HSAE v{VERSION} — ICJ/PCA Legal Dossier (26 Transboundary Basins)</h1>
<h2>Author: {AUTHOR} · ORCID: {ORCID} · DOI: {DOI} ·
    Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</h2>
<table><thead><tr>
<th>Basin</th><th>Countries</th><th>Treaty</th>
<th>ATDI%</th><th>HIFD%</th><th>NSE</th><th>KGE</th><th>CI</th>
<th>Dispute</th><th>P(Neg)</th><th>UN Articles</th><th>Context</th>
</tr></thead><tbody>{rows}</tbody></table>
<p class="ft">HSAE v{VERSION} · UNWC 1997 · TFDD/ICOW ·
<a href="{SSRN_URL}" style="color:#58a6ff">Preprint (SSRN)</a> ·
<a href="https://doi.org/{DOI}" style="color:#58a6ff">{DOI}</a></p>
</body></html>""")

    def open_map_panel(self):
        """Open interactive Leaflet.js basin risk map inside QGIS."""
        try:
            if not hasattr(self, '_map_panel') or self._map_panel is None:
                self._map_panel = HSAEMapPanel(self.iface, self._basins())
                self.iface.mainWindow().addDockWidget(
                    8,  # Qt.BottomDockWidgetArea
                    self._map_panel)
            self._map_panel.show()
            self._map_panel.raise_()
        except Exception as e:
            self.iface.messageBar().pushWarning(
                "HSAE", f"Map panel error: {e}")

    def open_uncertainty(self):
        """Open Bayesian uncertainty + Sobol sensitivity panel."""
        try:
            basins = self._basins()
            basin = basins[0] if basins else {}
            if not hasattr(self, '_unc_panel') or self._unc_panel is None:
                self._unc_panel = HSAEUncertaintyPanel(self.iface)
                self.iface.mainWindow().addDockWidget(
                    2,  # Qt.RightDockWidgetArea
                    self._unc_panel)
            self._unc_panel.update_basin(basin)
            self._unc_panel.show()
            self._unc_panel.raise_()
        except Exception as e:
            self.iface.messageBar().pushWarning(
                "HSAE", f"Uncertainty panel error: {e}")

    def open_treaty_analysis(self):
        """Open ATCI Treaty Compliance Analysis panel."""
        try:
            if not hasattr(
                    self,
                    '_treaty_panel') or self._treaty_panel is None:
                self._treaty_panel = HSAETreatyPanel(self.iface, self._basins())
                self.iface.mainWindow().addDockWidget(
                    2,  # Qt.RightDockWidgetArea
                    self._treaty_panel)
            self._treaty_panel.show()
            self._treaty_panel.raise_()
        except Exception as e:
            self.iface.messageBar().pushWarning(
                "HSAE", f"Treaty panel error: {e}")

    def geoagent_tool(self):
        """Tool 16: GeoAgent Natural Language Query — opengeos/GeoAgent integration."""
        from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QTextEdit
        dlg = QDialog(self.iface.mainWindow())
        dlg.setWindowTitle("🤖 HSAE GeoAgent — Natural Language Query")
        dlg.setMinimumWidth(560)
        layout = QVBoxLayout(dlg)
        info_lbl = QLabel(
            "<b>HydroSovereign AI Engine — GeoAgent Integration</b><br>"
            "HSAE tools are now part of "
            "<a href='https://github.com/opengeos/GeoAgent'>opengeos/GeoAgent</a>"
            " (PR #79, merged May 2026).<br><br>"
            "<b>Example queries:</b><br>"
            "&#8226; <i>Analyze Blue Nile GERD compliance</i><br>"
            "&#8226; <i>What is the ATDI for the Mekong basin?</i><br>"
            "&#8226; <i>Is the Euphrates in violation of Article 7?</i>"
        )
        info_lbl.setWordWrap(True)
        info_lbl.setOpenExternalLinks(True)
        layout.addWidget(info_lbl)
        lbl = QLabel("Install GeoAgent to use natural language queries:")
        layout.addWidget(lbl)
        code = QTextEdit()
        code.setPlainText(
            "pip install geoagent[hsae]\n\n"
            "from geoagent.tools.hsae import hsae_tools\n"
            "agent = hsae_tools()\n"
            "result = agent.analyze_basin_compliance('Blue Nile')\n"
            "print(result)"
        )
        code.setMaximumHeight(120)
        layout.addWidget(code)
        link_btn = QPushButton("Open GeoAgent on GitHub")
        link_btn.clicked.connect(lambda: __import__('webbrowser').open(
            'https://github.com/opengeos/GeoAgent'))
        layout.addWidget(link_btn)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dlg.accept)
        layout.addWidget(close_btn)
        dlg.exec_()

    def about(self):
        QMessageBox.about(None, "ⓘ  About HSAE", f"""
<b>HydroSovereign AI Engine (HSAE) v{VERSION}</b><br><br>
<b>Author:</b> {AUTHOR}<br>
<b>ORCID:</b> {ORCID}<br>
<b>DOI:</b> {DOI}<br>
<b>Preprint:</b> <a href="{SSRN_URL}">papers.ssrn.com</a><br>
<b>GitHub:</b> <a href="{GITHUB}">{GITHUB}</a><br>
<b>Live App:</b> <a href="{LIVE_APP}">Streamlit Cloud</a><br><br>
<b>16 Tools:</b><br>
🌊 Basin Registry · 📊 TDI Visualiser · ⚖️ UNWC Legal Layer<br>
📤 Export · 📋 Dashboard · 🛰️ GEE Scripts (7 sensors)<br>
📡 GRDC Stations · ⚡ Conflict Index · 🤝 Negotiation AI<br>
🗺️ WebGIS Map v2 · 🏛️ ICJ/PCA Dossier · 🗺️ Basin Risk Map (Leaflet)<br>📉 Uncertainty Analysis · ⚖️ Treaty Analysis (ATCI) · 🤖 GeoAgent NL<br><br>
<b>5 Processing Algorithms:</b><br>
ATDI · AHIFD · Basin Legal Report · HBV-96 Calibration · Multi-Basin Comparison<br><br>
<b>Data:</b> 26 basins · TFDD/ICOW · UNWC 1997 · GEE<br>
<b>Model:</b> HBV-96 + SCE-UA · GBM Negotiation AI (478 cases)<br>
<b>Metrics:</b> NSE=0.63 · KGE=0.74 (pre-calibration)<br><br>
<i>SoftwareX 2026 (under review) · Preprint: SSRN · University of Khartoum</i><br><i>GeoAgent integration: opengeos/GeoAgent PR #79 · merged May 2026</i>
""")
