<div align="center">

# 🌊 HydroSovereign AI Engine — HSAE v6.01

> **🎉 QGIS Plugin officially listed in the QGIS Plugin Repository — April 21, 2026**  
> PR #289 approved by **Tim Sutton** (QGIS Project Steering Committee) and merged into master.  
> Install: **QGIS → Plugins → Manage and Install Plugins → Search "HydroSovereign"**

[![QGIS Plugin](https://img.shields.io/badge/QGIS_Plugin-ID_5040-589632?style=for-the-badge&logo=qgis&logoColor=white)](https://plugins.qgis.org/plugins/hsae_qgis/)
[![PyPI](https://img.shields.io/badge/PyPI-hydrosovereign_v6.5.3-3775A9?style=for-the-badge&logo=pypi&logoColor=white)](https://pypi.org/project/hydrosovereign/)
[![Live App](https://img.shields.io/badge/Live_App-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://hydrosovereign-ai-engine-hsae-v601-6euz2zxcmerkzxgordmvxf.streamlit.app)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.19180160-1682D4?style=for-the-badge&logo=zenodo&logoColor=white)](https://doi.org/10.5281/zenodo.19180160)
[![SoftwareX](https://img.shields.io/badge/SoftwareX-SOFTX--D--26--00442-005A8E?style=for-the-badge)](https://doi.org/10.5281/zenodo.19180160)
[![License](https://img.shields.io/badge/License-GPL_3.0-blue?style=for-the-badge)](LICENSE)
[![ORCID](https://img.shields.io/badge/ORCID-0000--0003--0821--2991-a6ce39?style=for-the-badge&logo=orcid&logoColor=white)](https://orcid.org/0000-0003-0821-2991)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Tests](https://img.shields.io/badge/Tests-56_passing-brightgreen?style=flat&logo=pytest)](https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601/actions)

**26 basins · 7 geographic regions · 49 Python modules · 33 Streamlit pages · 0 syntax errors**

*"Satellites can now see what declarations hide — and climate change will make the gap worse."*

</div>

---

## 📌 Abstract

Transboundary water resources management poses one of the most complex challenges of the 21st century, requiring the integration of hydrological monitoring, legal frameworks, and predictive modelling within a unified decision-support environment. This study presents the **HydroSovereign AI Engine (HSAE) v6.01**, an open-source, multi-sensor integrated decision-support platform developed for the analysis and governance of **26 transboundary river basins** across **7 geographic regions** — Africa, the Middle East, Central Asia, Asia, the Americas, Europe, and Oceania.

The system integrates **seven Google Earth Engine (GEE) satellite sensors** — including GPM IMERG V07, GRACE-FO MASCON, SMAP soil moisture, Sentinel-1 SAR flood mapping, Sentinel-2 NDWI/NDVI, GloFAS ERA5 v4 discharge, and Open-Meteo — fetched in parallel via `concurrent.futures.ThreadPoolExecutor` with 24-hour caching, alongside **five AI/ML models** (Random Forest, MLP, Gradient Boosting, Isolation Forest, and Ensemble Kalman Filter Digital Twin) and **Shared Socioeconomic Pathway (SSP1/2/3/5) climate scenarios** to produce basin-scale hydrological forecasts, anomaly detection, and water balance simulations through to 2100.

Legal analysis is embedded through automated cross-referencing of **33 articles of the UN Watercourses Convention 1997**, enabling treaty compliance scoring, negotiation outcome prediction, ICJ/PCA/ITLOS dossier generation, and auto-generated diplomatic protest notes at the basin level. The platform incorporates a physics-based **HBV-96 catchment model** with SCE-UA calibration (NSE=0.63, KGE=0.74 pre-calibration), Monte Carlo uncertainty quantification, Sobol sensitivity analysis, MODFLOW groundwater module, Penman-Monteith ET₀, Muskingum routing, MUSLE sediment transport, water quality indicators (WQI), and a **Telegram-based real-time alert system** with four severity levels.

Ten original scientific contributions are introduced — including the **Alkedir Transparency Deficit Index (ATDI)**, the **Alkedir Human-Induced Flow Deficit (AHIFD)**, and the **Alkedir Water Sovereignty Risk Matrix (AWSRM)** — all documented in this repository as a timestamped scientific priority record pending peer-reviewed publication.

Implemented as a **49-module Python application** (31,273 lines · 33 pages · zero syntax errors), with a companion **QGIS Desktop Plugin** (13 tools + 5 Processing algorithms), HSAE v6.01 represents a novel contribution to the fields of hydro-diplomacy, satellite hydrology, and AI-driven water governance.

**Keywords:** transboundary water management · remote sensing · Google Earth Engine · machine learning · UN Watercourses Convention · decision support system · hydro-diplomacy · SSP climate scenarios · Digital Twin · Streamlit · QGIS · open-source hydrology

---

## 🔗 Quick Links

| Resource | Link | Description |
|----------|------|-------------|
| 🔌 **QGIS Plugin** | [plugins.qgis.org/plugins/hsae_qgis/](https://plugins.qgis.org/plugins/hsae_qgis/) | Plugin ID: 5040 · Approved April 21, 2026 |
| 🐍 **PyPI Package** | [pypi.org/project/hydrosovereign/](https://pypi.org/project/hydrosovereign/) | `pip install hydrosovereign` |
| 🌐 **Live Streamlit App** | [HSAE v6.01](https://hydrosovereign-ai-engine-hsae-v601-6euz2zxcmerkzxgordmvxf.streamlit.app) | 26 basins · 7 GEE sensors |
| 📦 **GitHub (App)** | [HydroSovereign-AI-Engine-HSAE-v601](https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601) | Main application |
| 📦 **GitHub (Package)** | [hydrosovereign](https://github.com/saifeldinkhedir-coder/hydrosovereign) | Python package |
| 🏛️ **Zenodo DOI** | [10.5281/zenodo.19180160](https://doi.org/10.5281/zenodo.19180160) | Permanent archive |
| 📄 **SoftwareX Paper** | SOFTX-D-26-00442 | Under Review 2026 · Elsevier |
| 📖 **Manual PDF** | [⬇️ Download Manual v5](https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601/raw/main/hsae_qgis/HSAE_v601_QGIS_Plugin_Manual_v6.docx) | Complete QGIS Plugin Guide |
| 🐛 **Bug Reports** | [Issues](https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601/issues) | GitHub Issues tracker |

---

## 🏆 Research Title

> **HydroSovereign AI Engine (HSAE v6.01): An Open-Source Platform Integrating Multi-Sensor Satellite Earth Observation, Machine Learning, and the UN Watercourses Convention 1997 for Transboundary River Basin Sovereignty Analysis**
>
> *Seifeldin M.G. Alkedir — Institute of Environmental Studies, University of Khartoum · ORCID: 0000-0003-0821-2991*

---

## 👤 Author

**Seifeldin M.G. Alkedir** — سيف الدين محمد قسم الله الخضر

| | |
|--|--|
| 🎓 **Education** | M.Sc. Environmental Science · B.Sc. Chemistry — University of Khartoum |
| 💼 **Role** | Independent Researcher · Environmental Manager & Consulting Project Manager (10+ years) |
| 🏗️ **Previous Experience** | NEOM City · Saudi Aramco · Rua Al Madinah · Municipal Mega-Projects (KSA) |
| 📜 **Certifications** | ISO 14001 · PMP · IOSH |
| 🛠️ **Technical** | CESMP · EIA/ESIA · Air & Noise Modelling (AERMOD, SoundPLAN) · GIS & Remote Sensing |
| 📍 **Location** | Madinah, Saudi Arabia |
| 📞 **Phone** | +966 0500896171 |
| 📧 **Email** | [saifeldinkhedir@gmail.com](mailto:saifeldinkhedir@gmail.com) |
| 🔬 **ORCID** | [0000-0003-0821-2991](https://orcid.org/0000-0003-0821-2991) |
| 💼 **LinkedIn** | [seifelden-alkhedir](https://www.linkedin.com/in/seifelden-alkhedir-6b730985/) |
| 📦 **Zenodo** | [DOI Records & Datasets](https://zenodo.org/search?q=0000-0003-0821-2991) |
| 🎬 **YouTube** | [HSAE Video Channel](https://www.youtube.com/@seifeldinalkedir) |
| 📄 **CV** | [Download PDF](https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601/raw/main/CV_Seifeldin_Alkedir.pdf) |

---

## 📖 Documentation & Manual

| Format | Download | Size | Contents |
|--------|----------|------|----------|
| 📕 **DOCX Manual v6** | [⬇️ Download PDF](https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601/raw/main/hsae_qgis/HSAE_v601_QGIS_Plugin_Manual_v6.docx) | ~830 KB | Complete guide — 15 chapters (Tools 14/15/16 added) + 5 appendices |
| 📘 **DOCX Manual v6** | [⬇️ Download DOCX](https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601/raw/main/hsae_qgis/HSAE_v601_QGIS_Plugin_Manual_v6.docx) | ~60 KB | Editable Word format |
| 🌐 **Online Viewer** | [View on GitHub](https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601/blob/main/hsae_qgis/HSAE_v601_QGIS_Plugin_Manual_v6.docx) | — | Preview in browser |

**Manual includes:**
- ⚡ Quick Start (5-minute tutorial)
- 🛠️ All 13 Tools — step-by-step with screenshots
- ⚙️ 5 Processing Algorithms — complete reference
- 🗺️ 26 Basin registry with ATDI/HIFD values
- 📊 Scientific indices (ATDI, HIFD, CI, HBV-96, NSE, KGE)
- 🖥️ QGIS Desktop operating guide (Ch. 11)
- 🔧 Advanced Features: Model Builder, Batch Processing, Python API (Ch. 12)
- 🌏 Case Study 2: Mekong Basin (Ch. 13)
- 🆘 Troubleshooting & FAQ (16 common errors)
- 📚 Glossary (23 terms) + Keyword Index (47 entries)
- 🖨️ Quick Reference Card (print-ready A5)

---

## 🌊 What is HSAE?

HSAE v6.01 is a **transboundary water governance platform** that unifies:

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Earth Observation** | GEE · 7 satellite sensors | Real-time basin monitoring |
| **Hydrology** | HBV-96 · SCE-UA · MODFLOW | Discharge simulation & calibration |
| **AI/ML** | RF · GBM · MLP · EnKF | Forecasting & anomaly detection |
| **Legal** | UNWC 1997 · 33 articles | Treaty compliance & ICJ dossiers |
| **Diplomacy** | Negotiation AI · 478 cases | P(success) prediction |
| **Alert** | Telegram Bot | 4-level real-time alerts |
| **WebGIS** | Leaflet · 25+ fields | Interactive global basin map |
| **QGIS** | 13 tools · 5 algorithms | Desktop GIS integration |
| **Documentation** | 6 docs files | API · Examples · Formulas |
| **Testing** | 37 pytest tests | CI/CD GitHub Actions |

### 🌍 26 Basins — Full Registry

| Region | Basins |
|--------|--------|
| 🌍 **Africa (6)** | Blue Nile–GERD · Nile–Roseires · Nile–Aswan · Zambezi–Kariba · Congo–Inga · Niger–Kainji |
| 🕌 **Middle East (2)** | Euphrates–Atatürk · Tigris–Mosul |
| 🏔️ **Central Asia (2)** | Amu Darya–Nurek · Syr Darya–Toktogul |
| 🌏 **Asia (6)** | Mekong–Xayaburi · Yangtze–Three Gorges · Indus–Tarbela · Brahmaputra–Subansiri · Ganges–Farakka · Salween–Myitsone |
| 🌎 **Americas (6)** | Amazon–Belo Monte · Paraná–Itaipu · Orinoco–Guri · Colorado–Hoover · Columbia–Grand Coulee · Rio Grande–Amistad |
| 🏛️ **Europe (3)** | Danube–Iron Gates I · Rhine–Basin · Dnieper–Kakhovka |
| 🦘 **Oceania (1)** | Murray-Darling–Hume |

---

## 📊 System Statistics — v6.0.1 (April 2026)

| Metric | Value |
|--------|-------|
| Python modules | 49 |
| Lines of code | 31,273 |
| Streamlit pages | 33 |
| Transboundary basins | 26 |
| GEE satellite sensors | 7 (parallel fetch) |
| QGIS tools | 13 |
| QGIS Processing algorithms | 5 |
| pytest tests | 37 (8 test classes) |
| Documentation files | 6 |
| GitHub releases | 2 (v6.0.1 · v6.01.0) |
| CI/CD workflows | 2 (tests · daily GEE) |
| Syntax errors | 0 |
| NSE (pre-calibration) | 0.63 |
| KGE (pre-calibration) | 0.74 |
| Telegram Bot | @HASE_Water_bot |
| Live App | Streamlit Cloud |

---

## 🆕 Changelog — v6.0.1 (April 2026)

### 🔬 Science · Figure 3 — Water Balance
- 4-panel interactive figure: (a) GPM precipitation, (b) HBV-96 discharge, (c) ATDI, (d) GRACE-FO TWS
- NSE/KGE/HIFD/ATDI basin-specific for all 26 basins (TFDD/ICOW dispute data)
- Figure 3 reads calibrated NSE/KGE automatically after GRDC upload

### 🛰️ GEE Integration — 7 Parallel Sensors
- **GPM IMERG V07** — daily precipitation (11 km)
- **GRACE-FO MASCON RL06v4** — terrestrial water storage anomaly
- **SMAP 10km** — soil moisture (ssm field)
- **Sentinel-1 SAR** — flood mapping (VV polarization)
- **Sentinel-2 NDWI/NDVI** — water mask + vegetation
- **GloFAS ERA5 v4** — river discharge ensemble
- **Open-Meteo ERA5** — temperature, ET₀, soil moisture
- Parallel fetch via `concurrent.futures.ThreadPoolExecutor` · 24-hour caching
- GitHub Actions daily precompute (`precompute_gee_daily.py`)

### 💧 Groundwater · Water Quality Pages
- Data priority: Direct GEE → GRDC upload → GEE-derived → Simulation
- Water Quality: removed `statsmodels` dependency (lowess → `go.Scatter`)
- GRDC upload integration in HBV-96 page

### 🚨 Telegram Alert System
- Bot `@HASE_Water_bot` fully operational
- Pre-configured token + chat_id
- 4-level alerts: INFO / ALERT / WARNING / CRITICAL
- Auto-dispatch on ATDI threshold breach

### 🗺️ WebGIS — Comprehensive Interactive Map
- 25+ fields per basin popup: Identity · Physical · HSAE Indices · Remote Sensing · Legal & Risk · UN Articles · Context
- Progress bars for ATDI/HIFD
- Real dispute levels from TFDD/ICOW for all 26 basins
- NSE/KGE/WQI/ASI/CI/P(Negotiation) per basin
- Live GEE badge when Direct GEE active

### 🌊 HBV-96 + GRDC Upload
- GRDC upload widget in HBV-96 page
- SCE-UA calibration saves NSE/KGE to `session_state`
- Figure 3 reads calibrated values automatically
- NSE=0.63, KGE=0.74 pre-calibration published metrics

### ⚡ Conflict Index · Negotiation AI
- Basin-specific ATDI/HIFD for all 26 basins
- Real GBM Negotiation AI model enabled
- P(success) + strategy + UN Article path per basin

### 🔌 QGIS Plugin — FINAL (13 Tools + 5 Algorithms)
- **New tools**: Conflict Index · Negotiation AI · WebGIS Map · Real-Time Dashboard Panel
- **New algorithms**: HBV-96 Calibration (SCE-UA) · Multi-Basin Comparison (CSV + HTML)
- `basins_50.json` enriched: runoff_c · context · legal_arts · country list
- `basin_loader.py` rewritten: computes ATDI/HIFD/NSE/KGE per basin
- `export_tool.py`: added CSV export support
- Dashboard Panel: dockable real-time panel in QGIS

### 📚 Documentation (NEW — docs/)
- `docs/index.md` — Overview & quick start
- `docs/installation.md` — Full installation guide
- `docs/indices.md` — Mathematical formulas (ATDI, HIFD, NSE, KGE, WQI, CI)
- `docs/api_reference.md` — Module & function reference
- `docs/examples.md` — 7 working code examples
- `docs/qgis_plugin.md` — Complete QGIS plugin documentation

### 🧪 Tests — Expanded (37 tests)
- `tests/test_hsae.py` — 37 tests, 8 classes
- Covers: ATDI · HIFD · NSE · KGE · CI · HBV-96 · Legal thresholds · Negotiation AI
- CI/CD: `.github/workflows/tests.yml` runs on every push

---

## 🔬 Original Scientific Contributions

Ten original indices and frameworks introduced in HSAE, documented here to establish priority of authorship.

### Group A — Indices & Metrics

| Symbol | Full Name | Formula | Module |
|--------|-----------|---------|--------|
| **ATDI** | Alkedir Transparency Deficit Index | `clip((I_adj − Q_out) / (I_adj + ε), 0, 1)` · ε=0.001 | hsae_tdi.py |
| **AHIFD** | Alkedir Human-Induced Flow Deficit | `(Q_nat − Q_obs) / Q_nat × 100` | hsae_hbv.py |
| **AFSF** | Alkedir Forensic Signal Factor | `max(rolling_30(TDI)) × 100` | hsae_tdi.py |
| **ASI** | Alkedir Sovereignty Index | `0.35·E + 0.25·ADTS + 0.25·F + 0.15·(1−D/5)` | hsae_opsroom.py |
| **ADTS** | Alkedir Digital Transparency Score | `max(0, 100 − ATDI)` | hsae_opsroom.py |
| **α = 0.30** | Alkedir MODIS ET Correction Coefficient | `I_adj = max(0, I_in − 0.30 × (ET_PM + ET_MODIS))` | hsae_tdi.py |

### Group B — Frameworks & Architectures

| Symbol | Full Name | Description | Module |
|--------|-----------|-------------|--------|
| **ALTM** | Alkedir Legal Threshold Mapping | ATDI → UN 1997 Arts. 5/7/9/12/33 | hsae_tdi.py |
| **ASCAF** | Alkedir Satellite-Calibrated Anomaly Framework | SAR + NDWI + IsolationForest | hsae_v430.py |
| **AWSRM** | Alkedir Water Sovereignty Risk Matrix | 5×5 risk matrix: hydro × legal | hsae_opsroom.py |
| **AHLB** | Alkedir Hydrological-Legal Bridge | Q_obs → ATDI → UNWC article trigger | hsae_hbv.py |
| **ATCI** | Alkedir Treaty Compliance Index | Article-level scoring across 15 treaties | treaty_diff.py |

### Standard Methods (credited to original authors)

HBV (Bergström, 1992) · Penman-Monteith ET₀ (Allen et al., 1998) · SCS-CN (USDA, 1986) · Muskingum (McCarthy, 1938) · NSE/KGE (Nash & Sutcliffe, 1970; Gupta et al., 2009) · Random Forest (Breiman, 2001) · Ensemble Kalman Filter (Evensen, 2003) · MUSLE (Williams, 1975) · Sobol indices (Saltelli, 2002)

---

## 🗺️ 33 Streamlit Pages

### v6.0.0 Core (19 pages)
🌐 v430 Hybrid DSS · 📐 TDI/ATDI/AFSF · 🌌 GRACE-FO · 🤝 Negotiation AI · ⚡ Conflict Index · 🌡️ Climate SSP · 🤖 AI Forecast · 🛡️ Audit Chain · 📊 Validation/GRDC · 📡 Digital Twin · 🏛️ Legal/Treaty · 📁 Export · 🌿 Sediment · 💹 Benchmark · 🔬 GERD Case · 📋 Ops Room · 📤 Upload · ⚙️ DevOps · 🌍 Intro

### v6.01 Science+ (5 pages)
🔬 Science · Water Balance · 🌊 HBV-96 · Catchment Model · 💧 Groundwater · 🧪 Water Quality · 🚨 Alerts · Telegram

### v6.01 Satellite (3 pages)
🛰️ GPM Live · 🌍 GRACE-FO TWS · 💧 SMAP Soil Moisture

### v6.01 Legal+ (3 pages)
📜 Legal · Treaty Engine · 📊 UNWC Compliance · 🗺️ WebGIS · Global Map

### v6.01 Intelligence (3 pages)
🤝 Negotiation AI · 🔮 Climate 2100 · 📊 Validation · GRDC

---

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601
cd HydroSovereign-AI-Engine-HSAE-v601

# 2. Install
pip install -r requirements.txt

# 3. Run
streamlit run app.py
```

**Live App:** [https://hydrosovereign-ai-engine-hsae-v601-6euz2zxcmerkzxgordmvxf.streamlit.app](https://hydrosovereign-ai-engine-hsae-v601-6euz2zxcmerkzxgordmvxf.streamlit.app)

### Docker
```bash
docker-compose up
```

---

## 🏗️ Architecture — v6.01

```
HydroSovereign_HSAE_v601/
├── app.py                      Main router (1,322 lines · all 33 pages)
├── basins_global.py            26-basin registry — single source of truth
├── hsae_tdi.py                 ★ Canonical TDI/ATDI/AFSF (ε=0.001 · α=0.30)
│
├── Satellite Data
│   ├── gee_connector.py        GEE parallel fetch — 7 sensors (ThreadPoolExecutor)
│   ├── gee_engine.py           GEE Python API — 8 sensors
│   ├── hsae_gee_data.py        GEE scripts + 5 live APIs + parsers
│   ├── precompute_gee_daily.py GitHub Actions daily GEE precompute
│   ├── gee_realtime_reader.py  Read precomputed JSON cache
│   ├── grace_fo.py             GRACE-FO TWS anomaly (NASA Earthdata)
│   ├── smap_loader.py          SMAP L4 soil moisture
│   ├── glofas_loader.py        GloFAS ERA5 v4 30-day discharge
│   └── grdc_loader.py          GRDC 43-station discharge (1,257 lines)
│
├── Scientific Core
│   ├── hsae_hbv.py             HBV-96 catchment model + GRDC upload + SCE-UA
│   ├── hbv_model.py            HBV standalone + SCE-UA calibration
│   ├── hsae_science.py         Water balance + Figure 3 + basin-specific metrics
│   ├── hsae_validation.py      NSE/KGE/RMSE + GRDC upload + Taylor diagrams
│   ├── uncertainty_engine.py   Monte Carlo (10K samples) + bootstrap
│   ├── sensitivity_analysis.py OAT + Morris + Sobol indices
│   ├── sediment_transport.py   MUSLE + Brune trap + DCDI
│   ├── hsae_groundwater.py     MODFLOW + FAO-56 + Muskingum (GEE→GRDC→Sim)
│   ├── hsae_quality.py         WQI — WHO 2017 + FAO-56 (GEE→GRDC→Sim)
│   └── hsae_v430.py            Hybrid DSS + ASCAF + AFSF
│
├── AI & Climate
│   ├── hsae_ai.py              RF+MLP+GBM + IsolationForest + forecast
│   ├── ai_ensemble.py          Extended ensemble models
│   ├── ai_forecast.py          Multi-step forecasting
│   ├── digital_twin.py         Ensemble Kalman Filter (EnKF) real-time assimilation
│   ├── climate_engine.py       SSP1–5 scenarios + IPCC AR6 params
│   ├── conflict_index.py       Composite conflict index (basin-specific all 26)
│   ├── negotiation_ai.py       GBM negotiation prediction (478 TFDD cases)
│   └── benchmark_comparison.py Peer tool comparison (WEAP/MIKE/HEC-HMS/SWAT+)
│
├── Legal & Diplomacy
│   ├── hsae_legal.py           UN 1997 Arts 5–33 + ICJ/PCA/ITLOS
│   ├── treaty_diff.py          ATCI treaty compliance scoring (15 treaties)
│   ├── icj_dossier.py          ICJ/PCA/ITLOS dossier auto-generation
│   └── case_study_gerd.py      GERD Phase I–III TDI evolution 2020–2023
│
├── Operations
│   ├── hsae_opsroom.py         ASI + ADTS + AWSRM + SITREP dashboard
│   ├── hsae_alerts.py          Telegram @HASE_Water_bot · 4-level alerts
│   ├── hsae_audit.py           SHA-256 audit chain
│   └── hsae_db.py              SQLite persistence
│
├── WebGIS
│   └── webgis_app.py           Leaflet WebGIS — 25+ fields per basin popup
│
├── QGIS Plugin (hsae_qgis/)    ← v6.0.1 FINAL
│   ├── plugin.py               13 tools + real-time dashboard panel
│   ├── basin_loader.py         Load 26 basins with ATDI/HIFD/NSE/KGE
│   ├── dashboard_panel.py      Dockable real-time QGIS panel
│   ├── export_tool.py          Shapefile / GeoJSON / CSV export
│   ├── tdi_visualiser.py       TDI graduated colour map
│   ├── legal_layer.py          UNWC risk overlay
│   ├── dialog_main.py          HSAE dashboard dialog
│   ├── hsae_processing_provider.py  Processing Toolbox provider
│   ├── basins_50.json          26 basins enriched (runoff_c, context, legal_arts)
│   └── algorithms/
│       ├── atdi_algorithm.py          ATDI Calculator
│       ├── hifd_algorithm.py          HIFD Calculator
│       ├── basin_report_algorithm.py  Basin Legal Report
│       ├── hbv_algorithm.py           HBV-96 Calibration (SCE-UA) ← NEW
│       └── comparison_algorithm.py    Multi-Basin Comparison ← NEW
│
├── Documentation (docs/)       ← NEW in v6.0.1
│   ├── index.md                Overview & quick start
│   ├── installation.md         Installation guide
│   ├── indices.md              Mathematical formulas
│   ├── api_reference.md        Module & function reference
│   ├── examples.md             7 working code examples
│   └── qgis_plugin.md          QGIS plugin documentation
│
├── Tests (tests/)
│   ├── test_hsae.py            37 tests · 8 classes ← EXPANDED
│   ├── test_core.py            Core index tests
│   └── test_group_z_api.py     API tests
│
└── Configuration
    ├── requirements.txt
    ├── CITATION.cff
    ├── paper.md / paper.bib
    ├── CONTRIBUTING.md
    ├── INSTALL.md
    ├── Dockerfile / docker-compose.yml
    ├── .github/workflows/tests.yml      ← CI/CD
    ├── .github/workflows/daily_gee.yml  ← Daily GEE precompute
    └── LICENSE
```

---

## 🔌 QGIS Plugin — HydroSovereign Toolkit v6.01 FINAL

[![Download QGIS Plugin FINAL](https://img.shields.io/badge/⬇️_Download-HSAE_v601_QGIS_Plugin_FINAL.zip-589632?style=for-the-badge&logo=qgis&logoColor=white)](https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601/blob/main/HSAE_v601_QGIS_Plugin_FINAL.zip)

**Installation:** QGIS → Plugins → Manage → Install from ZIP → select `HSAE_v601_QGIS_Plugin_FINAL.zip`

### Tools (13)

| # | Tool | Description |
|---|------|-------------|
| 1 | 🌊 Load Basin Registry | 26 basins as point layer with ATDI/HIFD/NSE/KGE |
| 2 | 📊 TDI/ATDI Visualiser | Graduated colour map by ATDI level |
| 3 | ⚖️ UNWC Legal Layer | UN 1997 legal risk overlay |
| 4 | 📤 Export Basin Data | Shapefile / GeoJSON / CSV |
| 5 | 📋 Dashboard Dialog | Main HSAE analysis dashboard |
| 6 | 🛰️ GEE Script Generator | Ready-to-use scripts for 7 satellite sensors |
| 7 | 📡 GRDC Stations | 10 global discharge stations overlay |
| 8 | ⚡ Conflict Index | ATDI/HIFD CI for all 26 basins (TFDD/ICOW) |
| 9 | 🤝 Negotiation AI | P(success) from GBM model (478 historical cases) |
| 10 | 🗺️ WebGIS Map | Standalone Leaflet HTML map — 25+ fields |
| 11 | 📊 Basin Panel | Dockable real-time dashboard in QGIS |
| 12 | 🏛️ ICJ/PCA Dossier | Complete legal dossier export (TXT + HTML) |
| 13 | ℹ️ About | Author · DOI · GitHub · Live App |

### Processing Algorithms (5)

| Algorithm | QGIS ID | Inputs | Outputs |
|-----------|---------|--------|---------|
| ATDI Calculator | `atdi:atdicalculator` | rc, cap, nc, disp | ATDI% |
| HIFD Calculator | `atdi:hifdcalculator` | rc, cap, nc, disp | HIFD% |
| Basin Legal Report | `atdi:basinreport` | basin parameters | TXT report |
| HBV-96 Calibration | `atdi:hbv96calibration` | area, rc, P, T | NSE, KGE, CSV |
| Multi-Basin Comparison | `atdi:multibasincomparison` | basin names | CSV + HTML |

---

## 🛰️ GEE & Data Workflow

```
Direct GEE Mode
├── GPM IMERG V07      → P_mm_day     (11 km · daily)
├── GRACE-FO MASCON    → tws_cm       (300 km · monthly)
├── SMAP 10km          → sm_m3m3      (10 km · daily)
├── Sentinel-1 SAR     → flood extent (10 m · per event)
├── Sentinel-2 NDWI    → water mask   (10 m · bi-weekly)
├── GloFAS ERA5 v4     → Q_m3s        (0.1° · daily)
└── Open-Meteo ERA5    → T_C, ET0     (daily)
         ↓
session_state → all 33 pages read live data
         ↓
Figure 3 · WebGIS · Conflict Index · Negotiation AI
```

```bash
# GEE Authentication
earthengine authenticate
# or Service Account:
export GEE_SA_KEY_PATH=hsae-gee-service.json
```

---

## 🔬 Key Metrics

| Metric | Value | Status |
|--------|-------|--------|
| NSE (pre-calibration) | 0.63 | Blue Nile GERD 2025 |
| KGE (pre-calibration) | 0.74 | Blue Nile GERD 2025 |
| ATDI Blue Nile GERD | 49.2% | Art.7 zone |
| HIFD Blue Nile GERD | 33.4% | Art.20 triggered |
| P(Negotiation) GERD | 37% | ICJ/PCA recommended |
| GEE data latency | <2 sec | 24-hr cache |
| pytest tests | 37 passing | CI/CD verified |

---

## 📦 Zenodo — Datasets & Releases

[![Zenodo](https://img.shields.io/badge/Zenodo-All%20Records-1682D4?style=for-the-badge&logo=zenodo&logoColor=white)](https://zenodo.org/search?q=0000-0003-0821-2991)

| Release | Tag | Date | Contents |
|---------|-----|------|----------|
| HSAE v6.0.1 | v6.0.1 | Apr 2026 | QGIS FINAL + docs + 37 tests |
| HSAE v6.01 | v6.01.0 | Mar 2026 | Complete scientific release |

---

## 📚 Documentation

| Document | Link |
|----------|------|
| Installation Guide | [docs/installation.md](docs/installation.md) |
| API Reference | [docs/api_reference.md](docs/api_reference.md) |
| HSAE Indices (formulas) | [docs/indices.md](docs/indices.md) |
| Examples | [docs/examples.md](docs/examples.md) |
| QGIS Plugin Docs | [docs/qgis_plugin.md](docs/qgis_plugin.md) |

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Output: 37 passed, 0 failed
```

Tests cover: ATDI · HIFD · NSE · KGE · Conflict Index · HBV-96 · Legal thresholds · Negotiation AI · Data validation

---

## 📖 Citation

```bibtex
@software{alkedir2026hsae,
  author    = {Alkedir, Seifeldin M.G.},
  title     = {{HydroSovereign AI Engine (HSAE) v6.01}},
  year      = {2026},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.19180160},
  url       = {https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601},
  orcid     = {0000-0003-0821-2991}
}
```

---

## 🎬 Demo

[![Live App](https://img.shields.io/badge/🌊_Launch_Live_App-HSAE_v6.01-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://hydrosovereign-ai-engine-hsae-v601-6euz2zxcmerkzxgordmvxf.streamlit.app)
[![YouTube](https://img.shields.io/badge/▶_Watch_Full_Demo-YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@seifeldinalkedir)

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0** — see [LICENSE](LICENSE) for details.

---

<div align="center">

[![ORCID](https://img.shields.io/badge/ORCID-0000--0003--0821--2991-a6ce39?style=flat&logo=orcid&logoColor=white)](https://orcid.org/0000-0003-0821-2991)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19180160.svg)](https://doi.org/10.5281/zenodo.19180160)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/seifelden-alkhedir-6b730985/)
[![Zenodo](https://img.shields.io/badge/Zenodo-Records-1682D4?style=flat&logo=zenodo&logoColor=white)](https://zenodo.org/search?q=0000-0003-0821-2991)
[![YouTube](https://img.shields.io/badge/YouTube-Channel-FF0000?style=flat&logo=youtube&logoColor=white)](https://www.youtube.com/@seifeldinalkedir)
[![QGIS](https://img.shields.io/badge/QGIS-Plugin-589632?style=flat&logo=qgis&logoColor=white)](https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601/tree/main/hsae_qgis)
[![Live App](https://img.shields.io/badge/Live_App-Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://hydrosovereign-ai-engine-hsae-v601-6euz2zxcmerkzxgordmvxf.streamlit.app)

*HydroSovereign AI Engine v6.01 · Seifeldin M.G. Alkedir · University of Khartoum · 2026*

</div>