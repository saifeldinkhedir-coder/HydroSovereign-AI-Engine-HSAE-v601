# Architecture

## Package Structure

```
hydrosovereign/
├── __init__.py          # Top-level API
├── indices.py           # ATDI, HIFD, NSE, KGE, WQI, CI (calibrated)
├── hbv.py               # HBV-96 + SCE-UA calibration
├── basins.py            # 26 basin registry
├── legal.py             # UNWC 1997 engine
├── alerts.py            # 4-level alert system
├── api.py               # analyze_basin() unified entry point
├── api_server.py        # FastAPI REST service
├── async_alerts.py      # asyncio concurrent monitoring
├── cli.py               # Command-line interface
├── ai/
│   ├── negotiation.py   # GBM trained on 306 TFDD/ICOW cases
│   ├── bayesian.py      # Beta-Binomial risk assessment
│   ├── conflict.py      # Dynamic conflict predictor
│   └── forecast.py      # PyTorch LSTM + LinearForecast
├── models/
│   └── hbv.py           # HBVModel OOP wrapper
├── viz/
│   ├── plots.py         # 5 plot functions (Plotly)
│   └── maps.py          # 2 map functions (Scattergeo)
└── data/
    ├── fetchers.py      # Open-Meteo, GEE, Sentinel-2
    ├── tfdd_icow_cases.csv  # 306 empirical training cases
    └── nile_basin_sample.json  # 1825-day sample data
```

## Calibrated Formulas

### ATDI (RMSE = 4.1% vs 14 published basins)
```
ATDI = w_d·D + w_cap·(1-e^{-C/λ})·30 + w_nc·max(0,N-2) + w_arc·(1-r)
```
Parameters: `w_d=11.22, λ=42.33, w_nc=1.28, w_arc=11.89`

### HIFD (RMSE = 1.8%)
```
HIFD = w_d·D + w_cap·(1-e^{-C/λ})·20 + w_nc·max(0,N-2) + w_arc·(1-r)
```
Parameters: `w_d=3.98, λ=8.44, w_nc=0.54, w_arc=17.86`
