"""
HydroSovereign AI Engine (HSAE) v6.2.0
========================================
Author:  Seifeldin M.G. Alkedir · ORCID: 0000-0003-0821-2991
DOI:     10.5281/zenodo.19180160
"""

__version__   = "6.5.0"
__author__    = "Seifeldin M.G. Alkedir"
__email__     = "saifeldinkhedir@gmail.com"
__orcid__     = "0000-0003-0821-2991"
__doi__       = "10.5281/zenodo.19180160"
__license__   = "GPL-3.0"

# Unified high-level API
from .api import analyze_basin, analyze_all_basins

# Live data fetchers
from .data import fetch_basin_forcing, fetch_openmeteo, fetch_gee_basin, fetch_sentinel2_wqi

# Core indices (backward compatible)
from .indices import (compute_atdi, compute_hifd, compute_nse, compute_kge,
    compute_wqi, compute_conflict_index, compute_negotiation_probability,
    compute_all_indices)

# HBV-96
from .hbv    import run_hbv96, calibrate_hbv_sceua

# Basin registry
from .basins import BasinRegistry, get_basin, list_basins, BASINS_26

# Legal engine
from .legal  import (get_triggered_articles, check_art7_nsh, check_art20_envflow,
    check_art33_dispute, get_legal_assessment)

# Alerts
from .alerts import AlertLevel, check_atdi_alert, check_hifd_alert
