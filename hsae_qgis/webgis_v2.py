"""
HSAE v6.0.8 -- WebGIS Map v2 (v6.0.8)
Professional interactive map with Search, Layer Toggle,
Basemap Switcher, Risk Filter, Chart Popups, and Export PNG.
"""
from __future__ import annotations
import json as _json


def build_webgis_v2(basins: list, compute_fn) -> str:
    """Build complete WebGIS HTML v2 with all professional features."""

    features = []
    for b in basins:
        lat = float(b.get('lat', b.get('glofas_lat', 0)))
        lon = float(b.get('lon', b.get('glofas_lon', 0)))
        if not lat:
            continue
        d = compute_fn(b)
        atdi = round(d.get('atdi', 0), 1)
        hifd = round(d.get('ahifd', 0), 1)
        ci = round(d.get('ci', 0), 3)
        pneg = round(d.get('pneg', 0), 1)
        nse = d.get('nse', 0)
        kge = d.get('kge', 0)
        nc = d.get('nc', 2)
        dlvl = d.get('dlvl', 'LOW')

        # ATCI computation
        atci = _compute_atci(atdi, hifd)

        # UNWC zone
        if atdi < 20:
            zone = 'Compliant'
        elif atdi < 40:
            zone = 'Art. 7 NSH'
        elif atdi < 55:
            zone = 'Art. 9 Data Share'
        elif atdi < 70:
            zone = 'Art. 33 Dispute'
        else:
            zone = 'Art. 35 Emergency'

        # colour
        if atdi < 20:
            col = '#16a34a'
        elif atdi < 40:
            col = '#ca8a04'
        elif atdi < 55:
            col = '#ea580c'
        elif atdi < 70:
            col = '#dc2626'
        else:
            col = '#7c3aed'

        clist = ', '.join(b.get('country', [])) if isinstance(
            b.get('country'), list) else str(b.get('country', ''))

        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
            "properties": {
                "name": b.get('name', ''),
                "river": b.get('river', ''),
                "dam": b.get('dam', ''),
                "treaty": b.get('treaty', ''),
                "countries": clist,
                "nc": nc,
                "atdi": atdi,
                "ahifd": hifd,
                "ci": ci,
                "pneg": pneg,
                "nse": nse,
                "kge": kge,
                "atci": atci,
                "dlvl": dlvl,
                "zone": zone,
                "colour": col,
            }
        })

    geojson_str = _json.dumps({"type": "FeatureCollection", "features": features})

    return _HTML_TEMPLATE.replace('__GEOJSON__', geojson_str)


def _compute_atci(atdi: float, hifd: float) -> int:
    """Compute ATCI score (0-100)."""
    thresholds = [
        ('Art.5', hifd > 25),
        ('Art.7', atdi > 20),
        ('Art.9', atdi > 40),
        ('Art.11', atdi > 35),
        ('Art.12', atdi > 45),
        ('Art.17', atdi > 50),
        ('Art.20', hifd > 30),
        ('Art.21', hifd > 20),
        ('Art.33', atdi > 55),
        ('Art.35', atdi > 70),
    ]
    triggered = sum(1 for _, t in thresholds if t)
    return round(triggered / len(thresholds) * 100)


