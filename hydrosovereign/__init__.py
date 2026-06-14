"""
HydroSovereign AI Engine (HSAE) v6.7.0
=======================================
Satellite-driven transboundary water law compliance.
26 basins · 6 AWSI indices · UNWC 1997 · eWaterCycle BMI

Author:  Seifeldin M.G. Alkhedir
ORCID:   0000-0003-0821-2991
DOI:     10.5281/zenodo.19180160
License: GPL-3.0
"""

__version__   = "6.7.2"
__author__    = "Seifeldin M.G. Alkhedir"
__email__     = "saifeldinkhedir@gmail.com"
__orcid__     = "0000-0003-0821-2991"
__doi__       = "10.5281/zenodo.19180160"
__license__   = "GPL-3.0"
__plugin_id__ = "5040"
__qgis_ver__  = "6.0.12"

# Short-name aliases for all 6 AWSI indices
from hydrosovereign.indices import (
    compute_atdi  as ATDI,
    compute_ahifd as AHIFD,
    compute_afsf  as AFSF,
    compute_ahlb  as AHLB,
    compute_asi   as ASI,
    compute_atci  as ATCI,
    compute_conflict_index          as ConflictIndex,
    compute_negotiation_probability as NegotiationProb,
    compute_nse, compute_kge,
    compute_all_indices,
)
from hydrosovereign.ai.negotiation import NegotiationAI
from hydrosovereign.ai.conflict    import ConflictIndex as Conflict
from hydrosovereign.ai.bayesian    import BayesianUncertainty

__all__ = [
    "ATDI","AHIFD","AFSF","AHLB","ASI","ATCI",
    "ConflictIndex","NegotiationProb",
    "NegotiationAI","Conflict","BayesianUncertainty",
    "compute_all_indices","compute_nse","compute_kge",
]
