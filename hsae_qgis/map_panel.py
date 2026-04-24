"""
HydroSovereign AI Engine v6.0.3 — Interactive Map Panel
========================================================
Embeds a Leaflet.js interactive map directly inside QGIS Desktop
using QWebEngineView. Shows all 26 basins with full ATDI/HIFD/CI
popups, risk colour-coding, and real-time updates.

Author: Seifeldin M.G. Alkedir · ORCID: 0000-0003-0821-2991
"""
from __future__ import annotations
import json
from typing import Optional

try:
    from qgis.PyQt.QtWidgets import QDockWidget, QWidget, QVBoxLayout, QLabel
    from qgis.PyQt.QtCore import Qt, QUrl
    from qgis.PyQt.QtWebEngineWidgets import QWebEngineView
    HAS_WEBENGINE = True
except ImportError:
    HAS_WEBENGINE = False

from qgis.core import QgsMessageLog, Qgis


def _atdi_colour(atdi: float) -> str:
    """Return hex colour for ATDI risk level."""
    if atdi < 20:   return "#16a34a"   # green  — compliant
    if atdi < 40:   return "#ca8a04"   # yellow — Art. 7
    if atdi < 55:   return "#ea580c"   # orange — Art. 9
    if atdi < 70:   return "#dc2626"   # red    — Art. 33
    return "#7c3aed"                    # purple — Art. 35


def _unwc_zone(atdi: float) -> str:
    if atdi < 20:   return "Compliant"
    if atdi < 40:   return "Art. 7 — Notify"
    if atdi < 55:   return "Art. 9 — Data Share"
    if atdi < 70:   return "Art. 33 — Dispute"
    return "Art. 35 — Emergency"


