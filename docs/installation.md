# Installation Guide

## Requirements

- Python 3.9+
- pip

## Install from GitHub

```bash
git clone https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601
cd HydroSovereign-AI-Engine-HSAE-v601
pip install -r requirements.txt
streamlit run app.py
```

## Install via Docker

```bash
docker-compose up
```

## QGIS Plugin Installation

1. Download `HSAE_v601_QGIS_Plugin_FINAL.zip`
2. Open QGIS → Plugins → Manage and Install Plugins
3. Click "Install from ZIP"
4. Select the downloaded ZIP file
5. Enable "HydroSovereign AI Engine v6.01"

## Google Earth Engine Setup

1. Create GEE account at [earthengine.google.com](https://earthengine.google.com)
2. Create project: `zinc-arc-484714-j8`
3. In HSAE app: select "Direct GEE" mode

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| streamlit | ≥1.32 | Web interface |
| numpy | ≥1.24 | Numerical computing |
| pandas | ≥2.0 | Data manipulation |
| plotly | ≥5.18 | Interactive charts |
| earthengine-api | ≥0.1.390 | GEE integration |
| scipy | ≥1.10 | SCE-UA optimization |
