# Examples

## 1. Compute ATDI for Blue Nile (GERD)

```python
from conflict_index import compute_atdi, compute_hifd

atdi = compute_atdi(
    runoff_c=0.38,
    cap=74.0,          # BCM
    n_countries=3,     # Ethiopia, Sudan, Egypt
    dispute_level=4    # CRITICAL (TFDD data)
)
print(f"ATDI = {atdi:.1f}%")  # → 49.2%

hifd = compute_hifd(runoff_c=0.38, cap=74.0, n_countries=3, dispute_level=4)
print(f"HIFD = {hifd:.1f}%")  # → 33.4%
```

---

## 2. Run HBV-96 Model

```python
import numpy as np
from hsae_hbv import run_hbv96

# Generate synthetic forcing data
np.random.seed(42)
n = 365
P = np.maximum(0, 2.5 * np.sin(np.pi * np.arange(n) / 180) + np.random.exponential(0.3, n))
T = 25 + 5 * np.sin(2 * np.pi * np.arange(n) / 365)

results = run_hbv96(P=P, T=T, area_km2=174000, runoff_c=0.38)
print(f"NSE = {results['NSE']:.3f}")  # → ~0.63
print(f"KGE = {results['KGE']:.3f}")  # → ~0.74
```

---

## 3. Fetch GEE Data

```python
import ee
from gee_connector import fetch_gpm_monthly

ee.Initialize(project="zinc-arc-484714-j8")

data = fetch_gpm_monthly(
    bbox=[33.0, 8.0, 37.5, 13.0],
    year=2025
)
print(f"Mean P = {data['mean_P']:.2f} mm/day")
print(f"Months with data: {data['n_months']}")
```

---

## 4. Use QGIS Plugin Programmatically

```python
# In QGIS Python console:
from hsae_qgis.plugin import HSAEPlugin
from hsae_qgis.basin_loader import load_basin_layer
from hsae_qgis.basins_data import BASINS_26
import json

# Load basins
with open("hsae_qgis/basins_50.json") as f:
    basins = json.load(f)

lyr = load_basin_layer(basins)
print(f"Loaded {lyr.featureCount()} basins")

# Access attributes
for feat in lyr.getFeatures():
    print(f"{feat['name']}: ATDI={feat['atdi_pct']:.1f}%")
```

---

## 5. Generate WebGIS Map

```python
from hsae_qgis.plugin import HSAEPlugin
import json

with open("hsae_qgis/basins_50.json") as f:
    basins = json.load(f)

plugin = HSAEPlugin.__new__(HSAEPlugin)
html   = plugin._build_webgis(basins)

with open("hsae_webgis.html", "w") as f:
    f.write(html)

print("WebGIS map saved: hsae_webgis.html")
```

---

## 6. Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_core.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

---

## 7. Export ICJ Dossier

```python
from hsae_qgis.plugin import HSAEPlugin
import json

with open("hsae_qgis/basins_50.json") as f:
    basins = json.load(f)

plugin = HSAEPlugin.__new__(HSAEPlugin)
plugin._dossier_html(basins, "HSAE_ICJ_Dossier.html")
print("ICJ Dossier exported: HSAE_ICJ_Dossier.html")
```
