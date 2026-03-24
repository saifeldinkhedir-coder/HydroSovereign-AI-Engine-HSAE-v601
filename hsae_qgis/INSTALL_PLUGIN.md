# HSAE QGIS Plugin v6.01 — Installation Guide

## Method 1: Install from ZIP (Recommended)
1. Download `hsae_qgis_v601.zip`
2. Open QGIS
3. Plugins → Manage and Install Plugins
4. Install from ZIP → select `hsae_qgis_v601.zip`
5. Restart QGIS
6. Look for **HSAE v6.01** toolbar

## Method 2: Manual Installation
Copy the `hsae_qgis/` folder to:
- **Windows:** `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\`
- **Linux/Mac:** `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`

## Tools Available
| Tool | Description |
|------|-------------|
| 🌊 Load Basin Registry | 26 basins with ATF risk colours |
| 📊 TDI/ATDI Visualiser | Graduated colour map |
| ⚖️ UNWC Legal Layer | UN 1997 compliance overlay |
| 🛰️ GEE Script Generator | JavaScript for 7 sensors |
| 📡 GRDC Stations | Gauge stations Tier 1/2/3 |
| 📤 Export Basin Data | Shapefile / GeoJSON |
| 📋 Dashboard | HSAE main dialog |
| 🏛️ ICJ Dossier Export | Legal dossier TXT |

## Processing Toolbox
HydroSovereign → Calculate ATDI / HIFD / Basin Report

## Requirements
- QGIS ≥ 3.16
- No additional Python packages needed

## Author
Seifeldin M.G. Alkedir · ORCID: 0000-0003-0821-2991  
https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601
