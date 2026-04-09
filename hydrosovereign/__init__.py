"""
HydroSovereign AI Engine (HSAE) v6.01
======================================
Open-source transboundary water analysis platform.

Core scientific functions for computing ATDI, HIFD, NSE, KGE,
Conflict Index, Negotiation AI, HBV-96 model, and more.

Author:  Seifeldin M.G. Alkedir
ORCID:   0000-0003-0821-2991
DOI:     10.5281/zenodo.19180160
GitHub:  https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-v601
App:     https://hydrosovereign-ai-engine-hsae-v601-6euz2zxcmerkzxgordmvxf.streamlit.app

Usage:
    from hydrosovereign import compute_atdi, compute_hifd, run_hbv96
    from hydrosovereign import ConflictIndex, NegotiationAI, BasinRegistry
"""

__version__    = "6.0.1"
__author__     = "Seifeldin M.G. Alkedir"
__email__      = "saifeldinkhedir@gmail.com"
__orcid__      = "0000-0003-0821-2991"
__doi__        = "10.5281/zenodo.19180160"
__license__    = "GPL-3.0"

# Core indices
from .indices import (
    compute_atdi,
    compute_hifd,
    compute_nse,
    compute_kge,
    compute_wqi,
    compute_conflict_index,
    compute_negotiation_probability,
    compute_all_indices,
)

# HBV-96 model
from .hbv import run_hbv96, calibrate_hbv_sceua

# Basin registry
from .basins import BasinRegistry, get_basin, list_basins, BASINS_26

# Alert system
from .alerts import AlertLevel, check_atdi_alert, check_hifd_alert

# Legal thresholds
from .legal import (
    get_triggered_articles,
    check_art7_nsh,
    check_art20_envflow,
    check_art33_dispute,
    get_legal_assessment,
)

__all__ = [
    # Indices
    "compute_atdi",
    "compute_hifd",
    "compute_nse",
    "compute_kge",
    "compute_wqi",
    "compute_conflict_index",
    "compute_negotiation_probability",
    "compute_all_indices",
    # HBV-96
    "run_hbv96",
    "calibrate_hbv_sceua",
    # Basins
    "BasinRegistry",
    "get_basin",
    "list_basins",
    "BASINS_26",
    # Alerts
    "AlertLevel",
    "check_atdi_alert",
    "check_hifd_alert",
    # Legal
    "get_triggered_articles",
    "check_art7_nsh",
    "check_art20_envflow",
    "check_art33_dispute",
    "get_legal_assessment",
]