def _build_html(basins: list, selected_id: Optional[str] = None) -> str:
    """Build full Leaflet.js HTML for embedding in QWebEngineView."""

    markers_js = []
    for b in basins:
        bid    = b.get("id", "")
        name   = b.get("name", "Unknown")
        lat    = b.get("lat", 0)
        lon    = b.get("lon", 0)
        atdi   = round(float(b.get("atf_risk", b.get("tdi", 0.3) * 100)), 1)
        hifd   = round(atdi * 0.46, 1)
        ci_raw = 0.40 * (atdi / 100) + 0.25 * (b.get("dispute_level", 3) / 5) + 0.20 * (hifd / 100) + 0.15 * (b.get("n_countries", 3) / 6)
        ci     = round(ci_raw, 2)
        p_neg  = round(max(15, min(85, 95 - atdi * 0.8 - ci * 10)), 0)
        dam    = b.get("dam", "—")
        river  = b.get("river", "—")
        colour = _atdi_colour(atdi)
        zone   = _unwc_zone(atdi)
        n_c    = b.get("n_countries", 3)
        cap    = b.get("cap_bcm", 0)
        area   = b.get("area_km2", 0)
        c_up   = b.get("country_up", "—")
        arts   = ", ".join(b.get("legal_arts", [zone.split("—")[0].strip()]))
        is_sel = "true" if bid == selected_id else "false"

        popup_html = f"""
<div style='font-family:Arial,sans-serif;min-width:260px;max-width:320px'>
  <div style='background:linear-gradient(135deg,#061F4A,#0E6B6A);color:#fff;
              padding:10px 14px;border-radius:6px 6px 0 0;margin:-12px -12px 10px'>
    <div style='font-size:15px;font-weight:700'>🌊 {{name}}</div>
    <div style='font-size:11px;opacity:0.85'>{{dam}} · {{river}}</div>
  </div>
  <table style='width:100%;border-collapse:collapse;font-size:12px'>
    <tr style='background:#f4f6f9'>
      <td style='padding:5px 8px;font-weight:600;color:#0B3D8E'>ATDI</td>
      <td style='padding:5px 8px'><span style='background:{colour};color:#fff;
         padding:2px 8px;border-radius:12px;font-weight:700'>{{atdi}}%</span></td>
      <td style='padding:5px 8px;font-size:11px;color:#4A5568'>{{zone}}</td>
    </tr>
    <tr>
      <td style='padding:5px 8px;font-weight:600;color:#0B3D8E'>HIFD</td>
      <td style='padding:5px 8px'>{{hifd}}%</td>
      <td style='padding:5px 8px;font-size:11px;color:#4A5568'>Flow deficit</td>
    </tr>
    <tr style='background:#f4f6f9'>
      <td style='padding:5px 8px;font-weight:600;color:#0B3D8E'>CI</td>
      <td style='padding:5px 8px'>{{ci}}</td>
      <td style='padding:5px 8px;font-size:11px;color:#4A5568'>Conflict Index</td>
    </tr>
    <tr>
      <td style='padding:5px 8px;font-weight:600;color:#0B3D8E'>P(Neg.)</td>
      <td style='padding:5px 8px'>{{p_neg}}%</td>
      <td style='padding:5px 8px;font-size:11px;color:#4A5568'>Negotiation success</td>
    </tr>
    <tr style='background:#f4f6f9'>
      <td style='padding:5px 8px;font-weight:600;color:#0B3D8E'>Dam</td>
      <td colspan='2' style='padding:5px 8px'>{{dam}}</td>
    </tr>
    <tr>
      <td style='padding:5px 8px;font-weight:600;color:#0B3D8E'>Riparian</td>
      <td style='padding:5px 8px'>{{n_c}} states</td>
      <td style='padding:5px 8px;font-size:11px'>Cap: {{cap}} BCM</td>
    </tr>
    <tr style='background:#f4f6f9'>
      <td style='padding:5px 8px;font-weight:600;color:#0B3D8E'>UNWC</td>
      <td colspan='2' style='padding:5px 8px;font-size:11px'>{{arts}}</td>
    </tr>
  </table>
  <div style='margin-top:8px;padding:6px 8px;background:#EBF4FF;border-radius:4px;
              font-size:11px;color:#1A365D'>
    🔑 ID: <b>{{bid}}</b> · Upstream: <b>{{c_up}}</b>
  </div>
</div>""".format(name=name, dam=dam, river=river, atdi=atdi, zone=zone,
                  hifd=hifd, ci=ci, p_neg=p_neg, n_c=n_c, cap=cap,
                  area=area, c_up=c_up, arts=arts, bid=bid, colour=colour)

        radius = max(6, min(18, int(atdi / 5)))
        opacity = "0.95" if bid == selected_id else "0.82"

        markers_js.append(f"""
  L.circleMarker([{lat}, {lon}], {{
    radius: {radius},
    fillColor: "{colour}",
    color: "#FFFFFF",
    weight: {3 if bid == selected_id else 1.5},
    opacity: 1,
    fillOpacity: {opacity}
  }}).bindPopup({_json.dumps(popup_html)}, {{maxWidth: 340}})
    .bindTooltip("<b>{name}</b><br>ATDI {atdi}% · CI {ci}", 
      {{permanent: false, direction: "top"}})
    .addTo(map);""")

    markers_str = "
