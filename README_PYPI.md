# HydroSovereign — HSAE v6.01

**Open-source transboundary water analysis toolkit**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19180160.svg)](https://doi.org/10.5281/zenodo.19180160)
[![License](https://img.shields.io/badge/License-GPL--3.0-blue)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)

## Installation

```bash
pip install hydrosovereign
```

## Quick Start

```python
from hydrosovereign import compute_atdi, compute_hifd, compute_all_indices

# Blue Nile GERD basin
result = compute_all_indices(
    runoff_c=0.38,
    cap_bcm=74.0,
    n_countries=3,
    dispute_level=4
)

print(f"ATDI = {result['atdi']:.1f}%")           # 49.2%
print(f"HIFD = {result['hifd']:.1f}%")           # 33.4%
print(f"P(Negotiation) = {result['negotiation']['p_success']:.0%}")  # 37%
print(f"Strategy: {result['negotiation']['strategy']}")
```

## Features

- **ATDI** — Alkedir Transparency Deficit Index
- **HIFD** — Human-Induced Flow Deficit
- **HBV-96** — Rainfall-runoff model with SCE-UA calibration
- **26 basins** — Full transboundary basin registry
- **Legal engine** — UNWC 1997 Article triggering
- **Conflict Index** — Composite basin risk score
- **Negotiation AI** — P(success) prediction

## Basin Registry

```python
from hydrosovereign import BasinRegistry

reg = BasinRegistry()
basin = reg.get("Blue Nile (GERD)")
print(basin["runoff_c"])   # 0.38
print(basin["cap"])         # 74.0

# Filter by continent
africa_basins = reg.filter_by_continent("Africa")
# Filter by dispute level
critical_basins = reg.filter_by_dispute(min_level=4)
```

## HBV-96 Model

```python
import numpy as np
from hydrosovereign import run_hbv96, calibrate_hbv_sceua

P = np.maximum(0, 2.5 * np.sin(np.pi * np.arange(365) / 180))
T = 25 + 5 * np.sin(2 * np.pi * np.arange(365) / 365)

result = run_hbv96(P, T, area_km2=174000, runoff_c=0.38)
print(f"Mean Q = {result['Q_sim'].mean():.1f} m³/s")
```

## Legal Assessment

```python
from hydrosovereign import get_legal_assessment

assessment = get_legal_assessment(atdi=49.2, hifd=33.4,
                                   dispute_level=4, n_countries=3)
print(assessment["articles"])
# ['Art.5 ERU', 'Art.9 Data Sharing', 'Art.7 NSH', 'Art.20 Env.Flow']
print(assessment["recommendation"])
```

## Author

**Seifeldin M.G. Alkedir** — University of Khartoum  
ORCID: [0000-0003-0821-2991](https://orcid.org/0000-0003-0821-2991)  
DOI: [10.5281/zenodo.19180160](https://doi.org/10.5281/zenodo.19180160)

## Live App

[https://hydrosovereign-ai-engine-hsae-v601-6euz2zxcmerkzxgordmvxf.streamlit.app](https://hydrosovereign-ai-engine-hsae-v601-6euz2zxcmerkzxgordmvxf.streamlit.app)

## License

GNU General Public License v3.0
