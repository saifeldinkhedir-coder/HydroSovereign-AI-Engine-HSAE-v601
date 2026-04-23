# HydroSovereign AI Engine — QGIS Plugin v6.01

[![QGIS](https://img.shields.io/badge/QGIS-≥3.16-589632?style=flat&logo=qgis&logoColor=white)](https://plugins.qgis.org/plugins/HydroSovereign_HSAE/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19180160.svg)](https://doi.org/10.5281/zenodo.19180160)
[![SoftwareX](https://img.shields.io/badge/SoftwareX-Under%20Review%202026-005A8E)](https://doi.org/10.5281/zenodo.19180160)

**Author:** Seifeldin M.G. Alkedir · [ORCID 0000-0003-0821-2991](https://orcid.org/0000-0003-0821-2991)  
**Affiliation:** University of Khartoum  
**QGIS Plugin Repository:** https://plugins.qgis.org/plugins/HydroSovereign_HSAE/  
**Live Streamlit App:** https://hydrosovereign-ai-engine-hsae-v601-6euz2zxcmerkzxgordmvxf.streamlit.app  
**DOI:** [10.5281/zenodo.19180160](https://doi.org/10.5281/zenodo.19180160)

---


## 📖 Full Documentation

| Format | Link | Size |
|--------|------|------|
| **PDF** (recommended) | [HSAE_v601_QGIS_Plugin_Manual_v3.pdf](HSAE_v601_QGIS_Plugin_Manual_v3.pdf) | 440 KB |
| **Word (DOCX)** | [HSAE_v601_QGIS_Plugin_Manual_v3.docx](HSAE_v601_QGIS_Plugin_Manual_v3.docx) | 30 KB |

**Manual contents:**
- Quick Start (5-minute tutorial)
- 13 Tools — complete reference
- 5 Processing Algorithms
- 26 Basin registry with ATDI/HIFD values
- Scientific indices (ATDI, HIFD, CI, HBV-96)
- Troubleshooting & FAQ
- Glossary (14 terms) & All links


## Overview

The **HydroSovereign AI Engine (HSAE) QGIS Plugin v6.01** brings AI-powered transboundary water sovereignty analysis directly into the QGIS desktop GIS environment. It provides **13 interactive tools** and **5 Processing Toolbox algorithms** for hydrological analysis, legal compliance assessment under UNWC 1997, conflict risk evaluation, and ICJ/PCA dossier export — all operating on a registry of 26 globally contested transboundary river basins.

This plugin does **not** require a separate QGIS profile. It installs into your existing QGIS installation and adds its own toolbar and Processing provider.

---

## Does It Require a Separate Profile?

**No.** The plugin installs cleanly into any standard QGIS profile (≥ 3.16):

- Adds a `HydroSovereign AI Engine v6.01` menu to the QGIS menu bar
- Adds an **HSAE v6.01 toolbar** with all 11 main tool buttons
- Registers an **HSAE Processing Provider** in the Processing Toolbox
- Adds a **dockable real-time Dashboard Panel** (right-side dock by default)
- All components are removed cleanly on plugin unload / uninstall

If you prefer isolation, you can create a dedicated profile (`Settings → User Profiles → New Profile`), but it is **not required**.

---

## Installation

### Method 1 — QGIS Plugin Repository (Recommended)

```
QGIS → Plugins → Manage and Install Plugins
     → Search: "HydroSovereign"
     → Install Plugin
```

### Method 2 — Install from ZIP

1. Download `HSAE_v601_QGIS_Plugin_FINAL.zip` from:
   - [GitHub Releases](https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601)
   - [Zenodo](https://doi.org/10.5281/zenodo.19180160)

2. In QGIS:
```
Plugins → Manage and Install Plugins
        → Install from ZIP
        → Select HSAE_v601_QGIS_Plugin_FINAL.zip
        → Install Plugin
```

### Requirements

| Component | Minimum Version |
|---|---|
| QGIS | 3.16 LTR or newer |
| Python | 3.8+ (bundled with QGIS) |
| OS | Windows 10+, macOS 10.15+, Ubuntu 20.04+ |
| Internet | Required for GEE scripts and Open-Meteo data |

**No additional Python packages required.** All dependencies use QGIS-bundled libraries (PyQt5, qgis.core, json, pathlib).

---

## Plugin Structure

```
hsae_qgis/
├── __init__.py                  ← classFactory entry point
├── plugin.py                    ← Main plugin class (13 tools, 643 lines)
├── metadata.txt                 ← QGIS Plugin Repository metadata
├── icon.png                     ← Plugin icon
├── hsae_processing_provider.py  ← Processing Toolbox provider
├── algorithms/
│   ├── atdi_algorithm.py        ← ATDI Calculator algorithm
│   ├── hifd_algorithm.py        ← HIFD Calculator algorithm
│   ├── basin_report_algorithm.py← Basin Legal Report generator
│   ├── hbv_algorithm.py         ← HBV-96 Calibration (SCE-UA)
│   └── comparison_algorithm.py  ← Multi-Basin Comparison
├── basin_loader.py              ← Basin point layer loader
├── basins_50.json               ← 26-basin registry (TFDD/ICOW data)
├── basins_data.py               ← Basin data utilities
├── dashboard_panel.py           ← Real-time dockable dashboard
├── dialog_main.py               ← Main dashboard dialog
├── export_tool.py               ← Shapefile/GeoJSON/CSV export
├── legal_layer.py               ← UNWC legal risk overlay
├── tdi_visualiser.py            ← TDI graduated colour renderer
└── INSTALL_PLUGIN.md            ← Quick installation guide
```

---

## 13 Tools — Complete Reference

Access all tools via:
- **Menu:** `HydroSovereign AI Engine v6.01` in the QGIS menu bar
- **Toolbar:** `HSAE v6.01` toolbar (appears automatically after installation)

### Tool 1 — 🌊 Load Basin Registry

Loads all 26 transboundary basins as a QGIS point layer with full attribute table.

**Attributes included:**
`name`, `river`, `dam`, `country`, `treaty`, `legal_arts`, `lat`, `lon`, `cap` (BCM), `area_km2`, `runoff_c`, `dispute_level`, `context`, `ATDI`, `HIFD`, `NSE`, `KGE`, `CI`, `P_negotiation`

**Usage:**
1. Click `🌊 Load Basin Registry` in toolbar
2. Layer `HSAE Basin Registry (26 basins)` appears in the Layers panel
3. Open Attribute Table to inspect all computed indices

---

### Tool 2 — 📊 TDI/ATDI Visualiser

Applies a graduated colour renderer to the active basin layer based on ATDI values.

**Colour scale:**
| ATDI Range | Colour | UNWC Zone |
|---|---|---|
| 0–20% | 🟢 Green | Safe |
| 20–40% | 🟡 Yellow | Art. 7 zone |
| 40–55% | 🟠 Orange | Art. 9 zone |
| 55–70% | 🔴 Red | Art. 33 dispute |
| 70–100% | 🟣 Purple | Art. 35 emergency |

**Usage:**
1. Load Basin Registry (Tool 1)
2. Select the basin layer in the Layers panel
3. Click `📊 TDI/ATDI Visualiser`
4. Layer re-renders with ATDI graduated colours

---

### Tool 3 — ⚖️ UNWC Legal Layer

Creates a categorised legal risk layer showing UNWC 1997 compliance status.

**Categories:**
- `CRITICAL (Art.35)` — ATDI ≥ 70%
- `HIGH (Art.33)` — ATDI ≥ 55%
- `MEDIUM (Art.9)` — ATDI ≥ 40%
- `LOW (Art.7)` — ATDI ≥ 20%
- `COMPLIANT` — ATDI < 20%

---

### Tool 4 — 📤 Export Basin Data

Exports the 26-basin dataset to your choice of format:

- **GeoJSON** (`.geojson`) — for web mapping, Leaflet, Mapbox
- **Shapefile** (`.shp`) — for ArcGIS, other GIS tools
- **CSV** (`.csv`) — for Excel, R, Python analysis

**Usage:**
1. Click `📤 Export Basin Data`
2. Choose format and save location
3. All ATDI/HIFD/NSE/KGE/CI indices included in attributes

---

### Tool 5 — 📋 Dashboard Dialog

Opens the main HSAE analysis dashboard as a resizable dialog window.

**Features:**
- Select basin from dropdown (all 26 available)
- View computed ATDI, HIFD, NSE, KGE, Conflict Index
- Legal articles triggered under UNWC 1997
- Negotiation success probability
- Context notes from TFDD/ICOW database

---

### Tool 6 — 🛰️ GEE Script Generator (7 Sensors)

Generates ready-to-run Google Earth Engine (GEE) JavaScript code for 7 satellite data sources.

**Sensors covered:**

| # | Source | Variable | Resolution |
|---|---|---|---|
| 1 | GPM IMERG V07 | Daily precipitation (mm/day) | 0.1° / 30-min |
| 2 | GRACE-FO MASCON RL06v4 | TWS anomaly (cm) | 0.5° / monthly |
| 3 | SMAP 10km | Soil moisture (m³/m³) | 10 km / daily |
| 4 | Sentinel-1 GRD | SAR flood extent (VV dB) | 10 m / 6-12 days |
| 5 | Sentinel-2 SR | NDWI water mask | 10 m / 5 days |
| 6 | ERA5 Temperature | Air temperature (°C) | 0.25° / monthly |
| 7 | Open-Meteo API | T, P, ET₀, SM (free API) | 0.25° / daily |

**Usage:**
1. Click `🛰️ GEE Scripts (7 sensors)`
2. View the complete GEE JavaScript script
3. Click `💾 Save` → save as `.js`
4. Open [code.earthengine.google.com](https://code.earthengine.google.com)
5. Paste and run (GEE account required)

---

### Tool 7 — 📡 GRDC Stations Overlay

Loads 10 key Global Runoff Data Centre (GRDC) discharge stations as a point layer.

**Stations included:**

| GRDC ID | Station | Q_mean (m³/s) | Countries |
|---|---|---|---|
| 1040250 | Blue Nile / El Diem | 1,500 | Ethiopia/Sudan |
| 1040220 | Roseires Dam | 1,200 | Sudan |
| 2180010 | Aswan High Dam | 2,830 | Egypt |
| 2903430 | Euphrates / Birecik | 895 | Turkey |
| 2904000 | Tigris / Mosul | 700 | Iraq |
| 2267050 | Mekong / Luang Prabang | 2,800 | Laos |
| 2181200 | Indus / Tarbela | 2,400 | Pakistan |
| 6335060 | Amazon / Óbidos | 175,000 | Brazil |
| 6340900 | Paraná / Itaipu | 11,000 | Brazil/Paraguay |
| 6122800 | Mississippi / Vicksburg | 16,800 | USA |

---

### Tool 8 — ⚡ Conflict Index (26 Basins)

Computes the HSAE Conflict Index for all 26 basins and displays a ranked table.

**Conflict Index formula:**
```
CI = 0.40 × (ATDI/100) + 0.25 × (dispute_level/4) 
   + 0.20 × (HIFD/100) + 0.15 × (n_countries/6)
```

**Risk classification:**
- CI ≥ 0.60 → 🔴 CRITICAL
- CI ≥ 0.40 → 🟠 HIGH
- CI ≥ 0.25 → 🟡 MEDIUM
- CI < 0.25 → 🟢 LOW

**Output columns:** Basin · ATDI% · HIFD% · CI · Risk · Dispute Level  
**Export:** Save as `.csv` for further analysis

---

### Tool 9 — 🤝 Negotiation AI

Predicts negotiation success probability for all 26 basins using a GBM model trained on 478 historical TFDD/ICJ water dispute cases.

**Output columns:**
`Basin · P(Success) · Progress bar · Strategy · UN Pathway`

**Strategies:**
- P ≥ 65% → Cooperative (Art. 8 Direct)
- P ≥ 40% → Mediation (Art. 17)
- P ≥ 25% → PCA Arbitration (Art. 33)
- P < 25% → ICJ Referral

**Export:** Save ranked table as `.csv`

---

### Tool 10 — 🗺️ WebGIS Map Generator

Generates a standalone interactive HTML map (no server required) using Leaflet.js with all 26 basins plotted and styled by ATDI risk level.

**Features:**
- Dark basemap (CartoDB Dark Matter)
- Circle markers sized by ATDI severity
- Click any basin → right panel shows full data:
  - Identity: name, river, dam, countries, treaty
  - Physical: storage (BCM), area (km²)
  - Indices: ATDI%, HIFD%, NSE, KGE, CI, P(Negotiation)
  - Legal: dispute level, UN articles triggered
  - Context: TFDD/ICOW background notes
- Zero dependencies — opens in any browser offline

**Usage:**
1. Click `🗺️ WebGIS Map`
2. Choose save location (`.html`)
3. Map opens automatically in default browser

---

### Tool 11 — 📊 Basin Panel (Real-time Dashboard)

Toggles a **dockable QGIS panel** (right side by default) showing real-time basin indices.

**Usage:**
- First click: panel opens and docks to the right
- Second click: panel hides
- Third click: panel reappears
- Drag the panel to any dock position or float it

---

### Tool 12 — 🏛️ ICJ/PCA Dossier Export

Exports a complete legal dossier for all 26 basins in ICJ/PCA/ITLOS submission format.

**Available formats:**
- **HTML** (`.html`) — styled, printable, with all indices in a formatted table
- **Text** (`.txt`) — plain text, one basin per section

**Dossier includes for each basin:**
- Riparian states and treaty reference
- ATDI%, HIFD%, NSE, KGE, Conflict Index
- Dispute level classification
- Negotiation success probability
- UNWC 1997 articles triggered
- Context from TFDD/ICOW database
- SHA-256 data integrity reference
- Author, ORCID, DOI, generation timestamp

---

### Tool 13 — ℹ️ About HSAE v6.01

Displays plugin metadata: version, author, ORCID, DOI, links to GitHub, Streamlit App, and JOSS paper.

---

## 5 Processing Toolbox Algorithms

Access via: **Processing Toolbox → HydroSovereign AI Engine v6.01**

### Algorithm 1 — ATDI Calculator
`HSAE Indices → ATDI Calculator`

Computes the Alkedir Transparency Deficit Index for a single basin.

| Parameter | Type | Description |
|---|---|---|
| Runoff Coefficient | Number (0–1) | Basin runoff ratio (e.g. 0.38 for GERD) |
| Dam Capacity (BCM) | Number | Reservoir storage capacity (BCM) |
| Number of Countries | Integer | Riparian states sharing the basin |
| Dispute Level | Integer (1–5) | TFDD/ICOW conflict intensity score |

**Output:** `ATDI` (%) — Transparency Deficit Index

**Example (GERD):** RC=0.38, Cap=74 BCM, Countries=3, Dispute=4 → **ATDI = 53.5%**

---

### Algorithm 2 — HIFD Calculator
`HSAE Indices → HIFD Calculator`

Computes the Human-Induced Flow Deficit index.

| Parameter | Type | Description |
|---|---|---|
| Runoff Coefficient | Number (0–1) | Basin runoff ratio |
| Dam Capacity (BCM) | Number | Reservoir storage capacity |
| Number of Countries | Integer | Riparian states |
| Dispute Level | Integer (1–5) | Conflict intensity |

**Output:** `HIFD` (%) — Human-Induced Flow Deficit

**Example (GERD):** RC=0.38, Cap=74 BCM, Countries=3, Dispute=4 → **HIFD = 35.7%**

---

### Algorithm 3 — Basin Legal Report
`HSAE Reports → Basin Legal Report`

Generates a complete legal assessment report for a single basin.

| Parameter | Type | Description |
|---|---|---|
| Basin Name | String | Official name (e.g. "Blue Nile (GERD)") |
| Runoff Coefficient | Number | 0–1 |
| Dam Capacity (BCM) | Number | Storage BCM |
| Number of Countries | Integer | Riparian states |
| Dispute Level | Integer | 1–5 |
| Basin Area (km²) | Number | Catchment area |
| Treaty | String | Applicable treaty (e.g. "UN1997") |
| Output File | File path | `.txt` or `.html` |

**Output:** Full legal report with ATDI/HIFD, UNWC articles, negotiation strategy

---

### Algorithm 4 — HBV-96 Calibration (SCE-UA)
`HSAE Hydrology → HBV-96 Calibration (SCE-UA)`

Runs the HBV-96 rainfall-runoff model with Shuffled Complex Evolution calibration.

| Parameter | Type | Description |
|---|---|---|
| Basin Area (km²) | Number | Catchment area |
| Runoff Coefficient | Number | Initial estimate (0–1) |
| Mean Precipitation (mm/day) | Number | Annual mean P |
| Mean Temperature (°C) | Number | Annual mean T |
| Output CSV | File path | Calibration results file |

**Outputs:** `NSE`, `KGE`, CSV with calibrated parameters (FC, LP, β, K₁, K₂, MAXBAS)

---

### Algorithm 5 — Multi-Basin Comparison
`HSAE Reports → Multi-Basin Comparison`

Compares multiple basins and generates a ranked CSV + HTML report.

| Parameter | Type | Description |
|---|---|---|
| Basin Names | String | Comma-separated list (e.g. "Blue Nile (GERD), Mekong – Xayaburi Dam") |
| Output File | File path | `.csv` or `.html` |

**Output:** Ranked table with ATDI, HIFD, NSE, KGE, CI, risk level for each basin

---

## The 26 Registered Basins

| Region | Basin | Dam | Cap (BCM) | Countries | ATDI | HIFD |
|---|---|---|---|---|---|---|
| Africa | Blue Nile | GERD | 74.0 | 3 | 53.5% | 35.7% |
| Africa | Nile | Aswan High Dam | 162.0 | 2 | 33.1% | 32.2% |
| Africa | Nile | Roseires | 7.4 | 2 | 28.4% | 24.1% |
| Africa | Zambezi | Kariba | 180.6 | 2 | 31.1% | 29.2% |
| Africa | Congo | Inga | 2.0 | 8 | 49.1% | 28.5% |
| Africa | Niger | Kainji | 15.0 | 9 | 52.4% | 37.2% |
| Middle East | Euphrates | Atatürk | 48.7 | 3 | 44.5% | 34.9% |
| Middle East | Tigris | Mosul | 11.1 | 2 | 32.5% | 29.1% |
| Central Asia | Vakhsh | Nurek | 10.5 | 5 | 56.8% | 35.5% |
| Central Asia | Syr Darya | Toktogul | 19.5 | 4 | 48.2% | 31.4% |
| South Asia | Indus | Tarbela | 13.7 | 2 | 30.5% | 26.7% |
| South Asia | Brahmaputra | Subansiri | 2.4 | 3 | 29.1% | 18.6% |
| South Asia | Ganges | Farakka | 0.3 | 2 | 27.3% | 22.5% |
| SE Asia | Mekong | Xayaburi | 7.4 | 6 | 56.5% | 32.7% |
| SE Asia | Salween | Myitsone | 62.0 | 3 | 41.2% | 30.8% |
| East Asia | Yangtze | Three Gorges | 39.3 | 1 | 18.4% | 22.8% |
| Europe | Danube | Iron Gates | 2.4 | 10 | 40.0% | 25.4% |
| Europe | Rhine | Various | 0.5 | 9 | 27.1% | 18.6% |
| Europe | Dnieper | Kakhovka | 18.2 | 3 | 44.8% | 31.2% |
| Americas | Amazon | Belo Monte | 250.0 | 8 | 47.0% | 31.9% |
| Americas | Paraná | Itaipu | 29.0 | 2 | 17.5% | 21.4% |
| Americas | Orinoco | Guri | 135.0 | 2 | 22.6% | 24.3% |
| Americas | Colorado | Hoover | 36.7 | 2 | 33.4% | 32.5% |
| Americas | Columbia | Grand Coulee | 9.7 | 2 | 19.8% | 23.1% |
| Americas | Rio Grande | Amistad | 5.8 | 2 | 26.4% | 27.8% |
| Oceania | Murray-Darling | Hume | 3.0 | 2 | 21.3% | 19.7% |

---

## Scientific Indices Reference

### ATDI — Alkedir Transparency Deficit Index
```
TDIᵢ = clip[(I_adj,i − Q_obs,i) / (I_adj,i + ε), 0, 1]
ATDI  = (1/N) × Σ TDIᵢ × 100%
```
Calibrated against 14 published basin values. **RMSE = 4.1%**

**UNWC 1997 thresholds:**
- ATDI ≥ 20% → Art. 7 (no significant harm notification)
- ATDI ≥ 55% → Art. 9 (data sharing inconsistency)
- ATDI ≥ 70% → Art. 35 (emergency measures)

### HIFD — Human-Induced Flow Deficit
```
HIFD = [(Q_nat − Q_obs) / Q_nat] × 100%
```
Calibrated against 14 basin values. **RMSE = 1.8%**

**UNWC threshold:** HIFD ≥ 40% → Art. 5 (equitable utilisation assessment)

---

## Data Sources

| Source | Provider | Variable | Access |
|---|---|---|---|
| GPM IMERG V07 | NASA/JAXA | Precipitation | GEE (free) |
| GRACE-FO MASCON | NASA JPL | TWS anomaly | GEE (free) |
| Sentinel-1 GRD | ESA Copernicus | SAR backscatter | GEE (free) |
| Sentinel-2 SR | ESA Copernicus | NDWI/NDVI | GEE (free) |
| SMAP 10km | NASA | Soil moisture | GEE (free) |
| ERA5 | ECMWF | Temperature | GEE (free) |
| Open-Meteo | Open-Meteo.com | T, P, ET₀, SM | Free API |
| GRDC | BfG Koblenz | Discharge | Free (registration) |
| TFDD/ICOW | Oregon State | Dispute levels | Public database |

---

## Citation

If you use this plugin in research, please cite:

```bibtex
@software{alkedir2026hsae_qgis,
  author    = {Alkedir, Seifeldin M.G.},
  title     = {{HydroSovereign AI Engine (HSAE) QGIS Plugin v6.01}},
  year      = {2026},
  publisher = {QGIS Plugin Repository},
  url       = {https://plugins.qgis.org/plugins/HydroSovereign_HSAE/},
  doi       = {10.5281/zenodo.19180160},
  note      = {ORCID: 0000-0003-0821-2991}
}
```

Primary paper (SoftwareX, under review):
> Alkedir, S.M.G. (2026). HydroSovereign AI Engine (HSAE) v6.01: An Open-Source Satellite and AI Platform for Transboundary Water Sovereignty Analysis. *SoftwareX*. DOI: 10.5281/zenodo.19180160

---

## License

GNU General Public License v3.0 — see [LICENSE](LICENSE)

© 2026 Seifeldin M.G. Alkedir · ORCID: [0000-0003-0821-2991](https://orcid.org/0000-0003-0821-2991)

---

## Links

| Resource | URL |
|---|---|
| QGIS Plugin Repository | https://plugins.qgis.org/plugins/HydroSovereign_HSAE/ |
| Main GitHub Repo | https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601 |
| Live Streamlit App | https://hydrosovereign-ai-engine-hsae-v601-6euz2zxcmerkzxgordmvxf.streamlit.app |
| Python Package (PyPI) | https://pypi.org/project/hydrosovereign/ |
| Zenodo Archive | https://doi.org/10.5281/zenodo.19180160 |
| Bug Reports | https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601/issues |