".join(markers_js)

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"/>
<title>HSAE v6.0.3 — Basin Risk Map</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  body,html{{margin:0;padding:0;background:#061F4A;font-family:Arial,sans-serif}}
  #map{{width:100%;height:calc(100vh - 52px)}}
  #header{{height:52px;background:linear-gradient(135deg,#061F4A 0%,#0E6B6A 100%);
           display:flex;align-items:center;padding:0 16px;gap:12px}}
  .htitle{{color:#fff;font-size:14px;font-weight:700}}
  .hsub{{color:rgba(255,255,255,0.7);font-size:11px}}
  .legend{{padding:10px 14px;background:rgba(255,255,255,0.95);
           border-radius:8px;box-shadow:0 2px 12px rgba(0,0,0,0.2);
           font-size:11px;line-height:1.8}}
  .legend h4{{margin:0 0 6px;font-size:12px;color:#061F4A}}
  .dot{{display:inline-block;width:12px;height:12px;
        border-radius:50%;margin-right:6px;vertical-align:middle}}
  .leaflet-popup-content-wrapper{{border-radius:8px;padding:0;overflow:hidden}}
  .leaflet-popup-content{{margin:12px}}
</style>
</head>
<body>
<div id="header">
  <span style="font-size:22px">🌊</span>
  <div>
    <div class="htitle">HydroSovereign AI Engine v6.0.3 — Basin Risk Map</div>
    <div class="hsub">26 Globally Contested Basins · ATDI · HIFD · UNWC 1997 · Plugin ID: 5040</div>
  </div>
</div>
<div id="map"></div>
<script>
var map = L.map('map', {{
  center: [20, 20],
  zoom: 2,
  minZoom: 2,
  maxZoom: 10
}});

L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
  attribution: '&copy; <a href="https://carto.com/">CARTO</a> · HSAE v6.0.3',
  subdomains: 'abcd',
  maxZoom: 19
}}).addTo(map);

{markers_str}

// Legend
var legend = L.control({{position: 'bottomright'}});
legend.onAdd = function(map) {{
  var div = L.DomUtil.create('div', 'legend');
  div.innerHTML = '<h4>ATDI Risk Level (UNWC 1997)</h4>' +
    '<span class="dot" style="background:#16a34a"></span>&lt;20% Compliant<br>' +
    '<span class="dot" style="background:#ca8a04"></span>20–40% Art. 7 Notify<br>' +
    '<span class="dot" style="background:#ea580c"></span>40–55% Art. 9 Data Share<br>' +
    '<span class="dot" style="background:#dc2626"></span>55–70% Art. 33 Dispute<br>' +
    '<span class="dot" style="background:#7c3aed"></span>&ge;70% Art. 35 Emergency<br>' +
    '<hr style="margin:6px 0;border-color:#CBD5E0"><span style="font-size:10px;color:#4A5568">' +
    'Circle size ∝ ATDI risk · Click for full analysis</span>';
  return div;
}};
legend.addTo(map);

// Attribution panel
var info = L.control({{position: 'bottomleft'}});
info.onAdd = function(map) {{
  var div = L.DomUtil.create('div', 'legend');
  div.innerHTML = '<b>HSAE v6.0.3</b> · Plugin ID: 5040<br>' +
    'DOI: <a href="https://doi.org/10.5281/zenodo.19180160" target="_blank">10.5281/zenodo.19180160</a><br>' +
    'ORCID: <a href="https://orcid.org/0000-0003-0821-2991" target="_blank">0000-0003-0821-2991</a>';
  return div;
}};
info.addTo(map);
</script>
</body>
</html>"""
    return html


class HSAEMapPanel(QDockWidget):
    """
    Dockable interactive Leaflet.js map panel for HSAE v6.0.3.
    Shows all 26 basins with ATDI/HIFD/CI popups inside QGIS Desktop.
    """

    TITLE = "🗺️ HSAE Basin Risk Map — Interactive"

    def __init__(self, iface, basins: list, parent=None):
        super().__init__(self.TITLE, parent)
        self.iface   = iface
        self.basins  = basins
        self.browser = None
        self.setObjectName("HSAEMapPanelV603")
        self.setAllowedAreas(
            Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea |
            Qt.TopDockWidgetArea  | Qt.BottomDockWidgetArea
        )
        self._build_widget()

    def _build_widget(self):
        container = QWidget()
        layout    = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        if not HAS_WEBENGINE:
            label = QLabel(
                "⚠️ QWebEngineView not available.\n"
                "Install PyQtWebEngine:\n"
                "  pip install PyQtWebEngine"
            )
            label.setStyleSheet("color:#dc2626;padding:20px;font-size:12px")
            label.setWordWrap(True)
            layout.addWidget(label)
        else:
            self.browser = QWebEngineView()
            self.browser.setMinimumHeight(400)
            layout.addWidget(self.browser)
            self._refresh()

        self.setWidget(container)

    def _refresh(self, selected_id: Optional[str] = None):
        """Rebuild and reload the Leaflet map."""
        if not self.browser:
            return
        html = _build_html(self.basins, selected_id)
        self.browser.setHtml(html, QUrl("about:blank"))
        QgsMessageLog.logMessage(
            f"HSAE Map Panel refreshed ({len(self.basins)} basins)",
            "HSAE", Qgis.Info
        )

    def highlight_basin(self, basin_id: str):
        """Highlight a specific basin (called from other tools)."""
        self._refresh(selected_id=basin_id)

    def update_basins(self, basins: list):
        """Update basins data and refresh map."""
        self.basins = basins
        self._refresh()
