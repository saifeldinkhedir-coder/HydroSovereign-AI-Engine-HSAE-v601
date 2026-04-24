# 🌊 HydroSovereign AI Engine — QGIS Plugin v6.01

<div align="center">

[![QGIS Plugin](https://img.shields.io/badge/QGIS_Plugin-ID_5040-589632?style=for-the-badge&logo=qgis&logoColor=white)](https://plugins.qgis.org/plugins/hsae_qgis/)
[![PyPI](https://img.shields.io/badge/PyPI-hydrosovereign_v6.5.3-3775A9?style=for-the-badge&logo=pypi&logoColor=white)](https://pypi.org/project/hydrosovereign/)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.19180160-1682D4?style=for-the-badge&logo=zenodo&logoColor=white)](https://doi.org/10.5281/zenodo.19180160)
[![SoftwareX](https://img.shields.io/badge/SoftwareX-SOFTX--D--26--00442-005A8E?style=for-the-badge)](https://doi.org/10.5281/zenodo.19180160)
[![License](https://img.shields.io/badge/License-GPL_3.0-blue?style=for-the-badge)](https://www.gnu.org/licenses/gpl-3.0)
[![Security](https://img.shields.io/badge/Security_Scan-0_Critical-brightgreen?style=for-the-badge)](https://plugins.qgis.org/plugins/hsae_qgis/)
[![QGIS](https://img.shields.io/badge/QGIS-≥_3.16_LTR-589632?style=flat&logo=qgis&logoColor=white)](https://qgis.org)

**Author:** Seifeldin M.G. Alkedir · [ORCID 0000-0003-0821-2991](https://orcid.org/0000-0003-0821-2991) · University of Khartoum

</div>

---

## 🔗 Quick Links

| Resource | Link |
|----------|------|
| 🔌 **QGIS Plugin Repository** | [plugins.qgis.org/plugins/hsae_qgis/](https://plugins.qgis.org/plugins/hsae_qgis/) — Plugin ID: **5040** |
| 🌐 **Live Streamlit App** | [HSAE v6.01 on Streamlit](https://hydrosovereign-ai-engine-hsae-v601-6euz2zxcmerkzxgordmvxf.streamlit.app) |
| 🐍 **Python Package** | [pypi.org/project/hydrosovereign/](https://pypi.org/project/hydrosovereign/) — `pip install hydrosovereign` |
| 📦 **GitHub (Main App)** | [HydroSovereign-AI-Engine-HSAE-v601](https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601) |
| 🏛️ **Zenodo DOI** | [10.5281/zenodo.19180160](https://doi.org/10.5281/zenodo.19180160) |
| 📄 **SoftwareX Paper** | SOFTX-D-26-00442 — Under Review 2026 |
| 🐛 **Bug Reports** | [GitHub Issues](https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601/issues) |

---

## 📖 Documentation & Manual

| Format | Download | Size | Contents |
|--------|----------|------|----------|
| 📕 **PDF Manual v5** | [⬇️ Download PDF](https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601/raw/main/hsae_qgis/HSAE_v601_QGIS_Plugin_Manual_v5.pdf) | ~830 KB | Complete guide — 13 chapters + 5 appendices |
| 📘 **DOCX Manual v5** | [⬇️ Download DOCX](https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601/raw/main/hsae_qgis/HSAE_v601_QGIS_Plugin_Manual_v5.docx) | ~60 KB | Editable Word format |
| 🌐 **Online Viewer** | [View on GitHub](https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601/blob/main/hsae_qgis/HSAE_v601_QGIS_Plugin_Manual_v5.pdf) | — | Preview in browser |

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

## ⚙️ Installation

### Method 1 — QGIS Plugin Repository (Recommended ✅)
```
QGIS → Plugins → Manage and Install Plugins
     → Search: "HydroSovereign"
     → Click: Install Plugin
```
> Plugin ID: **5040** · Published: **April 21, 2026** · Security: **0 Critical · 0 Warnings · 76 files scanned**  
> Approved by: *zimbogisgeek (QGIS reviewer) · PR #289 — Tim Sutton, QGIS PSC*

### Method 2 — Install from ZIP
1. Download: [HSAE_v601_QGIS_Plugin_FINAL_v2.zip](https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601/raw/main/hsae_qgis/HSAE_v601_QGIS_Plugin_FINAL_v2.zip)
2. QGIS → Plugins → Manage and Install Plugins → **Install from ZIP** tab
3. Browse to the ZIP file → Install Plugin

> ⚠️ Internal folder must be `hsae_qgis/` — do not rename. **Method 1 is always preferred.**

---

## 🛠️ What the Plugin Provides

| Component | Count | Access |
|-----------|-------|--------|
| Toolbar Tools | **13 tools** | HydroSovereign AI Engine v6.01 menu + toolbar |
| Processing Algorithms | **5 algorithms** | Processing Toolbox → HydroSovereign AI Engine v6.01 |
| Basin Registry | **26 basins** | Built-in — 7 world regions |
| GEE Satellite Scripts | **7 sensors** | Tool 5 generates GEE JavaScript |
| GRDC Stations | **10 stations** | Tool 4 loads as point layer |

### 🧰 13 Tools at a Glance
| # | Tool | Purpose |
|---|------|---------|
| 1 | 🌊 Load Basin Registry | 26 basins on world map |
| 2 | 📊 TDI/ATDI Visualiser | Colour by ATDI risk level |
| 3 | ⚖️ UNWC Legal Layer | Treaty compliance mapping |
| 4 | 📡 GRDC Stations | Discharge monitoring overlay |
| 5 | 🛰️ GEE Script Generator | 7 satellite data scripts |
| 6 | 📋 Dashboard Dialog | Per-basin analysis |
| 7 | ⚡ Conflict Index | All 26 basins ranked |
| 8 | 🤝 Negotiation AI | P(success) prediction |
| 9 | 🗺️ WebGIS Map | Offline HTML map |
| 10 | 📤 Export Data | GeoJSON / SHP / CSV |
| 11 | 📊 Basin Panel | Dockable live dashboard |
| 12 | 🏛️ ICJ/PCA Dossier | Full legal dossier |
| 13 | ℹ️ About | Metadata + BibTeX |

---

## 📊 Key Scientific Results (Blue Nile / GERD)

| Index | Value | Interpretation |
|-------|-------|----------------|
| **ATDI** | **43.5%** | Article 7 UNWC No-Significant-Harm zone |
| **HIFD** | **20.0%** | 20% of natural downstream flow withheld |
| **NSE** | **0.63** | Satisfactory (proxy-validated vs GloFAS ERA5 v4) |
| **KGE** | **0.74** | Satisfactory |
| **CI** | **0.44 HIGH** | Conflict Index |
| **P(Negotiation)** | **58%** | Art. 17 Mediation recommended |

---

## 🔒 Security & Quality

- ✅ **Passed:** 4/5 checks
- ✅ **Critical issues:** 0
- ✅ **Warnings:** 0
- ✅ **Files scanned:** 76
- ✅ **Bandit security analysis:** 0 issues
- ✅ **Secrets detection:** 0 issues
- ✅ **File permissions:** 0 issues

---

## 📝 Citation

```bibtex
@software{alkedir2026hsae,
  author    = {Alkedir, Seifeldin M.G.},
  title     = {{HydroSovereign AI Engine (HSAE) v6.01}},
  year      = {2026},
  publisher = {QGIS Plugin Repository + PyPI + Zenodo},
  version   = {6.0.1},
  note      = {QGIS Plugin ID: 5040. SoftwareX SOFTX-D-26-00442.},
  url       = {https://plugins.qgis.org/plugins/hsae_qgis/},
  doi       = {10.5281/zenodo.19180160},
  orcid     = {0000-0003-0821-2991}
}
```

---

*Plugin ID: 5040 · GPL-3.0 · April 21, 2026 · Seifeldin M.G. Alkedir*
