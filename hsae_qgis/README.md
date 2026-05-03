# 🌊 HydroSovereign AI Engine — QGIS Plugin v6.0.6

<div align="center">

[![Version](https://img.shields.io/badge/Version-6.0.6-orange?style=for-the-badge)](https://plugins.qgis.org/plugins/hsae_qgis/)
[![QGIS Plugin](https://img.shields.io/badge/QGIS_Plugin-ID_5040-589632?style=for-the-badge)](https://plugins.qgis.org/plugins/hsae_qgis/)
[![Downloads](https://img.shields.io/badge/Downloads-73%2B-brightgreen?style=for-the-badge)](https://plugins.qgis.org/plugins/hsae_qgis/)
[![Countries](https://img.shields.io/badge/Countries-16_%C2%B7_5_Continents-blue?style=for-the-badge)](https://plugins.qgis.org/plugins/hsae_qgis/)
[![PyPI](https://img.shields.io/badge/PyPI-hydrosovereign-3775A9?style=for-the-badge&logo=pypi&logoColor=white)](https://pypi.org/project/hydrosovereign/)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.19180160-1682D4?style=for-the-badge)](https://doi.org/10.5281/zenodo.19180160)
[![SoftwareX](https://img.shields.io/badge/SoftwareX-SOFTX--D--26--00442_Under_Review-005A8E?style=for-the-badge)](https://www.sciencedirect.com/journal/softwarex)
[![License](https://img.shields.io/badge/License-GPL_3.0-blue?style=for-the-badge)](https://www.gnu.org/licenses/gpl-3.0)
[![Security](https://img.shields.io/badge/Security_Scan-0_Critical-brightgreen?style=for-the-badge)](https://plugins.qgis.org/plugins/hsae_qgis/)
[![QGIS](https://img.shields.io/badge/QGIS-%E2%89%A5_3.16_LTR-589632?style=flat)](https://qgis.org)

**Author:** Seifeldin M.G. Alkhedir · [ORCID 0000-0003-0821-2991](https://orcid.org/0000-0003-0821-2991) · University of Khartoum

> *The first open-source platform to automate the complete pipeline from live satellite observation to international water law compliance — in under 2 minutes per basin.*

</div>

---

## 🔗 Quick Links

| Resource | Link |
|----------|------|
| 🔌 **QGIS Plugin Repository** | [plugins.qgis.org/plugins/hsae_qgis/](https://plugins.qgis.org/plugins/hsae_qgis/) — Plugin ID: **5040** |
| 🌐 **Live Streamlit App** | [HSAE v6.0.6 on Streamlit Cloud](https://hydrosovereign-ai-engine-hsae-v601-6euz2zxcmerkzxgordmvxf.streamlit.app) |
| 🐍 **Python Package** | [pypi.org/project/hydrosovereign/](https://pypi.org/project/hydrosovereign/) — `pip install hydrosovereign` |
| 📦 **GitHub (Main Repo)** | [HydroSovereign-AI-Engine-HSAE-v601](https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601) |
| 🏛️ **Zenodo DOI** | [10.5281/zenodo.19180160](https://doi.org/10.5281/zenodo.19180160) |
| 📄 **SoftwareX Paper** | SOFTX-D-26-00442 — **Confirmed Under Peer Review — April 2026** |
| 📘 **Manual v6** | [Download DOCX (15 chapters)](https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601/raw/main/hsae_qgis/HSAE_v601_QGIS_Plugin_Manual_v6.docx) |
| 🐛 **Bug Reports** | [GitHub Issues](https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601/issues) |

---

## 📊 Live Statistics — April 26, 2026

```
73+ Downloads  ·  16 Countries  ·  5 Continents  ·  2 Rating Votes
Plugin ID: 5040  ·  Version: 6.0.6  ·  Security: 0 Critical · 0 Warnings
SoftwareX SOFTX-D-26-00442 — Confirmed Under Peer Review
```

**Download geography:** 🇺🇸 USA (30) · 🇮🇩 Indonesia (3) · 🇧🇷 Brazil (2) · 🇫🇮 Finland (2) · 🇸🇦 Saudi Arabia (2) · 🇪🇹 **Ethiopia** (1 — GERD upstream) · 🇫🇷 France · 🇬🇧 UK · 🇨🇳 China · 🇲🇦 Morocco · 🇮🇹 Italy · 🇵🇱 Poland · 🇪🇸 Spain · 🇸🇬 Singapore · 🇲🇽 Mexico · 🇵🇫 French Polynesia

---

## ⚙️ Installation

### Method 1 — QGIS Plugin Repository (Recommended ✅)
```
QGIS → Plugins → Manage and Install Plugins
     → Search: "HydroSovereign"
     → Click: Install Plugin
```
> Plugin ID: **5040** · Published: **April 21, 2026** · Security: **0 Critical · 0 Warnings**
> Approved by: *zimbogisgeek (QGIS reviewer) · PR #289 reviewed by Tim Sutton (QGIS PSC)*

### Method 2 — Install from ZIP
1. Download: [HSAE_v606_QGIS_Plugin.zip](https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601/raw/main/hsae_qgis/HSAE_v606_QGIS_Plugin.zip)
2. QGIS → Plugins → Manage and Install Plugins → **Install from ZIP** tab
3. Browse to the ZIP file → Install Plugin

> ⚠️ Internal folder must be `hsae_qgis/` — do not rename. **Method 1 is always preferred.**

---

## 🛠️ What the Plugin Provides

| Component | Count | Access |
|-----------|-------|--------|
| **Tools** | **15 tools** | HydroSovereign AI Engine v6.0.6 menu + toolbar |
| **Processing Algorithms** | **5 algorithms** | Processing Toolbox → HydroSovereign AI Engine |
| **Basin Registry** | **26 basins** | Built-in — 7 world regions · all continents |
| **GEE Satellite Sensors** | **9 sensors** | GPM IMERG · GRACE-FO · SMAP · Sentinel-1/2 · ERA5 · Open-Meteo · MODIS · VIIRS |
| **Original Indices** | **6 indices** | ATDI · HIFD · AFSF · AHLB · ASI · ATCI |

---

## 🧰 15 Tools — Complete Reference

| # | Tool | Purpose | Toolbar |
|---|------|---------|---------|
| 1 | 🌊 Load Basin Registry | Load 26 transboundary basins as point layer | ✅ |
| 2 | 📊 TDI/ATDI Visualiser | Apply ATDI graduated colour risk map | ✅ |
| 3 | ⚖️ UNWC Legal Layer | UN 1997 UNWC legal risk overlay | ✅ |
| 4 | 📤 Export Basin Data | Export to Shapefile / GeoJSON / CSV | ✅ |
| 5 | 📋 Dashboard Dialog | Open HSAE main analysis dashboard | ✅ |
| 6 | 🛰️ GEE Scripts (7 sensors) | Generate GEE JavaScript for 7 satellite sensors | ✅ |
| 7 | 📡 GRDC Stations | Load GRDC discharge monitoring stations | ✅ |
| 8 | ⚡ Conflict Index | Compute CI for all 26 basins (TFDD/ICOW) | ✅ |
| 9 | 🤝 Negotiation AI | P(success) prediction — GBM model (478 cases) | ✅ |
| 10 | 🗺️ WebGIS Map v2 | Interactive Leaflet map with Search · Layer Toggle · Risk Filter · Rankings | ✅ |
| 11 | 📊 Basin Panel | Dockable real-time dashboard panel | ✅ |
| 12 | 🏛️ ICJ/PCA Dossier | Export complete legal dossier (SHA-256 chain) | Menu |
| 13 | 🗺️ Basin Risk Map | Interactive Leaflet.js basin map **inside QGIS Desktop** | ✅ |
| 14 | 📉 Uncertainty Analysis | Bayesian CI + Monte Carlo (n=500) + Sobol sensitivity | ✅ |
| 15 | ⚖️ Treaty Analysis (ATCI) | Alkhedir Treaty Compliance Index — all 10 UNWC articles | ✅ |

---

## ⚙️ 5 Processing Algorithms (QGIS Toolbox)

| # | Algorithm | Description |
|---|-----------|-------------|
| 1 | 📐 **ATDI Calculator** | Compute Alkhedir Transparency Deficit Index for any basin |
| 2 | 📐 **HIFD Calculator** | Compute Human-Induced Flow Deficit |
| 3 | 📋 **Basin Legal Report** | Generate full UNWC compliance report as PDF/HTML |
| 4 | ⚙️ **HBV-96 Calibration** | SCE-UA calibration of HBV-96 model — outputs NSE/KGE |
| 5 | 🔄 **Multi-Basin Comparison** | Batch-process and compare all 26 basins simultaneously |

> Processing Algorithms support **Batch Mode**, **Graphical Modeler**, and **Python Console** — enabling automated large-scale analysis workflows.

---

## 📊 Key Scientific Results — Blue Nile (GERD) Primary Case Study

| Index | Value | Interpretation |
|-------|-------|----------------|
| **ATDI** | **43.5%** | Article 7 UNWC No-Significant-Harm zone |
| **HIFD** | **20.0%** | 20% of natural downstream flow withheld |
| **NSE** | **0.63** | Satisfactory (proxy-validated vs GloFAS ERA5 v4) |
| **KGE** | **0.74** | Satisfactory |
| **CI** | **0.44 HIGH** | Conflict Index |
| **P(Negotiation)** | **58%** | Article 17 Mediation recommended |
| **ATCI** | **70%** | 7 of 10 UNWC articles triggered |

> NSE = 0.63 is pre-calibration (proxy validation). Ground-truth calibration targeting NSE ≥ 0.70 pending GRDC data (Request ID 78949, El Diem station, 174,000 km²).

---

## 🛰️ 9 GEE Satellite Sensors

| Sensor | Variable | Resolution | Update |
|--------|----------|------------|--------|
| **GPM IMERG V07** | Precipitation | 0.1° | Daily |
| **GRACE-FO MASCON RL06v4** | Terrestrial Water Storage | 0.5° | Monthly |
| **SMAP SPL3SMP** | Soil Moisture | 36 km | Daily |
| **Sentinel-1 GRD** | SAR / Flood extent | 10 m | ~12 days |
| **Sentinel-2 SR** | NDWI / NDVI | 10 m | ~5 days |
| **GloFAS ERA5 v4** | River discharge (proxy) | — | Daily |
| **Open-Meteo** | T · P · ET0 · SM | ~1 km | Hourly |
| **MODIS MOD16A2** | Evapotranspiration | 500 m | 8-day |
| **VIIRS Night Lights** | Economic activity proxy | 500 m | Monthly |

---

## 🔬 6 Original Scientific Indices

| Index | Full Name | Description |
|-------|-----------|-------------|
| **ATDI** | Alkhedir Transparency Deficit Index | Daily satellite-based Art.7 UNWC compliance |
| **HIFD** | Human-Induced Flow Deficit | Annual volumetric downstream flow reduction |
| **AFSF** | Alkhedir Forensic Signal Factor | Anthropogenic vs natural signal separator |
| **AHLB** | Alkhedir HBV-Legal Bridge | HBV-96 physics → UNWC article flags |
| **ASI** | Alkhedir Sovereignty Index | Composite water governance metric |
| **ATCI** | Alkhedir Treaty Compliance Index | Triggered UNWC articles / total × 100% |

---

## 🗺️ 26 Global River Basins

Covers all 7 world regions across all inhabited continents:

**Africa:** Nile · Blue Nile · White Nile · Congo · Niger · Zambezi · Orange · Senegal
**Asia:** Mekong · Indus · Brahmaputra · Euphrates · Tigris · Jordan · Amu Darya · Ganges
**Europe:** Danube · Rhine · Dnieper
**Americas:** Amazon · Colorado · Columbia · Río de la Plata
**Middle East / Central Asia:** Helmand · Kura-Araks
**Oceania:** Murray-Darling

> The architecture is **fully generalisable**: any river basin in the world can be added by providing basin area, dam capacity, and riparian state count. All 9 satellite pipelines activate immediately.

---

## 📖 Manual v6 — 15 Chapters + 5 Appendices

| Chapter | Contents |
|---------|----------|
| Ch. 1–3 | Introduction · Installation · Quick Start |
| Ch. 4–10 | Tools 1–13 — complete step-by-step guides |
| Ch. 11 | QGIS Desktop operating guide |
| Ch. 12 | Advanced: Model Builder · Batch Processing · Python API |
| Ch. 13 | Case Study 2 — Mekong Basin (Xayaburi Dam) |
| Ch. 14 | Tools 14/15/16 — Leaflet · Uncertainty · Treaty ATCI |
| Ch. 15 | Error Codes · Troubleshooting · FAQ |
| App. A–E | Equations Index · Legal Disclaimers · Changelog · Arabic Quick Start · Keyword Index |

📥 **[Download Manual v6 DOCX](https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601/raw/main/hsae_qgis/HSAE_v601_QGIS_Plugin_Manual_v6.docx)** — 15 chapters · 5 appendices · 2,702 paragraphs

---

## 🔒 Security & Quality

| Check | Result |
|-------|--------|
| Critical issues | ✅ **0** |
| Warnings | ✅ **0** |
| Files scanned | ✅ **76** |
| Bandit security analysis | ✅ **0 issues** |
| Secrets detection | ✅ **0 issues** |
| File permissions | ✅ **0 issues** |
| Python syntax (20 files) | ✅ **0 errors** |
| Flake8 issues | ✅ **< 400** (down from 1,220) |

---

## 📚 Publication Status

| Status | Publication |
|--------|-------------|
| 🔄 **Under Review** | **Elsevier SoftwareX** — SOFTX-D-26-00442 — Confirmed under peer review April 26, 2026 |
| 📝 **In Preparation** | **JOSS** — Journal of Open Source Software |
| ✅ **Published** | **Zenodo** — DOI: [10.5281/zenodo.19180160](https://doi.org/10.5281/zenodo.19180160) |
| ✅ **Published** | **QGIS Plugin Repository** — Plugin ID: 5040 · v6.0.6 |
| ✅ **Published** | **PyPI** — [hydrosovereign](https://pypi.org/project/hydrosovereign/) |
| 📋 **Planned** | **Water Resources Research** (IF 5.4) — pending GRDC data |
| 📋 **Planned** | **Nature Water** (IF 13.2) — pending NSE ≥ 0.70 calibration |

---

## 📝 Citation

```bibtex
@software{alkedir2026hsae,
  author    = {Alkhedir, Seifeldin M.G.},
  title     = {{HydroSovereign AI Engine (HSAE) v6.0.6:
                An Open-Source Satellite and AI Platform
                for Transboundary Water Sovereignty Analysis}},
  year      = {2026},
  publisher = {QGIS Plugin Repository · PyPI · Zenodo},
  version   = {6.0.6},
  note      = {QGIS Plugin ID: 5040.
                SoftwareX SOFTX-D-26-00442 under review.
                73+ downloads · 16 countries · 5 continents.},
  url       = {https://plugins.qgis.org/plugins/hsae_qgis/},
  doi       = {10.5281/zenodo.19180160},
  orcid     = {0000-0003-0821-2991}
}
```

---

## 📋 Version History

| Version | Date | Key Changes |
|---------|------|-------------|
| **v6.0.6** | April 26, 2026 | Version strings fix · Tools 14/15/16 in toolbar · About: 15 Tools + 5 Algorithms |
| **v6.0.5** | April 25, 2026 | Description fix · No "pc" abbreviation · Metadata restructured |
| **v6.0.4** | April 24, 2026 | WebGIS Map v2 · Flake8: 1,220→389 issues · 8 unused imports removed |
| **v6.0.3** | April 23, 2026 | Tool 14 (Leaflet in QGIS) · Tool 15 (Uncertainty+Sobol) · Tool 16 (Treaty ATCI) · Manual v6 |
| **v6.0.1** | April 21, 2026 | First publication · Plugin ID 5040 · 0 Critical · 0 Warnings · SoftwareX submitted |

---

*Plugin ID: 5040 · GPL-3.0 · April 2026 · Seifeldin M.G. Alkhedir · University of Khartoum*
*ORCID: [0000-0003-0821-2991](https://orcid.org/0000-0003-0821-2991) · DOI: [10.5281/zenodo.19180160](https://doi.org/10.5281/zenodo.19180160)*