_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>HSAE v6.0.8 -- WebGIS Basin Risk Map v2</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:'Segoe UI',Arial,sans-serif;background:#0a0e1a;color:#e2e8f0;height:100vh;display:flex;flex-direction:column}

  /* ── HEADER ── */
  #hdr{height:56px;background:linear-gradient(135deg,#061F4A 0%,#0E6B6A 100%);
    display:flex;align-items:center;padding:0 16px;gap:12px;flex-shrink:0;
    box-shadow:0 2px 8px rgba(0,0,0,.4)}
  .hlogo{font-size:22px}
  .htitle{font-size:15px;font-weight:700;color:#fff}
  .hsub{font-size:11px;color:rgba(255,255,255,.65)}
  #hdr-right{margin-left:auto;display:flex;align-items:center;gap:8px}

  /* ── TOOLBAR ── */
  #toolbar{display:flex;align-items:center;gap:8px;padding:8px 16px;
    background:#111827;border-bottom:1px solid #1f2937;flex-shrink:0;flex-wrap:wrap}
  .tb-group{display:flex;align-items:center;gap:6px}
  .tb-label{font-size:11px;color:#9ca3af;white-space:nowrap}
  select,#search{background:#1f2937;color:#e2e8f0;border:1px solid #374151;
    border-radius:6px;padding:5px 8px;font-size:12px;cursor:pointer}
  select:focus,#search:focus{outline:none;border-color:#0E6B6A}
  #search{width:200px}
  .btn{background:#1f2937;color:#e2e8f0;border:1px solid #374151;
    border-radius:6px;padding:5px 10px;font-size:12px;cursor:pointer;
    transition:all .2s;white-space:nowrap}
  .btn:hover{background:#374151;border-color:#6b7280}
  .btn.active{background:#0E6B6A;border-color:#0E6B6A;color:#fff}
  #stat-bar{margin-left:auto;display:flex;gap:12px;font-size:11px;color:#9ca3af}
  .stat-item span{color:#60a5fa;font-weight:600}

  /* ── MAP ── */
  #map{flex:1}

  /* ── LEGEND ── */
  .legend{background:rgba(10,14,26,.92);border:1px solid #1f2937;
    border-radius:8px;padding:10px 14px;font-size:11px;line-height:1.9;
    backdrop-filter:blur(4px)}
  .legend h4{font-size:12px;color:#60a5fa;margin-bottom:6px;font-weight:600}
  .dot{display:inline-block;width:12px;height:12px;border-radius:50%;
    margin-right:6px;vertical-align:middle;border:1px solid rgba(255,255,255,.2)}
  .legend hr{border:none;border-top:1px solid #1f2937;margin:6px 0}
  .legend small{color:#6b7280;display:block}

  /* ── POPUP ── */
  .leaflet-popup-content-wrapper{
    background:#111827;border:1px solid #1f2937;border-radius:10px;
    color:#e2e8f0;padding:0;overflow:hidden;min-width:300px;
    box-shadow:0 8px 32px rgba(0,0,0,.5)}
  .leaflet-popup-content{margin:0;width:auto!important}
  .leaflet-popup-tip{background:#111827}
  .p-hdr{padding:12px 14px;border-bottom:1px solid #1f2937}
  .p-name{font-size:14px;font-weight:700;color:#fff}
  .p-sub{font-size:11px;color:#9ca3af;margin-top:2px}
  .p-badge{display:inline-block;padding:2px 8px;border-radius:12px;
    font-size:11px;font-weight:700;margin-top:6px}
  .p-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;padding:12px 14px}
  .p-kv{background:#1f2937;border-radius:6px;padding:6px 8px}
  .p-k{font-size:10px;color:#6b7280;margin-bottom:2px}
  .p-v{font-size:13px;font-weight:600;color:#fff}
  .p-chart{padding:10px 14px;border-top:1px solid #1f2937}
  .p-chart-title{font-size:11px;color:#6b7280;margin-bottom:6px}
  .p-chart canvas{border-radius:4px}
  .p-footer{padding:8px 14px;border-top:1px solid #1f2937;
    font-size:10px;color:#4b5563;background:#0d1117}

  /* ── SEARCH RESULTS ── */
  #search-results{position:absolute;top:100%;left:0;right:0;background:#1f2937;
    border:1px solid #374151;border-top:none;border-radius:0 0 6px 6px;
    z-index:1000;display:none;max-height:200px;overflow-y:auto}
  #search-results div{padding:6px 10px;cursor:pointer;font-size:12px}
  #search-results div:hover{background:#374151}
  .search-wrap{position:relative}

  /* ── SIDEBAR ── */
  #sidebar{position:absolute;right:0;top:0;bottom:0;width:280px;
    background:#111827;border-left:1px solid #1f2937;z-index:500;
    transform:translateX(100%);transition:transform .3s;overflow-y:auto;
    display:none}
  #sidebar.open{transform:translateX(0)}
  .sb-hdr{padding:12px 14px;border-bottom:1px solid #1f2937;
    display:flex;justify-content:space-between;align-items:center}
  .sb-hdr h3{font-size:13px;font-weight:600;color:#fff}
  .close-btn{background:none;border:none;color:#9ca3af;cursor:pointer;font-size:18px}
  .sb-row{padding:10px 14px;border-bottom:1px solid #0d1117;cursor:pointer;
    transition:background .15s}
  .sb-row:hover{background:#1f2937}
  .sb-name{font-size:12px;font-weight:600;color:#e2e8f0}
  .sb-vals{font-size:11px;color:#6b7280;margin-top:2px}
  .sb-badge{float:right;padding:2px 6px;border-radius:4px;
    font-size:10px;font-weight:700;margin-top:2px}
</style>
</head>
<body>

<!-- HEADER -->
<div id="hdr">
  <span class="hlogo">🌊</span>
  <div>
    <div class="htitle">HydroSovereign AI Engine v6.0.8 -- WebGIS Basin Risk Map v2</div>
    <div class="hsub">26 Globally Contested Basins &middot; ATDI &middot; AHIFD &middot; ATCI &middot; UNWC 1997 &middot; Plugin ID: 5040</div>
  </div>
  <div id="hdr-right">
    <button class="btn" onclick="exportPNG()" title="Export map as PNG">&#128247; Export PNG</button>
    <button class="btn" onclick="toggleSidebar()" title="Basin rankings">&#8801; Rankings</button>
  </div>
</div>

<!-- TOOLBAR -->
<div id="toolbar">
  <div class="tb-group">
    <span class="tb-label">Layer:</span>
    <select id="layer-sel" onchange="switchLayer()">
      <option value="atdi">ATDI Risk</option>
      <option value="ahifd">AHIFD Flow Deficit</option>
      <option value="ci">Conflict Index</option>
      <option value="atci">Treaty Compliance (ATCI)</option>
    </select>
  </div>
  <div class="tb-group">
    <span class="tb-label">Basemap:</span>
    <select id="basemap-sel" onchange="switchBasemap()">
      <option value="dark">Dark (CARTO)</option>
      <option value="light">Light (CARTO)</option>
      <option value="satellite">Satellite (ESRI)</option>
      <option value="osm">OpenStreetMap</option>
    </select>
  </div>
  <div class="tb-group">
    <span class="tb-label">Filter:</span>
    <select id="filter-sel" onchange="applyFilter()">
      <option value="all">All Basins</option>
      <option value="critical">Critical (CI &ge;0.55)</option>
      <option value="high">High Risk (ATDI &ge;40%)</option>
      <option value="art33">Art.33 Dispute Zone</option>
      <option value="art7">Art.7 Notify Zone</option>
      <option value="compliant">Compliant</option>
    </select>
  </div>
  <div class="tb-group search-wrap">
    <input id="search" placeholder="&#128269; Search basin..." oninput="searchBasin()"
           onblur="setTimeout(()=>document.getElementById('search-results').style.display='none',200)"/>
    <div id="search-results"></div>
  </div>
  <div id="stat-bar">
    <div class="stat-item">Basins: <span id="st-count">26</span></div>
    <div class="stat-item">Critical: <span id="st-crit">--</span></div>
    <div class="stat-item">High Risk: <span id="st-high">--</span></div>
  </div>
</div>

<!-- MAP -->
<div id="map"></div>

<!-- SIDEBAR -->
<div id="sidebar">
  <div class="sb-hdr">
    <h3>&#127942; Basin Rankings</h3>
    <button class="close-btn" onclick="toggleSidebar()">&times;</button>
  </div>
  <div id="sb-list"></div>
</div>

<script>
// ── DATA ──────────────────────────────────────────────────────────────────
const GJ = __GEOJSON__;
const features = GJ.features;

// ── BASEMAPS ──────────────────────────────────────────────────────────────
const BASEMAPS = {
  dark: L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    {attribution:'&copy; CARTO &middot; HSAE v6.0.8',subdomains:'abcd',maxZoom:19}),
  light: L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
    {attribution:'&copy; CARTO &middot; HSAE v6.0.8',subdomains:'abcd',maxZoom:19}),
  satellite: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    {attribution:'&copy; ESRI &middot; HSAE v6.0.8',maxZoom:19}),
  osm: L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    {attribution:'&copy; OpenStreetMap &middot; HSAE v6.0.8',maxZoom:19}),
};

// ── MAP INIT ──────────────────────────────────────────────────────────────
const map = L.map('map',{center:[20,20],zoom:2,minZoom:1,maxZoom:12});
let currentBasemap = 'dark';
BASEMAPS.dark.addTo(map);

// ── COLOUR HELPERS ────────────────────────────────────────────────────────
function colourFor(layer, p) {
  if (layer === 'atdi') return p.colour;
  if (layer === 'ahifd') {
    if (p.hifd < 15) return '#16a34a';
    if (p.hifd < 25) return '#ca8a04';
    if (p.hifd < 35) return '#ea580c';
    return '#dc2626';
  }
  if (layer === 'ci') {
    if (p.ci < 0.3) return '#16a34a';
    if (p.ci < 0.45) return '#ca8a04';
    if (p.ci < 0.55) return '#ea580c';
    return '#dc2626';
  }
  if (layer === 'atci') {
    if (p.atci < 20) return '#16a34a';
    if (p.atci < 40) return '#ca8a04';
    if (p.atci < 70) return '#ea580c';
    if (p.atci < 90) return '#dc2626';
    return '#7c3aed';
  }
  return p.colour;
}

function radiusFor(layer, p) {
  const val = layer==='atdi'?p.atdi : layer==='ahifd'?p.hifd :
              layer==='ci'?p.ci*100 : p.atci;
  return Math.max(6, Math.min(20, val / 5 + 4));
}

// ── MARKERS ───────────────────────────────────────────────────────────────
let markers = [];
let currentLayer = 'atdi';
let currentFilter = 'all';
let chartInstances = {};

function makePopup(p) {
  const atdiBar = Math.min(100, p.atdi);
  const hifdBar = Math.min(100, p.hifd);
  const atciBar = Math.min(100, p.atci);
  const ciBar   = Math.min(100, p.ci * 100);

  return `
<div>
  <div class="p-hdr">
    <div class="p-name">&#127754; ${p.name}</div>
    <div class="p-sub">${p.dam} &middot; ${p.river} &middot; ${p.countries || p.nc + ' states'}</div>
    <div>
      <span class="p-badge" style="background:${p.colour};color:#fff">${p.zone}</span>
      <span class="p-badge" style="background:#1f2937;color:#9ca3af;margin-left:4px">
        CI: ${p.ci.toFixed(2)} ${p.dlvl}
      </span>
    </div>
  </div>
  <div class="p-grid">
    <div class="p-kv">
      <div class="p-k">ATDI</div>
      <div class="p-v" style="color:${p.colour}">${p.atdi}%</div>
    </div>
    <div class="p-kv">
      <div class="p-k">AHIFD</div>
      <div class="p-v">${p.hifd}%</div>
    </div>
    <div class="p-kv">
      <div class="p-k">NSE / KGE</div>
      <div class="p-v">${p.nse} / ${p.kge}</div>
    </div>
    <div class="p-kv">
      <div class="p-k">P(Negotiation)</div>
      <div class="p-v">${p.pneg}%</div>
    </div>
    <div class="p-kv">
      <div class="p-k">ATCI</div>
      <div class="p-v" style="color:#a78bfa">${p.atci}%</div>
    </div>
    <div class="p-kv">
      <div class="p-k">Treaty</div>
      <div class="p-v" style="font-size:11px">${p.treaty||'--'}</div>
    </div>
  </div>
  <div class="p-chart">
    <div class="p-chart-title">&#128202; Index Comparison</div>
    <canvas id="chart-${p.name.replace(/[^a-z0-9]/gi,'_')}"
      width="280" height="110"></canvas>
  </div>
  <div class="p-footer">
    HSAE v6.0.8 &middot; Plugin ID: 5040 &middot; DOI: 10.5281/zenodo.19180160
  </div>
</div>`;
}

function drawChart(p) {
  const id = 'chart-' + p.name.replace(/[^a-z0-9]/gi, '_');
  const canvas = document.getElementById(id);
  if (!canvas) return;
  if (chartInstances[id]) {
    chartInstances[id].destroy();
    delete chartInstances[id];
  }
  const ctx = canvas.getContext('2d');
  chartInstances[id] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['ATDI %', 'AHIFD %', 'CI x100', 'ATCI %', 'P(Neg) %'],
      datasets: [{
        data: [p.atdi, p.hifd, p.ci * 100, p.atci, p.pneg],
        backgroundColor: [p.colour, '#0E6B6A', '#f59e0b', '#a78bfa', '#3b82f6'],
        borderRadius: 4,
        borderSkipped: false,
      }]
    },
    options: {
      responsive: false,
      plugins: {legend: {display: false}},
      scales: {
        x: {ticks: {color: '#9ca3af', font: {size: 9}},
            grid: {color: '#1f2937'}},
        y: {ticks: {color: '#9ca3af', font: {size: 9}},
            grid: {color: '#1f2937'}, min: 0, max: 100},
      }
    }
  });
}

function buildMarkers(layerKey) {
  markers.forEach(m => map.removeLayer(m));
  markers = [];
  const filter = document.getElementById('filter-sel').value;

  let shown = 0;
  let critical = 0;
  let high = 0;

  features.forEach(f => {
    const p = f.properties;
    const [lon, lat] = f.geometry.coordinates;

    // Apply filter
    if (filter === 'critical' && p.ci < 0.55) return;
    if (filter === 'high' && p.atdi < 40) return;
    if (filter === 'art33' && p.atdi < 55) return;
    if (filter === 'art7' && (p.atdi < 20 || p.atdi >= 40)) return;
    if (filter === 'compliant' && p.atdi >= 20) return;

    shown++;
    if (p.ci >= 0.55) critical++;
    if (p.atdi >= 40) high++;

    const col = colourFor(layerKey, p);
    const rad = radiusFor(layerKey, p);

    const m = L.circleMarker([lat, lon], {
      radius: rad,
      fillColor: col,
      color: '#ffffff',
      weight: 1.5,
      opacity: 1,
      fillOpacity: 0.88,
    });

    m.bindTooltip(
      `<b>${p.name}</b><br>ATDI ${p.atdi}% &middot; CI ${p.ci.toFixed(2)}`,
      {permanent: false, direction: 'top', className: ''}
    );

    m.bindPopup(makePopup(p), {maxWidth: 320, maxHeight: 480});
    m.on('popupopen', () => setTimeout(() => drawChart(p), 50));
    m.addTo(map);
    markers.push(m);
  });

  // Update stats
  document.getElementById('st-count').textContent = shown;
  document.getElementById('st-crit').textContent = critical;
  document.getElementById('st-high').textContent = high;
}

// ── CONTROLS ──────────────────────────────────────────────────────────────
function switchLayer() {
  currentLayer = document.getElementById('layer-sel').value;
  buildMarkers(currentLayer);
  updateLegend();
}

function applyFilter() {
  buildMarkers(currentLayer);
}

function switchBasemap() {
  const sel = document.getElementById('basemap-sel').value;
  BASEMAPS[currentBasemap].remove();
  BASEMAPS[sel].addTo(map);
  map.eachLayer(l => { if (l !== BASEMAPS[sel]) return; });
  // re-add markers on top
  BASEMAPS[sel].addTo(map);
  currentBasemap = sel;
  buildMarkers(currentLayer);
}

function searchBasin() {
  const q = document.getElementById('search').value.toLowerCase();
  const res = document.getElementById('search-results');
  if (!q) { res.style.display = 'none'; return; }
  const matches = features.filter(f =>
    f.properties.name.toLowerCase().includes(q) ||
    (f.properties.river||'').toLowerCase().includes(q)
  );
  if (!matches.length) { res.style.display = 'none'; return; }
  res.innerHTML = matches.slice(0,8).map(f =>
    `<div onclick="flyTo('${f.properties.name}')">
      ${f.properties.name} <small style="color:#6b7280">${f.properties.atdi}% ATDI</small>
    </div>`
  ).join('');
  res.style.display = 'block';
}

function flyTo(name) {
  document.getElementById('search-results').style.display = 'none';
  document.getElementById('search').value = name;
  const f = features.find(f => f.properties.name === name);
  if (!f) return;
  const [lon, lat] = f.geometry.coordinates;
  map.flyTo([lat, lon], 5, {duration: 1.2});
  setTimeout(() => {
    const m = markers.find(m => {
      const ll = m.getLatLng();
      return Math.abs(ll.lat - lat) < 0.01 && Math.abs(ll.lng - lon) < 0.01;
    });
    if (m) m.openPopup();
  }, 1500);
}

function toggleSidebar() {
  const sb = document.getElementById('sidebar');
  sb.style.display = sb.style.display === 'none' ? 'block' : 'none';
  if (sb.style.display === 'block') {
    sb.classList.add('open');
    buildSidebar();
  } else {
    sb.classList.remove('open');
  }
}

function buildSidebar() {
  const sorted = [...features].sort((a, b) =>
    b.properties.ci - a.properties.ci
  );
  document.getElementById('sb-list').innerHTML = sorted.map((f, i) => {
    const p = f.properties;
    return `
<div class="sb-row" onclick="flyTo('${p.name}')">
  <span style="color:#6b7280;font-size:10px">#${i+1}</span>
  <span class="sb-badge" style="background:${p.colour};color:#fff">${p.atdi}%</span>
  <div class="sb-name">${p.name}</div>
  <div class="sb-vals">CI: ${p.ci.toFixed(3)} &middot; ATCI: ${p.atci}% &middot; P(Neg.): ${p.pneg}%</div>
</div>`;
  }).join('');
}

function exportPNG() {
  import('https://unpkg.com/leaflet-image@0.4.0/leaflet-image.js')
    .catch(() => {
      // fallback: open print dialog
      alert('Tip: Use Ctrl+P / Cmd+P to print this page as PDF.');
    });
}

// ── LEGEND ────────────────────────────────────────────────────────────────
const legendCtrl = L.control({position: 'bottomright'});
legendCtrl.onAdd = function() {
  const div = L.DomUtil.create('div', 'legend');
  div.id = 'legend-box';
  updateLegendContent(div, 'atdi');
  return div;
};
legendCtrl.addTo(map);

function updateLegend() {
  const div = document.getElementById('legend-box');
  if (div) updateLegendContent(div, currentLayer);
}

function updateLegendContent(div, layer) {
  const entries = {
    atdi: [
      ['#16a34a','< 20%  Compliant'],
      ['#ca8a04','20-40%  Art.7 Notify'],
      ['#ea580c','40-55%  Art.9 Data Share'],
      ['#dc2626','55-70%  Art.33 Dispute'],
      ['#7c3aed','&ge; 70%  Art.35 Emergency'],
    ],
    hifd: [
      ['#16a34a','< 15%  Low deficit'],
      ['#ca8a04','15-25%  Moderate'],
      ['#ea580c','25-35%  High'],
      ['#dc2626','&ge; 35%  Critical'],
    ],
    ci: [
      ['#16a34a','< 0.30  Low'],
      ['#ca8a04','0.30-0.45  Moderate'],
      ['#ea580c','0.45-0.55  High'],
      ['#dc2626','&ge; 0.55  Critical'],
    ],
    atci: [
      ['#16a34a','< 20%  Compliant'],
      ['#ca8a04','20-40%  Minor'],
      ['#ea580c','40-70%  Moderate'],
      ['#dc2626','70-90%  High'],
      ['#7c3aed','&ge; 90%  Critical'],
    ],
  };
  const labels = {
    atdi:'ATDI Risk Level', hifd:'AHIFD Flow Deficit',
    ci:'Conflict Index', atci:'Treaty Compliance (ATCI)'
  };
  const rows = entries[layer] || entries.atdi;
  div.innerHTML = `<h4>${labels[layer]||'Risk Level'}</h4>` + rows.map(([c,l]) =>
      `<span class="dot" style="background:${c}"></span>${l}<br>`
    ).join('') + `<hr><small>Circle size &prop; risk level &middot; Click for analysis</small>`;
}

// ── ATTRIBUTION ───────────────────────────────────────────────────────────
const attrCtrl = L.control({position: 'bottomleft'});
attrCtrl.onAdd = function() {
  const div = L.DomUtil.create('div', 'legend');
  div.innerHTML = `<b>HSAE v6.0.8</b> &middot; Plugin ID: 5040<br>
    DOI: <a href="https://doi.org/10.5281/zenodo.19180160" target="_blank"
      style="color:#60a5fa">10.5281/zenodo.19180160</a><br>
    ORCID: <a href="https://orcid.org/0000-0003-0821-2991" target="_blank"
      style="color:#60a5fa">0000-0003-0821-2991</a>`;
  return div;
};
attrCtrl.addTo(map);

// ── INIT ──────────────────────────────────────────────────────────────────
buildMarkers('atdi');

</script>
</body>
</html>"""
