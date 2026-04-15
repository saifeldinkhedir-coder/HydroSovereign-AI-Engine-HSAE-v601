# HydroSovereign AI Engine (HSAE) v6.5.0

> **AI-powered decision-support platform for transboundary water governance**

[![PyPI](https://img.shields.io/pypi/v/hydrosovereign)](https://pypi.org/project/hydrosovereign/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19180160.svg)](https://doi.org/10.5281/zenodo.19180160)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![ORCID](https://img.shields.io/badge/ORCID-0000--0003--0821--2991-green)](https://orcid.org/0000-0003-0821-2991)

## Overview

`hydrosovereign` is the only Python package that unifies:

| Component | Technology |
|---|---|
| Hydrological modelling | HBV-96 + SCE-UA calibration |
| AI forecasting | PyTorch LSTM (true recurrent) |
| Geopolitical AI | GBM trained on 306 TFDD/ICOW cases |
| Legal framework | UNWC 1997 — 33 articles automated |
| Live satellite data | Open-Meteo + GEE (GPM, GRACE-FO, SMAP, Sentinel) |
| Water quality | WHO 2017 physicochemical WQI |

## Quick Install

```bash
pip install hydrosovereign          # core
pip install hydrosovereign[ml]      # + PyTorch
pip install hydrosovereign[viz]     # + Plotly
pip install hydrosovereign[full]    # everything
```

## One-Line Analysis

```python
from hydrosovereign import analyze_basin

result = analyze_basin("Blue Nile (GERD)")
print(result["indices"]["atdi"])    # 53.5%
print(result["ai"]["p_success"])    # 0.505
print(result["legal"]["articles"])  # [Art.5, Art.7, Art.9, Art.20]
```

## Citation

```bibtex
@software{alkedir2026hydrosovereign,
  author    = {Alkedir, Seifeldin M.G.},
  title     = {hydrosovereign: HydroSovereign AI Engine v6.5.0},
  year      = {2026},
  doi       = {10.5281/zenodo.19180160},
  orcid     = {0000-0003-0821-2991}
}
```
