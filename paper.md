---
title: 'HydroSovereign AI Engine (HSAE) v6.01: An Open-Source Satellite
        and AI Platform for Transboundary Water Sovereignty Analysis'

tags:
  - Python
  - hydrology
  - transboundary water
  - satellite remote sensing
  - machine learning
  - Google Earth Engine
  - UN Watercourses Convention
  - QGIS
  - digital twin
  - water sovereignty

authors:
  - name: Seifeldin M.G. Alkedir
    orcid: 0000-0003-0821-2991
    affiliation: 1

affiliations:
  - name: Institute of Environmental Studies, University of Khartoum, Sudan
    index: 1

date: 23 March 2026
bibliography: paper.bib
---

# Summary

The **HydroSovereign AI Engine (HSAE) v6.01** is an open-source Python
platform that enables researchers and water managers to monitor, analyse, and
report on transboundary river basin conditions using satellite data, machine
learning, and international water law. Built on 49 Python modules (31,273
lines of code) and delivered as a 33-page Streamlit web application, HSAE
integrates eight satellite sensors from Google Earth Engine [@gorelick2017]
— including Sentinel-1 SAR, Sentinel-2, GPM IMERG [@funk2015], MODIS,
VIIRS, GRACE-FO [@landerer2020], and SMAP [@entekhabi2010] — with
physics-based hydrological models, five machine learning algorithms, and
automated legal analysis of 33 articles of the UN Watercourses Convention
1997 [@ilc2001] across 26 globally contested transboundary river basins.

HSAE introduces five original quantitative indices: the **Alkedir
Transparency Deficit Index** (ATDI), the **Alkedir Human-Induced Flow
Deficit** (AHIFD), the **Alkedir Forensic Signal Factor** (AFSF), the
**Alkedir Sovereignty Index** (ASI), and the **Alkedir Treaty Compliance
Index** (ATCI). These indices bridge the gap between hydrological
observations and legal obligations under international water law, enabling
automated generation of treaty compliance reports, ICJ/PCA/ITLOS legal
dossiers, and diplomatic protest letters.

The software is archived at Zenodo (DOI: 10.5281/zenodo.19180160)
[@alkedir2026] and is available at
<https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601>.

# Statement of Need

Transboundary river basins supply freshwater to more than 40% of the global
population [@wolf1999; @voros2010; @gleick2023]. Despite this critical
importance, upstream dam operations frequently reduce downstream flows without
notification, violating the UN Watercourses Convention 1997
[@ilc2001; @dinar2007]. Quantifying these violations requires integrating
satellite observations, hydrological models, and legal frameworks — a task
currently beyond any single open-source tool.

Existing platforms address isolated components: SWAT+ [@neitsch2011] handles
watershed hydrology but lacks legal analysis; HydroSHEDS
[@lehner2008; @lehner2011] provides geospatial data without modelling;
GloFAS [@harrigan2020; @hersbach2020] delivers streamflow forecasts without
treaty compliance scoring; and decision-support frameworks [@turban2023]
lack basin-specific satellite integration. No open-source software combines
satellite remote sensing, hydrological modelling, machine learning, and water
law automation in a single deployable application [@mccullough2022; @sips2021].

HSAE fills this gap by providing a reproducible, peer-reviewable computational
framework for transboundary water governance research.

# State of the Field

Satellite-based monitoring of transboundary reservoirs has advanced rapidly
[@biancamaria2016; @rodell2018], but tools remain fragmented. Hydrological
models such as HBV [@bergstrom1992] and MODFLOW [@doll2014] are
well-established for water balance computation but lack legal interpretation
layers. Machine learning approaches [@breiman2001; @shen2023; @yokoo2022]
improve streamflow forecasting but are rarely connected to treaty compliance
frameworks. HSAE is the first platform to connect satellite observation,
hydrological modelling, and legal compliance in an integrated open-source
system.

# Software Design and Functionality

HSAE is structured around five pillars:

**Satellite data integration.** Eight GEE sensors provide real-time data.
Penman-Monteith ET₀ [@penman1948; @allen1998] corrects inflow for
evapotranspiration. GRACE-FO [@landerer2020; @rodell2018] provides
terrestrial water storage anomalies. SMAP [@entekhabi2010; @oneill2021]
provides soil moisture. GloFAS v4 [@harrigan2020] provides 30-day
ensemble forecasts with UN Art. 28 early-warning alerts.

