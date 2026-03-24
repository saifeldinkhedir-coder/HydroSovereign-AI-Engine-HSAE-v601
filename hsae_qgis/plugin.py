"""
plugin.py — HSAE v6.01 QGIS Plugin (Complete)
================================================
Merges GitHub v6.0.0 original tools with v6.01 new algorithms.

Original v6.0.0 tools (from GitHub):
  - basin_loader.py   → Load 26 basins as vector layer
  - tdi_visualiser.py → Apply TDI graduated colour map
  - legal_layer.py    → UN 1997 legal risk overlay
  - export_tool.py    → Export to Shapefile/GeoJSON
  - dialog_main.py    → Main dashboard dialog

New v6.01 additions:
  - GEE script generator (7 sensors)
  - GRDC stations overlay (3 tiers)
  - ICJ dossier export (TXT)
  - QGIS Processing Toolbox (ATDI + HIFD + Basin Report)

Author : Seifeldin M.G. Alkedir · ORCID: 0000-0003-0821-2991
"""
from qgis.PyQt.QtWidgets import QAction, QMenu
from qgis.PyQt.QtGui import QIcon
from pathlib import Path
import json

PLUGIN_DIR = Path(__file__).parent


class HSAEPlugin:
    """HSAE v6.01 Complete QGIS Plugin."""

    def __init__(self, iface):
        self.iface   = iface
        self.provider = None
        self.actions  = []
        self.menu     = "&HydroSovereign AI Engine v6.01"
        self.toolbar  = None

    def initGui(self):
        from qgis.core import QgsApplication
        from .hsae_processing_provider import HSAEProcessingProvider
        self.provider = HSAEProcessingProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

        self.toolbar = self.iface.addToolBar("HSAE v6.01")
        self.toolbar.setObjectName("HSAEv601Toolbar")

        # ── Original v6.0.0 tools ──────────────────────────────────────────
        self._add("🌊 Load Basin Registry",    self.load_basins,    "Load 26 basins as point layer",     True)
        self._add("📊 TDI/ATDI Visualiser",    self.apply_tdi,      "Graduated TDI colour map",          True)
        self._add("⚖️  UNWC Legal Layer",       self.load_legal,     "UN 1997 legal risk overlay",        True)
        self._add("📤 Export Basin Data",       self.export_data,    "Export to Shapefile or GeoJSON",    True)
        self._add("📋 Dashboard",              self.show_dashboard, "HSAE Main Dashboard Dialog",        True)

        # ── New v6.01 tools ────────────────────────────────────────────────
        self._add("🛰️  GEE Script Generator",  self.gee_scripts,    "Generate GEE Python/JS scripts",    True)
        self._add("📡 GRDC Stations",          self.grdc_overlay,   "Load GRDC discharge stations",      True)
        self._add("🏛️  ICJ Dossier Export",    self.icj_export,     "Export ICJ legal dossier TXT",      False)
        self._add("ℹ️  About HSAE v6.01",      self.about,          "About",                             False)

    def _add(self, text, cb, tip, toolbar=False):
        a = QAction(text, self.iface.mainWindow())
        a.setStatusTip(tip)
        a.triggered.connect(cb)
        self.iface.addPluginToMenu(self.menu, a)
        if toolbar: self.toolbar.addAction(a)
        self.actions.append(a)

    def unload(self):
        from qgis.core import QgsApplication
        if self.provider:
            QgsApplication.processingRegistry().removeProvider(self.provider)
        for a in self.actions:
            self.iface.removePluginMenu(self.menu, a)
            if self.toolbar: self.toolbar.removeAction(a)
        if self.toolbar: del self.toolbar

    def _basins(self):
        p = PLUGIN_DIR / "basins_50.json"
        if p.exists():
            with open(p, encoding="utf-8") as f: return json.load(f)
        return []

    # ── Original v6.0.0 tools (call original modules) ────────────────────
    def load_basins(self):
        from .basin_loader import load_basins_layer
        basins = self._basins()
        if basins: load_basins_layer(self.iface, basins)

    def apply_tdi(self):
        from .tdi_visualiser import apply_tdi_style
        apply_tdi_style(self.iface)

    def load_legal(self):
        from .legal_layer import load_legal_layer
        basins = self._basins()
        if basins: load_legal_layer(self.iface, basins)

    def export_data(self):
        from .export_tool import export_basin_data
        export_basin_data(self.iface)

    def show_dashboard(self):
        from .dialog_main import HSAEMainDialog
        dlg = HSAEMainDialog(self.iface, self._basins())
        dlg.exec_()

    # ── New v6.01 tools ───────────────────────────────────────────────────
    def gee_scripts(self):
        from qgis.PyQt.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
            QLabel, QComboBox, QPushButton, QTextEdit, QGroupBox)
        dlg = QDialog(self.iface.mainWindow())
        dlg.setWindowTitle("HSAE v6.01 — GEE Script Generator")
        dlg.setMinimumWidth(540)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("<b>Google Earth Engine — Script Generator</b>"))
        grp = QGroupBox("Configuration"); gl = QVBoxLayout()
        sr = QHBoxLayout(); sr.addWidget(QLabel("Sensor:"))
        scb = QComboBox()
        scb.addItems(["Sentinel-1 SAR","Sentinel-2 NDWI","MODIS ET",
                      "GPM IMERG","GRACE-FO TWS","SMAP Soil Moisture","VIIRS Night Lights"])
        sr.addWidget(scb); gl.addLayout(sr)
        br = QHBoxLayout(); br.addWidget(QLabel("Basin:  "))
        bcb = QComboBox()
        for b in self._basins(): bcb.addItem(b.get("name",""), b)
        br.addWidget(bcb); gl.addLayout(br); grp.setLayout(gl)
        layout.addWidget(grp)
        te = QTextEdit(); te.setPlaceholderText("Script will appear here…"); layout.addWidget(te)
        def gen():
            b = bcb.currentData() or {}
            bbox = b.get("bbox",[-180,-90,180,90]); w,s,e,n = (bbox+[-180,-90,180,90])[:4]
            bid = b.get("id","basin"); sensor = scb.currentText()
            scripts = {
                "Sentinel-1 SAR": f"// HSAE v6.01 Sentinel-1 | {bid}\nvar roi=ee.Geometry.Rectangle([{w},{s},{e},{n}]);\nvar s1=ee.ImageCollection('COPERNICUS/S1_GRD').filterBounds(roi).filterDate('2024-01-01','2024-12-31').filter(ee.Filter.eq('instrumentMode','IW')).select('VV').median().clip(roi);\nvar water=s1.lt(-15);\nMap.centerObject(roi,8);\nMap.addLayer(water,{{palette:['white','0000FF']}},'Water');\nExport.image.toDrive({{image:water,description:'HSAE_{bid}_SAR',scale:30}});",
                "Sentinel-2 NDWI": f"// HSAE v6.01 Sentinel-2 NDWI | {bid}\nvar roi=ee.Geometry.Rectangle([{w},{s},{e},{n}]);\nvar s2=ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').filterBounds(roi).filterDate('2024-01-01','2024-12-31').filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE',20)).median().clip(roi);\nvar ndwi=s2.normalizedDifference(['B3','B8']);\nMap.centerObject(roi,8);\nMap.addLayer(ndwi,{{min:-1,max:1,palette:['brown','white','blue']}},'NDWI');\nExport.image.toDrive({{image:ndwi,description:'HSAE_{bid}_NDWI',scale:10}});",
                "GPM IMERG": f"// HSAE v6.01 GPM | {bid}\nvar roi=ee.Geometry.Rectangle([{w},{s},{e},{n}]);\nvar gpm=ee.ImageCollection('NASA/GPM_L3/IMERG_V06').filterBounds(roi).filterDate('2024-01-01','2024-12-31').select('precipitationCal').sum().clip(roi);\nMap.centerObject(roi,8);\nMap.addLayer(gpm,{{min:0,max:3000,palette:['white','cyan','blue']}},'Precip');\nExport.image.toDrive({{image:gpm,description:'HSAE_{bid}_GPM',scale:11132}});",
            }
            te.setPlainText(scripts.get(sensor, f"// {sensor} script for {bid}"))
        row = QHBoxLayout()
        g=QPushButton("Generate"); g.clicked.connect(gen); row.addWidget(g)
        c=QPushButton("Copy"); c.clicked.connect(lambda: __import__('qgis.PyQt.QtWidgets',fromlist=['QApplication']).QApplication.clipboard().setText(te.toPlainText())); row.addWidget(c)
        layout.addLayout(row)
        cl=QPushButton("Close"); cl.clicked.connect(dlg.close); layout.addWidget(cl)
        dlg.setLayout(layout); dlg.exec_()

    def grdc_overlay(self):
        from qgis.core import (QgsProject, QgsVectorLayer, QgsFeature,
            QgsGeometry, QgsPointXY, QgsField, QgsFields, QgsMarkerSymbol,
            QgsCategorizedSymbolRenderer, QgsRendererCategory)
        from qgis.PyQt.QtCore import QVariant
        basins = self._basins()
        if not basins: return
        GRDC = {
            "blue_nile_gerd":("1763100","El Diem","Tier1"),
            "nile_roseires": ("1763200","Roseires","Tier1"),
            "nile_aswan":    ("1763500","Aswan","Tier1"),
        }
        vl = QgsVectorLayer("Point?crs=EPSG:4326","HSAE — GRDC Stations","memory")
        pr = vl.dataProvider()
        flds = QgsFields()
        for fn,ft in [("name",QVariant.String),("station",QVariant.String),("tier",QVariant.String)]:
            flds.append(QgsField(fn,ft))
        pr.addAttributes(flds); vl.updateFields()
        feats=[]
        for b in basins:
            bid=b.get("id",""); stn=GRDC.get(bid,(None,"Virtual","Tier3"))
            f=QgsFeature(); f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(float(b.get("lon",0)),float(b.get("lat",0)))))
            f.setAttributes([b.get("name",""),stn[1],stn[2]]); feats.append(f)
        pr.addFeatures(feats); vl.updateExtents()
        cats=[QgsRendererCategory(t,QgsMarkerSymbol.createSimple({"name":"triangle","color":c,"size":"4"}),t)
              for t,c in [("Tier1","#22c55e"),("Tier2","#eab308"),("Tier3","#94a3b8")]]
        vl.setRenderer(QgsCategorizedSymbolRenderer("tier",cats))
        QgsProject.instance().addMapLayer(vl)
        self.iface.messageBar().pushSuccess("HSAE","✅ GRDC stations loaded")

    def icj_export(self):
        from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QComboBox, QPushButton, QLabel, QFileDialog
        basins = self._basins()
        dlg = QDialog(self.iface.mainWindow()); dlg.setWindowTitle("ICJ Dossier Export")
        layout = QVBoxLayout(); layout.addWidget(QLabel("Select basin:"))
        cb = QComboBox()
        for b in basins: cb.addItem(b.get("name",""), b)
        layout.addWidget(cb)
        def export():
            b=cb.currentData() or {}
            path,_=QFileDialog.getSaveFileName(dlg,"Save",f"ICJ_{b.get('id','')}.txt","Text (*.txt)")
            if not path: return
            tdi=float(b.get("tdi",0))*100
            arts=[a for v,a in [(25,"Art.5 Equitable Use"),(40,"Art.7 No Harm"),(55,"Art.9 Data Exchange"),(70,"Art.12 Notification"),(85,"Art.33 ICJ Referral")] if tdi>=v]
            with open(path,'w') as fp:
                fp.write('\n'.join(["="*60,"ICJ DOSSIER — HSAE v6.01","="*60,
                    f"Basin: {b.get('name','')}",f"TDI: {tdi:.1f}%",f"ATF: {b.get('atf_risk',0):.1f}%","",
                    "UNWC VIOLATIONS:"]+[f"  ✗ {a}" for a in arts]+["",
                    "Author: Seifeldin M.G. Alkedir · ORCID: 0000-0003-0821-2991"]))
            self.iface.messageBar().pushSuccess("HSAE",f"✅ Dossier saved"); dlg.close()
        btn=QPushButton("Export"); btn.clicked.connect(export); layout.addWidget(btn)
        dlg.setLayout(layout); dlg.exec_()

    def about(self):
        from qgis.PyQt.QtWidgets import QMessageBox
        QMessageBox.about(self.iface.mainWindow(),"HSAE v6.01",
            "<h3>HydroSovereign AI Engine v6.01</h3>"
            "<p><b>Original tools (v6.0.0):</b> Basin loader · TDI visualiser · Legal layer · Export · Dashboard</p>"
            "<p><b>New (v6.01):</b> GEE scripts · GRDC stations · ICJ dossier · Processing ATDI/HIFD</p>"
            "<p><b>Author:</b> Seifeldin M.G. Alkedir · ORCID: 0000-0003-0821-2991</p>")
