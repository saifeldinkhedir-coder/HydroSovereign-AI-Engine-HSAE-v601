# HydroSovereign AI Engine (HSAE)

<div align="center">

[![PyPI version](https://img.shields.io/pypi/v/hydrosovereign?style=for-the-badge&color=3775A9&logo=pypi&logoColor=white)](https://pypi.org/project/hydrosovereign/)
[![PyPI downloads](https://img.shields.io/pypi/dm/hydrosovereign?style=for-the-badge&color=3775A9)](https://pypi.org/project/hydrosovereign/)
[![Python](https://img.shields.io/pypi/pyversions/hydrosovereign?style=for-the-badge&logo=python&logoColor=white)](https://pypi.org/project/hydrosovereign/)
[![CI](https://img.shields.io/github/actions/workflow/status/saifeldinkhedir-coder/hydrosovereign/ci_publish.yml?style=for-the-badge&label=CI&logo=githubactions&logoColor=white)](https://github.com/saifeldinkhedir-coder/hydrosovereign/actions)
[![QGIS Plugin](https://img.shields.io/badge/QGIS_Plugin-ID_5040-589632?style=for-the-badge&logo=qgis&logoColor=white)](https://plugins.qgis.org/plugins/hsae_qgis/)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.19180160-1682D4?style=for-the-badge&logo=zenodo&logoColor=white)](https://doi.org/10.5281/zenodo.19180160)
[![Preprint](https://img.shields.io/badge/Preprint-SSRN_6661396-B31B1B?style=for-the-badge)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6661396)
[![License](https://img.shields.io/github/license/saifeldinkhedir-coder/hydrosovereign?style=for-the-badge)](LICENSE)
[![ORCID](https://img.shields.io/badge/ORCID-0000--0003--0821--2991-a6ce39?style=for-the-badge&logo=orcid&logoColor=white)](https://orcid.org/0000-0003-0821-2991)

**HSAE automates the full pipeline from live satellite observation to international water law compliance — in under 2 minutes per basin.**

> 362+ downloads · 20 countries · 5 continents · 100% QGIS security scan · GeoAgent AI · eWaterCycle BMI

</div>

## ⚠️ v6.8.1 — Major Scientific Revision (read before upgrading)

Version 6.8.1 rebuilds the index engine on a **provenance-bound** foundation. This is the most important change in the project's history and it changes how you call the indices.

### What changed and why

The earlier index formulas combined incommensurable quantities (storage in BCM, an ordinal dispute level, a country count, a dimensionless runoff coefficient) behind undocumented constants, and produced values even when no real observations existed. Following external scientific review, the engine now:

1. **Computes only from documented observations.** Every value carries provenance (source, reference, dates, quality). When the required observed data are absent, functions return `INSUFFICIENT_DATA` instead of a fabricated number.
2. **Fixes the indices.** `HIFD` now takes independent `Q_nat` and `Q_obs` (it no longer algebraically collapses to a constant). `ATDI` is the empirical mean of per-period TDI, matching the published equations.
3. **Separates empirical from normative.** Empirical measures (TDI, ATDI, HIFD, AFSF, AHLB) are distinct from declared normative composites (ASI, ATCI, AWGI), which expose explicit weights and sensitivity analysis.
4. **Trains the model for real.** `TreatyClassifier` is genuinely trained on the TFDD treaties database with an honest model card (F1, ROC-AUC, cross-validation, baseline).
5. **Validates independently.** `validate_model_skill` rejects any benchmark that shares the model's own forcing.

### Index reference (v6.8.1)

| Index | Kind | Inputs |
|-------|------|--------|
| `compute_tdi` | empirical | observed inflow, outflow |
| `compute_atdi` | empirical | observed inflow/outflow series |
| `compute_hifd` | empirical | independent observed Q_nat, Q_obs |
| `compute_afsf` | empirical | observed/natural anomaly, range |
| `compute_ahlb` | empirical | paired q_sim, q_obs (NSE) |
| `compute_asi` | normative | equity, cooperation, data-sharing (weighted) |
| `compute_atci` | normative | per-article compliance postures (weighted) |
| `compute_awgi` | normative | transparency, dispute, riparians, regulation |
| `correlation_matrix` | disclosure | cross-basin index values |

### Migrating from the old API

The previous heuristic functions remain available in `hydrosovereign.indices_legacy`, but they emit a `DeprecationWarning` and **will be removed in v7.0.0**:

```python
# old (deprecated, unvalidated):
from hydrosovereign.indices_legacy import compute_atdi
compute_atdi(runoff_c, cap_bcm, n_countries, dispute_level)

# new (provenance-based):
from hydrosovereign import compute_atdi, DataPoint, DataQuality
compute_atdi(inflow_series, outflow_series)   # observed DataPoints
```

---


---

## 📋 Table of Contents

- [What is HSAE?](#-what-is-hsae)
- [Six Original Scientific Indices (AWSI)](#-six-original-scientific-indices-awsi)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [26-Basin Coverage](#-26-basin-coverage)
- [Key Results](#-key-results)
- [Architecture](#-architecture)
- [CLI Usage](#-cli-usage)
- [Comparison with Alternatives](#-comparison-with-alternatives)
- [Citation](#-citation)
- [Links](#-links)

---

## 🌊 What is HSAE?

**HydroSovereign AI Engine (HSAE)** is a Python package and QGIS plugin for automated transboundary water law compliance assessment. It combines:

- **9 satellite sensors** via Google Earth Engine (GPM, GRACE-FO, SMAP, Sentinel-1/2, ERA5, GloFAS, Open-Meteo, MODIS, VIIRS)
- **HBV-96 hydrological model** with SCE-UA calibration and EnKF digital twin
- **6 original compliance indices** (the Alkhedir Water Sovereignty Indices — AWSI)
- **Treaty-feature classifier** genuinely trained on the TFDD treaties database (429 labelled treaties); honest model card (F1, ROC-AUC, CV, baseline). It classifies a documented treaty property — not negotiation success/failure
- **UNWC 1997** article-by-article trigger logic (Arts. 5, 7, 9, 11, 17, 33)
- **eWaterCycle BMI** compatible — integrates with the open-science hydrological platform
- **GeoAgent AI** — natural language queries inside QGIS (opengeos/GeoAgent PR #79)

Covers **26 globally contested transboundary basins** across 7 world regions. Model skill is assessed only against benchmarks that are independent of the model's own forcing; `validate_model_skill` rejects a benchmark that shares the model forcing (see the v6.8.1 revision).

---

## 🔬 Six Original Scientific Indices (AWSI)

The **Alkhedir Water Sovereignty Indices (AWSI)** are the first published quantitative framework connecting hydrological model outputs to UNWC 1997 article triggers:

| Index | Full Name | Legal Trigger | Illustrative value |
|-------|-----------|---------------|-------------|
| **ATDI** | Alkhedir Transparency Deficit Index | Art. 7 — No Significant Harm (≥40%) | **43.6%** ⚠️ |
| **AHIFD** | Alkhedir Human-Induced Flow Deficit | Art. 7 — volumetric downstream harm | **19.7%** |
| **AFSF** | Alkhedir Forensic Signal Factor | Art. 9 — data exchange obligation | 0.36 |
| **AHLB** | Alkhedir HBV-Legal Bridge | Arts. 5,6,7 — HBV-96 → legal triggers | 0.436 |
| **ASI** | Alkhedir Sovereignty Index | Art. 5 — equitable utilisation | 0.64 |
| **ATCI** | Alkhedir Treaty Compliance Index | Arts. 5,7,9,11,17,33 composite | **70/100** |

The six indices are collectively named **AWSI**. The values shown in the tables below are *illustrative outputs* of the framework, not validated field measurements: legally-relevant indices require observation-grade discharge data (see the v6.8.1 provenance model). Independent model-skill validation against a benchmark that does not share the model's forcing is pending real observed records (GRDC request in progress).

---

## ⚙️ Installation

```bash
# Minimal install
pip install hydrosovereign

# With Google Earth Engine
pip install hydrosovereign[gee]

# With visualisation (Plotly, Folium, Matplotlib)
pip install hydrosovereign[viz]

# With Jupyter notebook support
pip install hydrosovereign[jupyter]

# Everything
pip install hydrosovereign[full]
```

**Requirements:** Python ≥ 3.9 · NumPy · Pandas · SciPy · scikit-learn · Requests

---

## 🚀 Quick Start

```python
from hydrosovereign import (
    DataPoint, DataQuality, DataRegistry, hifd_for_basin,
)

# The engine computes ONLY from documented observations. Anyone holding
# real, sourced data contributes it to an auditable registry.
reg = DataRegistry()
reg.submit("GERD", DataPoint(
    value=1248.0, variable="Q_obs", unit="m3/s",
    source="GRDC station 1577100 (El Diem)",
    source_ref="https://grdc.bafg.de/  (request 78949)",
    date_start="2010-01-01", date_end="2020-12-31",
    quality=DataQuality.OBSERVED), contributor="Researcher A, ORCID ...")

# Without an independent observed Q_nat this returns INSUFFICIENT_DATA —
# never a fabricated number.
result = hifd_for_basin(reg, "GERD")
print(result.status, result.value)   # INSUFFICIENT_DATA  None
# ...once an independent observed Q_nat is also submitted, HIFD is
# computed from the real Eq.6 and carries its full provenance.

# Legacy heuristic functions still exist but are DEPRECATED:
#   from hydrosovereign.indices_legacy import compute_atdi   # warns; removed in v7.0.0
```

---

## 🌍 26-Basin Coverage

HSAE covers **26 globally contested transboundary basins** across 7 world regions:

| Region | Basins |
|--------|--------|
| 🌍 **Africa** | Blue Nile (GERD) · Nile-Roseires · Nile-Aswan · Zambezi-Kariba · Congo-Inga · Niger-Kainji |
| 🌏 **Middle East** | Euphrates-Atatürk · Tigris-Mosul |
| 🌏 **Central Asia** | Amu Darya-Nurek · Syr Darya-Toktogul |
| 🌏 **Asia** | Mekong-Xayaburi · Yangtze-Three Gorges · Indus-Tarbela · Brahmaputra-Subansiri · Ganges-Farakka · Salween-Myitsone |
| 🌎 **Americas** | Amazon-Belo Monte · Paraná-Itaipu · Orinoco-Guri · Colorado-Hoover · Columbia-Coulee · Rio Grande-Amistad |
| 🇪🇺 **Europe** | Danube-Iron Gates · Rhine · Dnieper-Kakhovka |
| 🌏 **Oceania** | Murray-Darling-Hume |

---

## 📊 Key Results — Multi-Basin

Illustrative AWSI framework outputs (NOT validated field measurements — real values require observation-grade discharge per basin):

| Basin | ATDI | AHIFD | ATCI | CI | Risk | UNWC |
|-------|------|-------|------|----|------|------|
| Blue Nile (GERD) | 43.6% | 19.7% | 70.3 | 0.484 | HIGH | Art. 7 |
| Euphrates-Atatürk | 41.8% | 19.3% | 71.4 | 0.475 | HIGH | Art. 7 |
| Nile-High Aswan | 40.8% | 19.5% | 71.8 | 0.399 | HIGH | Art. 7 |
| Syr Darya-Toktogul | 40.6% | 19.3% | 72.0 | 0.471 | HIGH | Art. 7 |
| Mekong-Xayaburi | 36.8% | 18.3% | 74.3 | 0.390 | MODERATE | Art. 5 |
| Danube-Iron Gates | 32.8% | 18.7% | 76.1 | 0.250 | MODERATE | Art. 5 |
| Rhine | 22.3% | 10.9% | 84.5 | 0.189 | LOW | — |

> Values above are illustrative framework outputs, not validated field measurements. Independent validation against non-shared-forcing benchmarks is pending observed discharge data. · 117 pytest tests passing
>
> **Risk distribution across all 26 basins:** HIGH = 4 (GERD, Euphrates-Atatürk, Nile-Aswan, Syr Darya-Toktogul) · MODERATE = 14 · LOW = 8. Legal tiers: CRITICAL ≥ 60% (Art. 33) · HIGH ≥ 40% (Art. 7) · MODERATE ≥ 25% (Art. 5) · LOW < 25%.

---

## 🏗 Architecture

```
hydrosovereign/
├── api.py              ← analyze_basin() — one-call entry point
├── indices.py          ← ATDI · AHIFD · AFSF · AHLB · ASI · ATCI
├── hbv.py              ← HBV-96 rainfall-runoff model
├── basins.py           ← 26-basin registry with metadata
├── legal.py            ← UNWC 1997 article trigger logic
├── alerts.py           ← Alert level classification
├── cli.py              ← Command-line interface (hsae / hydrosovereign)
├── py.typed            ← PEP 561 — type hints enabled
├── ai/
│   ├── negotiation.py  ← TreatyClassifier (429 TFDD treaties, trained)
│   ├── conflict.py     ← Conflict Index computation
│   ├── bayesian.py     ← Bayesian uncertainty quantification
│   └── forecast.py     ← Time-series forecasting
├── data/
│   ├── fetchers.py     ← Open-Meteo · GRDC · NASA POWER · GloFAS
│   └── nile_basin_sample.json
├── models/
│   └── hbv.py          ← HBV-96 model class + SCE-UA calibration
└── viz/
    ├── maps.py         ← Folium interactive maps
    └── plots.py        ← Plotly compliance dashboards
```

---

## 💻 CLI Usage

```bash
# Analyse a basin by coordinates
hsae analyze --lat 11.21 --lon 35.09 --name "Blue Nile"

# Full report for all 26 basins
hsae report --all --format json

# Compare two basins
hsae compare "Blue Nile" "Mekong"

# Check UNWC compliance
hsae compliance --basin "Euphrates" --article 7
```

---

## 📊 Comparison with Alternatives

| Feature | HSAE | SWAT+ | VIC | MRC Models |
|---------|------|-------|-----|------------|
| UNWC compliance (all articles) | ✅ | ❌ | ❌ | Partial |
| All 6 AWSI indices | ✅ | ❌ | ❌ | ❌ |
| Multi-model uncertainty bounds | ✅ (eWaterCycle) | ❌ | ❌ | ❌ |
| Live satellite (9 sensors) | ✅ | ❌ | ❌ | Partial |
| SHA-256 forensic audit chain | ✅ | ❌ | ❌ | ❌ |
| GeoAgent NL queries | ✅ | ❌ | ❌ | ❌ |
| QGIS Plugin | ✅ (ID 5040) | ❌ | ❌ | ❌ |
| pip installable | ✅ | ❌ | ❌ | ❌ |
| Open-source (GPL-3.0) | ✅ | Partial | ✅ | ❌ |
| 26-basin global coverage | ✅ | Manual | Manual | 6 countries |

---

## 🔗 Links

| Resource | URL |
|----------|-----|
| 🔌 QGIS Plugin (ID 5040) | [plugins.qgis.org/plugins/hsae_qgis/](https://plugins.qgis.org/plugins/hsae_qgis/) |
| 🌐 Live Streamlit App | [HSAE v6.0.14](https://hydrosovereign-ai-engine-hsae-v601-6euz2zxcmerkzxgordmvxf.streamlit.app) |
| 📦 GitHub (Main Repo) | [HydroSovereign-AI-Engine-HSAE-v601](https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601) |
| 🤖 GeoAgent Integration | [opengeos/GeoAgent PR #79](https://github.com/opengeos/GeoAgent/pull/79) |
| 🏛️ Zenodo Archive | [doi.org/10.5281/zenodo.19180160](https://doi.org/10.5281/zenodo.19180160) |
| 📄 Preprint (SSRN) | [papers.ssrn.com/abstract=6661396](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6661396) |
| 📰 SoftwareX Paper | [SOFTX-D-26-00442](https://www.sciencedirect.com/journal/softwarex) — Under Review |
| 📖 Manual (v6) | [Download Guide](https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601/raw/main/hsae_qgis/HSAE_v601_QGIS_Plugin_Manual_v6.docx) |

---

## 📝 Citation

```bibtex
@software{alkhedir2026hsae,
  author    = {Alkhedir, Seifeldin M.G.},
  title     = {{HydroSovereign AI Engine (HSAE) v6.8.1}},
  year      = {2026},
  publisher = {PyPI + QGIS Plugin Repository + Zenodo},
  version   = {6.8.1},
  note      = {QGIS Plugin ID: 5040. SoftwareX under review: SOFTX-D-26-00442.
               Preprint: SSRN 6661396. 362+ downloads, 20 countries.},
  url       = {https://pypi.org/project/hydrosovereign/},
  doi       = {10.5281/zenodo.19180160},
  orcid     = {0000-0003-0821-2991}
}
```

---

<div align="center">

*hydrosovereign v6.8.1 · GPL-3.0 · Seifeldin M.G. Alkhedir · ORCID: 0000-0003-0821-2991*

*University of Khartoum · DOI: 10.5281/zenodo.19180160*

</div>