**Hydrological modelling.** The HBV-96 model [@bergstrom1992] is calibrated
using GRDC discharge observations [@grdc2023]. Monte Carlo uncertainty
quantification (10,000 samples) and Sobol variance decomposition
[@saltelli2010] characterise parameter uncertainty. Model performance is
evaluated using NSE [@nash1970], KGE [@gupta2009], and PBIAS
[@moriasi2007] benchmarks.

**Machine learning and Digital Twin.** An ensemble of Random Forest
[@breiman2001], MLP, and Gradient Boosting models provides multi-step
streamflow forecasting. A Digital Twin using Ensemble Kalman Filter
assimilation [@evensen2003; @zhao2021; @shen2023; @yokoo2022] provides
real-time basin state estimation. Negotiation outcome prediction uses a GBM
classifier trained on 47 historical water dispute cases.

**Legal compliance automation.** The canonical ATDI formula maps satellite
observations to UN Arts. 5, 7, 9, 12, and 33 thresholds
[@ilc2001; @ipcc2021; @hamman2018; @lutz2016; @winsemius2006]. The Treaty
Diff module scores compliance across 15 international water treaties using
the ATCI index. The ICJ Dossier generator produces ICJ/PCA/ITLOS
submission-ready legal dossiers automatically.

**QGIS Desktop Plugin.** A companion QGIS plugin (9 tools + 3 Processing
algorithms) enables basin mapping, TDI visualisation, UNWC legal compliance
overlay, and export to Shapefile or GeoJSON for publication figures.


# Installation and Usage

HSAE can be installed and run locally with three commands:

```bash
git clone https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601
cd HydroSovereign-AI-Engine-HSAE-v601
pip install -r requirements.txt
streamlit run app.py
```

The application opens at `http://localhost:8501`. No API keys are required
for the built-in physics-based simulation mode. Real satellite data is
activated by registering for free credentials at Google Earth Engine,
NASA Earthdata, GRDC (grdc.bafg.de), and Copernicus CDS.

**Typical workflow:**

1. Select a basin from the sidebar (26 pre-configured basins)
2. Choose a data mode (simulation or real API)
3. Run the v430 engine to generate a basin DataFrame
4. Navigate pages: HBV → Validation → ATDI → Legal → ICJ Dossier → Export

**Inputs:** CSV uploads (GRDC discharge), GEE script outputs (satellite CSV),
or built-in simulation.

**Outputs:** ATDI/AHIFD scores, NSE/KGE metrics, legal compliance reports,
ICJ dossiers (TXT), HTML/Excel/JSON/GeoJSON exports, QGIS layers.

# Research Impact

HSAE has been applied to the Blue Nile GERD case study, demonstrating ATDI =
0.78 during the 2020–2023 filling phases, consistent with independent
estimates [@munia2020; @wheeler2016; @kim2009; @lauri2012]. Climate scenario
projections using IPCC AR6 SSP1–5 pathways [@ipcc2021] to 2100 support
future research on climate–water conflict interactions [@bharti2011].
Benchmarking against WEAP, MIKE HYDRO, HEC-HMS, and SWAT+ shows competitive
or superior NSE and KGE scores while uniquely providing legal compliance
automation [@moriasi2007; @gupta2009; @nash1970].

# AI Usage Disclosure

Claude (Anthropic) assisted with code debugging, documentation drafting, and
iterative module refinement during development of HSAE v6.01. All scientific
methodology, index formulations (ATDI, AHIFD, AFSF, ASI, ATCI), legal
mappings, and research design decisions were made exclusively by the author.
The author takes full responsibility for the accuracy and originality of all
submitted materials.

# Acknowledgements

The author acknowledges the Global Runoff Data Centre (GRDC, Koblenz,
Germany) [@grdc2023] for discharge data; ECMWF for GloFAS reanalysis
[@harrigan2020]; NASA NSIDC for SMAP L4 [@oneill2021]; NASA JPL for
GRACE-FO RL06 [@landerer2020]; and the QGIS Development Team. No financial
support was received for this work.

# References
