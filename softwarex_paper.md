# HydroSovereign AI Engine (HSAE) v6.01: An Open-Source Satellite and AI Platform for Transboundary Water Sovereignty Analysis

**Author:** Seifeldin M.G. Alkedir  
**ORCID:** 0000-0003-0821-2991  
**Affiliation:** Institute of Environmental Studies, University of Khartoum (Formerly); Independent Water Resources Researcher, Madinah, Saudi Arabia  
**Email:** saifeldinkhedir@gmail.com  
**Journal:** SoftwareX (Elsevier) — Submitted March 2026  
**Status:** Under Review (6 corrections applied)  
**DOI:** 10.5281/zenodo.19180160  

---

## Abstract

The HydroSovereign AI Engine (HSAE) v6.01 is an open-source Python and Streamlit platform integrating live multi-sensor satellite Earth observation, physics-based hydrological modelling, machine learning, and UN Watercourses Convention 1997 (UNWC) automated legal compliance scoring for transboundary river basin governance. Seven Google Earth Engine (GEE) sources — GPM IMERG V07, GRACE-FO MASCON RL06v4, Sentinel-1 SAR, Sentinel-2 NDWI/NDVI, SMAP soil moisture, GloFAS ERA5 v4 discharge, and Open-Meteo ERA5 temperature — are fetched in parallel and delivered to all 35 application pages simultaneously via a Direct GEE data mode. Applied to the Blue Nile (GERD) basin (174,000 km²), HSAE achieves NSE = 0.63 and KGE = 0.74 with default HBV-96 parameters and real GPM IMERG forcing, and computes ATDI = 43.5% (Article 7 UNWC zone) and HIFD = 20.0%. The platform covers 26 globally contested transboundary basins, includes a companion QGIS plugin (9 tools, 3 Processing algorithms), and generates ICJ-format legal dossiers with SHA-256 data integrity chains. HSAE v6.01 is freely available under GPL-3.0 (DOI: 10.5281/zenodo.19180160). A companion Python package (hydrosovereign v6.5.3) is published on PyPI, providing pip-installable access to all scientific indices and the HBV-96 model.

**Keywords:** transboundary water governance; Google Earth Engine; HBV-96; UN Watercourses Convention 1997; satellite hydrology; open-source software

---

## Software Metadata

| Field | Details |
|---|---|
| **Software name** | HydroSovereign AI Engine (HSAE) v6.01 |
| **Developer** | Seifeldin M.G. Alkedir, University of Khartoum |
| **Version** | 6.01 |
| **Language** | Python 3.12 · Streamlit 1.38 |
| **License** | GPL-3.0 |
| **GitHub** | https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601 |
| **Zenodo DOI** | https://doi.org/10.5281/zenodo.19180160 |
| **Live App** | https://hydrosovereign-ai-engine-hsae-v601-6euz2zxcmerkzxgordmvxf.streamlit.app |
| **CI/CD** | GitHub Actions — three workflows: tests.yml, daily_gee.yml (06:00 UTC), monthly_gee.yml |
| **Tests** | 61 Python files · full pytest suite (TDI/ATDI, NSE/KGE, HBV-96, GEE, legal) |
| **Modules** | 61 Python files · 35 app pages · 0 syntax errors · hydrosovereign PyPI v6.5.3 |
| **QGIS Plugin** | 9 tools + 3 Processing algorithms (ATDI + HIFD + Basin Report) |

---

## 1. Motivation and Significance

Transboundary river basins supply freshwater to more than 40% of the global population [1]. Despite the UN Watercourses Convention 1997 (UNWC) establishing principles of equitable utilisation and no-harm, upstream dam operations routinely reduce downstream flows without notification, potentially inconsistent with Arts. 5, 7, 9, and 12 [2]. Quantifying these violations requires integrating satellite observations, hydrological models, and legal frameworks — a task beyond any single existing open-source tool.

Existing platforms address isolated components: SWAT+ [3] handles watershed hydrology but lacks legal analysis; HydroSHEDS [4] provides geospatial data without modelling; GloFAS [5] delivers forecasts without treaty compliance scoring. HSAE is the first open-source platform to combine all three domains in a single deployable application.

---

## 2. Software Description

### 2.1 Architecture

