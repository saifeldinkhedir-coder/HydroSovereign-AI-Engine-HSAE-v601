# Quick Start

## Installation

```bash
pip install hydrosovereign[ml]
```

## Basin Analysis

```python
from hydrosovereign import analyze_basin

result = analyze_basin("Blue Nile (GERD)")

# Indices
print(result["indices"]["atdi"])   # 53.5%
print(result["indices"]["hifd"])   # 35.7%
print(result["indices"]["ci"])     # 0.583

# AI
print(result["ai"]["p_success"])   # 0.505
print(result["ai"]["strategy"])    # Mediation

# Legal
print(result["legal"]["articles"]) # Art.5, Art.7, Art.9, Art.20

# Alerts
print(result["alerts"]["overall"]) # ALERT
```

## HBV-96 Model

```python
from hydrosovereign.models import HBVModel
from hydrosovereign.data   import fetch_basin_forcing
import numpy as np

data  = fetch_basin_forcing("Blue Nile (GERD)", years=5)
P, T  = np.array(data["P"]), np.array(data["T"])
model = HBVModel(area_km2=174000, runoff_c=0.38)

# Simulate
result = model.simulate(P, T)
print(f"Mean Q = {result['Q_sim'].mean():.1f} m³/s")

# Calibrate
cal = model.calibrate(result["Q_sim"], P, T)
print(f"NSE = {cal['nse']:.3f}")
```

## Multi-Feature LSTM

```python
from hydrosovereign.ai import LSTMForecast
from hydrosovereign.data import fetch_basin_forcing

data  = fetch_basin_forcing("Blue Nile (GERD)", years=3)
model = LSTMForecast(features=["P","T","SM","ET0"])
model.fit_multi(data, area_km2=174000, epochs=50)
fc    = model.predict_multi(data)

print(fc["model"])       # LSTM(4_features, hidden=64, PyTorch)
print(fc["Q_forecast"])  # 7-day forecast (m³/s)
```

## REST API

```bash
uvicorn hydrosovereign.api_server:app --port 8000
```

```bash
curl http://localhost:8000/analyze \
  -X POST -H "Content-Type: application/json" \
  -d '{"name": "Blue Nile (GERD)"}'
```

## CLI

```bash
hydrosovereign analyze "Blue Nile (GERD)"
hydrosovereign rank-all
hydrosovereign list-basins
```
