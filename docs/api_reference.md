# API Reference

## Core Modules

### `basins_global.py`
Basin registry for all 26 transboundary basins.

```python
from basins_global import GLOBAL_BASINS

# Get basin data
basin = GLOBAL_BASINS["Blue Nile (GERD)"]
print(basin["runoff_c"])   # 0.38
print(basin["cap"])         # 74.0 BCM
print(basin["country"])     # ["Ethiopia", "Sudan", "Egypt"]
```

---

### `conflict_index.py`
ATDI/HIFD-based conflict index computation.

```python
from conflict_index import compute_atdi, compute_hifd, compute_conflict_index

atdi = compute_atdi(runoff_c=0.38, cap=74.0, n_countries=3, dispute_level=4)
# Returns: 49.2

hifd = compute_hifd(runoff_c=0.38, cap=74.0, n_countries=3, dispute_level=4)
# Returns: 33.4

ci = compute_conflict_index(atdi=49.2, hifd=33.4, dispute=4, n_countries=3)
# Returns: 0.612
```

---

### `negotiation_ai.py`
Negotiation success probability using GBM classifier (478 cases).

```python
from negotiation_ai import predict_negotiation_success

prob = predict_negotiation_success(
    atdi=49.2, hifd=33.4, n_countries=3,
    has_treaty=True, dispute_level=4
)
# Returns: {"p_success": 0.37, "strategy": "PCA Arbitration",
#           "article": "Art.33 UNWC"}
```

---

### `hsae_hbv.py`
HBV-96 hydrological model with SCE-UA calibration.

```python
from hsae_hbv import run_hbv96, calibrate_hbv_sceua

# Run HBV-96 simulation
results = run_hbv96(
    P=precip_series,    # Daily precipitation (mm/day)
    T=temp_series,      # Daily temperature (°C)
    area_km2=174000,
    runoff_c=0.38,
    params={"FC": 250, "LP": 0.7, "BETA": 2.0, "K1": 0.05, "K2": 0.005}
)
# Returns: {"Q_sim": [...], "NSE": 0.63, "KGE": 0.74}

# SCE-UA calibration (requires GRDC observed data)
best_params = calibrate_hbv_sceua(
    Q_obs=observed_discharge,
    P=precip_series, T=temp_series,
    area_km2=174000, n_trials=300
)
```

---

### `gee_connector.py`
Google Earth Engine data fetcher (7 satellite sources).

```python
from gee_connector import fetch_all_gee_sources

data = fetch_all_gee_sources(
    basin_bbox=[33.0, 8.0, 37.5, 13.0],
    start_date="2025-01-01",
    end_date="2025-12-31"
)
# Returns data from:
# - GPM IMERG V07 (precipitation)
# - GRACE-FO MASCON (TWS)
# - SMAP (soil moisture)
# - Sentinel-1 SAR (flood extent)
# - Sentinel-2 NDWI/NDVI (water/vegetation)
# - GloFAS ERA5 v4 (discharge)
# - Open-Meteo (temperature, ET)
```

---

## QGIS Plugin API

### `hsae_qgis/plugin.py`

```python
# Tools accessible via QGIS Plugin menu:
# 1.  load_basins()       — Load 26 basins as point layer
# 2.  apply_tdi()         — Apply ATDI graduated colour map
# 3.  load_legal()        — UN 1997 UNWC legal risk overlay
# 4.  export_data()       — Export to Shapefile/GeoJSON/CSV
# 5.  show_dashboard()    — Main dashboard dialog
# 6.  gee_scripts()       — GEE scripts for 7 sensors
# 7.  grdc_overlay()      — GRDC discharge stations
# 8.  conflict_index()    — Conflict Index all 26 basins
# 9.  negotiation_ai()    — Negotiation success probability
# 10. webgis_map()        — Standalone Leaflet HTML map
# 11. toggle_panel()      — Real-time dashboard panel
# 12. icj_export()        — ICJ/PCA legal dossier
# 13. about()             — About dialog
```

### `hsae_qgis/algorithms/`

Processing Toolbox algorithms accessible via QGIS Processing:

| Algorithm | ID | Inputs | Outputs |
|---|---|---|---|
| ATDI Calculator | `atdi:atdicalculator` | rc, cap, nc, disp | ATDI% |
| HIFD Calculator | `atdi:hifdcalculator` | rc, cap, nc, disp | HIFD% |
| Basin Legal Report | `atdi:basinreport` | basin params | TXT report |
| HBV-96 Calibration | `atdi:hbv96calibration` | area, rc, P, T | NSE, KGE, CSV |
| Multi-Basin Comparison | `atdi:multibasincomparison` | basin names | CSV + HTML |