HSAE is structured around five functional pillars: satellite data integration, physics-based hydrological modelling, machine learning and Digital Twin state estimation, legal compliance automation, and QGIS desktop integration.

### 2.2 Satellite Data Integration

Seven GEE sources provide real-time basin monitoring through parallel server-side fetching. All sources are fetched in parallel using concurrent.futures.ThreadPoolExecutor (8 workers). Two automated pipelines are operational:

1. **daily_gee.yml** (06:00 UTC) — retrieves the rolling 12-month window for all seven sources across all 26 basins, stores in `data/gee_realtime.json` (schema v4.0), enabling sub-second response for current-year queries
2. **monthly_gee.yml** (1st of each month, 04:00 UTC) — computes annual summaries for 2015–2024 in `data/gee_historical.json`

Sources: GPM IMERG V07 [7] (12 months), GRACE-FO MASCON RL06v4 [8] (57-month archive, all 26 basins), Sentinel-1 GRD (12 months, VV dB), Sentinel-2 SR Harmonized (2–8 months, cloud-limited), SMAP via ERA5 proxy (13 months), GloFAS ERA5 v4 derived (12 months), Open-Meteo ERA5 (13 months).

### 2.3 Mathematical Framework

Core equations: TDI (daily transparency deficit), ATDI (annual index), NSE, KGE, HBV-96 water balance, HIFD.

### 2.4 Machine Learning and Digital Twin

Ensemble of Random Forest [18], MLP, and Gradient Boosting models. Digital Twin using Ensemble Kalman Filter (n=200) for real-time basin state estimation.

### 2.5 Legal Compliance Automation

Automated UNWC 1997 compliance assessment across 33 articles using ATDI thresholds. ICJ Dossier generator with SHA-256 evidence chain.

### 2.6 QGIS Plugin

9 tools + 3 Processing algorithms. Compatible with QGIS ≥ 3.16. GPL-3.0.

---

## 3. Installation and Usage

```bash
git clone https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601
pip install -r requirements.txt
streamlit run app.py
```

Companion package:
```bash
pip install hydrosovereign   # [24]
```

Tests:
```bash
pytest tests/test_core.py -v
```

---

## 4. Illustrative Example: Blue Nile (GERD)

Applied to the Blue Nile basin (GERD case study, area = 174,000 km², latitude 7–15°N):

| Metric | Value | Source | UNWC Implication |
|---|---|---|---|
| Mean Precipitation P | 1.29 mm/day | GPM IMERG V07 | Forcing input |
| Mean Temperature T | 28.1 °C | Open-Meteo ERA5 | PET estimation |
| TWS Anomaly (mean) | 21.94 cm | GRACE-FO MASCON (57mo) | Storage validation |
| SMAP Soil Moisture | 13 months · ERA5 proxy · 26 basins | NASA SMAP | Soil state |
| NSE (default HBV-96) | 0.63 | GPM + GloFAS ERA5 | Model performance |
| KGE (default HBV-96) | 0.74 | GPM + GloFAS ERA5 | Decomposed skill |
| ATDI | 43.5% | GPM + HBV-96 | Art. 7 UNWC zone |
| HIFD | 20.0% | HBV-96 naturalised | Art. 5 utilisation |
| ICJ dossier time | < 2 minutes | Automated pipeline | Legal evidence |

---

## 5. Impact

HSAE addresses a documented gap in open-source hydro-legal software. The 24-hour caching strategy and parallel multi-source fetching enable near-real-time monitoring. Full SCE-UA calibration pending GRDC data (Request ID: 78949). The companion hydrosovereign package (v6.5.3, PyPI [24]) enables reproducible computation of all indices via `pip install hydrosovereign`.

---

## 6. Novelty, Innovation and Intellectual Contribution

### 6.1 Five Original Scientific Indices (Alkedir, 2024–2025)

1. ATDI — Alkedir Transparency Deficit Index
2. AHIFD — Alkedir Human-Induced Flow Deficit
3. AFSF — Alkedir Forensic Signal Factor
4. ASI — Alkedir Sovereignty Index
5. ATCI — Alkedir Treaty Compliance Index

### 6.2 Novel Software Architecture

