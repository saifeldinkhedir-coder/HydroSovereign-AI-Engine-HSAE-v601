# QGIS Plugin Documentation

## Overview

The HSAE v6.01 QGIS Plugin provides full integration of the HydroSovereign AI Engine
within the QGIS desktop GIS environment.

## Installation

1. Download [`HSAE_v601_QGIS_Plugin_FINAL.zip`](https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601/blob/main/HSAE_v601_QGIS_Plugin_FINAL.zip)
2. QGIS → Plugins → Manage and Install Plugins → Install from ZIP
3. Select the ZIP file → Install Plugin
4. Enable: Plugins → HydroSovereign AI Engine v6.01

## Tools (13)

### 🌊 Load Basin Registry
Loads all 26 transboundary basins as a QGIS point layer with computed ATDI/HIFD indices.

### 📊 TDI/ATDI Visualiser
Applies graduated colour map based on ATDI values.

### ⚖️ UNWC Legal Layer
Loads UN 1997 UNWC legal risk overlay.

### 📤 Export Basin Data
Exports basin layer to Shapefile, GeoJSON, or CSV.

### 📋 Dashboard Dialog
Opens the main HSAE analysis dashboard.

### 🛰️ GEE Script Generator
Generates ready-to-use GEE scripts for 7 satellite sensors.

### 📡 GRDC Stations
Loads 10 key GRDC discharge stations as point layer.

### ⚡ Conflict Index
Computes ATDI/HIFD Conflict Index for all 26 basins. Export to CSV.

### 🤝 Negotiation AI
Shows negotiation success probability using GBM classifier (478 historical cases).

### 🗺️ WebGIS Map
Generates standalone Leaflet HTML map with full basin popup.

### 📊 Basin Panel
Toggles a real-time dockable dashboard panel showing all indices for the selected basin.

### 🏛️ ICJ/PCA Dossier Export
Exports complete legal dossier in TXT or HTML format.

### ℹ️ About
Shows plugin information, author, DOI, and links.

## Processing Algorithms (5)

Accessible via QGIS Processing Toolbox → HydroSovereign AI Engine:

| Algorithm | Description |
|---|---|
| ATDI Calculator | Compute ATDI from basin parameters |
| HIFD Calculator | Compute HIFD from basin parameters |
| Basin Legal Report | Generate complete legal report (TXT) |
| HBV-96 Calibration | Run HBV-96 model with SCE-UA calibration |
| Multi-Basin Comparison | Compare multiple basins (CSV + HTML) |

## File Structure

```
hsae_qgis/
├── metadata.txt               # Plugin metadata (v6.0.1)
├── __init__.py                # Entry point
├── plugin.py                  # Main plugin (13 tools)
├── basin_loader.py            # Basin layer creation
├── dashboard_panel.py         # Real-time panel
├── export_tool.py             # Export functions
├── tdi_visualiser.py          # TDI colour styling
├── legal_layer.py             # UNWC legal overlay
├── dialog_main.py             # Dashboard dialog
├── hsae_processing_provider.py# Processing provider
├── basins_50.json             # 26 basin data (enriched)
├── icon.png                   # Plugin icon
└── algorithms/
    ├── atdi_algorithm.py
    ├── hifd_algorithm.py
    ├── basin_report_algorithm.py
    ├── hbv_algorithm.py
    └── comparison_algorithm.py
```

## Requirements

- QGIS 3.16+
- Python 3.9+
- No additional Python packages required