1. Direct GEE Parallel Multi-Source Fetching with Pre-computation Pipeline
2. Integrated Hydro-Legal Digital Twin (HBV-96 + EnKF + satellite assimilation)
3. Two-tier Automated GEE Pipeline with Historical Archive (daily_gee.yml + monthly_gee.yml). A companion pip-installable package (hydrosovereign v6.5.3, PyPI [24]) provides programmatic access to all indices, HBV-96 model, and 26-basin registry.

### 6.3 First-of-its-kind Integration Paradigm

First open-source platform to achieve end-to-end automation from live multi-sensor satellite observation to UN treaty compliance assessment.

### 6.4 Intellectual Property and Scientific Priority

All five indices and architectures are original contributions of Seifeldin M.G. Alkedir (ORCID: 0000-0003-0821-2991). Priority established via GitHub commits (2024), Zenodo DOI (10.5281/zenodo.19180160), and this SoftwareX submission.

### 6.5 Comparison with Prior Art

No existing tool provides the combination of live satellite integration, physics-based modelling, ML, and legal compliance assessment. See Table 2 in the full paper.

---

## 7. Conclusions

HSAE v6.01 provides the first open-source platform combining live multi-sensor GEE satellite data (7 sources, 26 basins), HBV-96 + SCE-UA calibration, ML ensemble + Digital Twin EnKF, and UNWC 1997 automated compliance scoring. Pre-calibration NSE = 0.63, KGE = 0.74 (Blue Nile, real GPM forcing). Post-calibration results forthcoming upon GRDC data receipt.

**Future priorities:**
1. SCE-UA calibration on Blue Nile, Rhine, Mekong (GRDC Request 78949)
2. JH-1 paper targeting NSE ≥ 0.70
3. JOSS submission April–May 2026 (all files ready)
4. Nature Water NW-1 paper (satellite evidence of underreporting — GEE data operational)
5. OSGeo QGIS Plugin Repository listing

---

## Conflict of Interest

The author declares no conflict of interest.

---

## Data Availability Statement

All source code under GPL-3.0 at GitHub and Zenodo (DOI: 10.5281/zenodo.19180160). Live app: https://hydrosovereign-ai-engine-hsae-v601-6euz2zxcmerkzxgordmvxf.streamlit.app. Companion package: `pip install hydrosovereign` (version 6.5.3; GitHub: https://github.com/saifeldinkhedir-coder/hydrosovereign) [24]. Pre-computed GEE data (`data/gee_realtime.json`, schema v4.0) committed to repository and updated automatically via GitHub Actions.

---

## References

[1] Wolf, A.T. (1999). Natural Resources Forum, 23(1), 3–30.  
[2] United Nations (1997). Convention on Non-Navigational Uses of International Watercourses. UN Doc. A/51/869.  
[3] Neitsch, S.L. et al. (2011). SWAT Theoretical Documentation. Texas Water Resources Institute.  
[4] Lehner, B. et al. (2008). Eos AGU, 89(10), 93–94.  
[5] Harrigan, S. et al. (2020). Earth System Science Data, 12(3), 2043–2060.  
[6] Gorelick, N. et al. (2017). Remote Sensing of Environment, 202, 18–27.  
[7] Huffman, G.J. et al. (2023). GPM IMERG Final V07. NASA GSFC. doi:10.5067/GPM/IMERG/3B-HH/07  
[8] Landerer, F.W. et al. (2020). Geophysical Research Letters, 47(12).  
[9] Entekhabi, D. et al. (2010). Proceedings of the IEEE, 98(5), 704–716.  
[16] Moriasi, D.N. et al. (2007). Transactions of ASABE, 50(3), 885–900.  
[18] Breiman, L. (2001). Machine Learning, 45(1), 5–32.  
[19] Evensen, G. (2003). Ocean Dynamics, 53(4), 343–367.  
[20] Duan, Q. et al. (1993). Water Resources Research, 28(4), 1015–1031.  
[22] Torres, R. et al. (2012). Remote Sensing of Environment, 120, 9–24.  
[23] Drusch, M. et al. (2012). Remote Sensing of Environment, 120, 25–36.  
[24] Alkedir, S.M.G. (2026). hydrosovereign: Python package for transboundary hydrological basin analysis, ATDI/HIFD indices, and HBV-96 modelling (v6.5.3). PyPI. GitHub: https://github.com/saifeldinkhedir-coder/hydrosovereign. DOI: 10.5281/zenodo.19180160  
