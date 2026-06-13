"""
hsae_qgis/core/indices.py  —  v6.0.12
======================================
SINGLE SOURCE OF TRUTH for all AWSI formulas.

Calibrated against Blue Nile (GERD) published values:
  ATDI=43.6%  AHIFD=19.7%  ATCI=70.3

All plugin files import from here:
  from hsae_qgis.core.indices import compute_atdi, compute_all

Author:  Seifeldin M.G. Alkhedir · ORCID: 0000-0003-0821-2991
"""
from __future__ import annotations
from typing import Dict


def compute_atdi(runoff_c: float, cap_bcm: float,
                 n_countries: int, dispute_level: int) -> float:
    """ATDI — Art.7 UNWC triggered when ≥ 40%."""
    t1 = min(float(cap_bcm) / 8.5, 11.0)
    t2 = float(dispute_level) * 4.8
    t3 = (float(n_countries) - 2) * 2.0
    t4 = (1.0 - float(runoff_c)) * 6.0
    return round(min(95.0, max(5.0, 10.0 + t1 + t2 + t3 + t4)), 1)


def compute_ahifd(runoff_c: float, cap_bcm: float,
                  n_countries: int, dispute_level: int) -> float:
    """AHIFD — Human-Induced Flow Deficit."""
    t1 = min(float(cap_bcm) / 18.0, 6.0)
    t2 = (1.0 - float(runoff_c)) * 5.0
    t3 = float(dispute_level) * 2.0
    t4 = (float(n_countries) - 2) * 1.5
    return round(min(80.0, max(3.0, 3.0 + t1 + t2 + t3 + t4)), 1)


def compute_hifd(runoff_c: float, cap_bcm: float,
                 n_countries: int, dispute_level: int) -> float:
    """Backward-compatibility alias for compute_ahifd()."""
    return compute_ahifd(runoff_c, cap_bcm, n_countries, dispute_level)


def compute_afsf(runoff_c: float, cap_bcm: float,
                 n_countries: int, dispute_level: int) -> float:
    """AFSF — Forensic Signal Factor. Art.9 → ≥ 0.50."""
    a = compute_atdi(runoff_c, cap_bcm, n_countries, dispute_level)
    h = compute_ahifd(runoff_c, cap_bcm, n_countries, dispute_level)
    return round(min(1.0, max(0.0, a / 100 * 0.6 + h / 80 * 0.4)), 3)


def compute_ahlb(runoff_c: float, cap_bcm: float,
                 n_countries: int, dispute_level: int) -> float:
    """AHLB — HBV-Legal Bridge. Arts. 5,6,7."""
    return round(compute_atdi(runoff_c, cap_bcm, n_countries, dispute_level) / 100, 3)


def compute_asi(runoff_c: float, cap_bcm: float,
                n_countries: int, dispute_level: int) -> float:
    """ASI — Sovereignty Index. Art.5 → < 0.50."""
    a = compute_atdi(runoff_c, cap_bcm, n_countries, dispute_level)
    h = compute_ahifd(runoff_c, cap_bcm, n_countries, dispute_level)
    return round(max(0.05, min(0.95, 1.0 - a / 100 * 0.6 - h / 80 * 0.4)), 3)


def compute_atci(runoff_c: float, cap_bcm: float,
                 n_countries: int, dispute_level: int) -> float:
    """ATCI — Treaty Compliance Index. All 6 UNWC arts."""
    a = compute_atdi(runoff_c, cap_bcm, n_countries, dispute_level)
    h = compute_ahifd(runoff_c, cap_bcm, n_countries, dispute_level)
    return round(min(95.0, max(20.0, 100.0 - a * 0.5 - h * 0.4)), 1)


def compute_conflict_index(atdi: float, ahifd: float,
                           dispute_level: int, n_countries: int) -> float:
    """CI — Composite Conflict Index. ≥ 0.55 = CRITICAL."""
    t1 = 0.40 * atdi / 100
    t2 = 0.25 * float(dispute_level) / 4.0
    t3 = 0.20 * float(ahifd) / 80.0
    t4 = 0.10 * min(float(n_countries - 2) * 0.15, 0.1)
    return round(min(1.0, max(0.0, t1 + t2 + t3 + t4)), 3)


def compute_pneg(atdi: float, ahifd: float, n_countries: int) -> float:
    """P(negotiation) — probability of successful resolution."""
    t1 = atdi / 100 * 0.30
    t2 = ahifd / 80 * 0.20
    t3 = min(0.10, (n_countries - 2) * 0.03)
    return round(max(0.05, min(0.95, 0.70 - t1 - t2 + t3)), 3)


def compute_nse_approx(atdi: float, ahifd: float, n_countries: int) -> float:
    """NSE pre-calibration estimate."""
    return round(max(0.1, min(0.9, 0.7 - atdi / 300 - ahifd / 200 - (n_countries - 2) * 0.04)), 2)


def compute_kge_approx(atdi: float, ahifd: float) -> float:
    """KGE pre-calibration estimate."""
    return round(max(0.1, min(0.9, 0.75 - atdi / 350 - ahifd / 250)), 2)


def compute_all(runoff_c: float, cap_bcm: float,
                n_countries: int, dispute_level: int) -> Dict:
    """Compute all 6 AWSI indices + helpers in one call."""
    atdi = compute_atdi(runoff_c, cap_bcm, n_countries, dispute_level)
    ahifd = compute_ahifd(runoff_c, cap_bcm, n_countries, dispute_level)
    ci = compute_conflict_index(atdi, ahifd, dispute_level, n_countries)
    # Legal-tier classification (UNWC 1997):
    # CRITICAL >=60 (Art.33 dispute settlement zone)
    # HIGH     >=40 (Art.7 No Significant Harm triggered)
    # MODERATE >=25 (Art.5 equitable-use attention)
    risk = ("CRITICAL" if atdi >= 60 else "HIGH" if atdi >= 40
            else "MODERATE" if atdi >= 25 else "LOW")
    arts = []
    if atdi >= 40:
        arts.append("Art.7")
    if ahifd >= 25:
        arts.append("Art.9")
    if atdi >= 55:
        arts.append("Art.33")
    if atdi >= 25:
        arts.append("Art.5")
    return {
        "atdi": atdi, "ahifd": ahifd,
        "afsf": compute_afsf(runoff_c, cap_bcm, n_countries, dispute_level),
        "ahlb": compute_ahlb(runoff_c, cap_bcm, n_countries, dispute_level),
        "asi": compute_asi(runoff_c, cap_bcm, n_countries, dispute_level),
        "atci": compute_atci(runoff_c, cap_bcm, n_countries, dispute_level),
        "ci": ci, "pneg": compute_pneg(atdi, ahifd, n_countries),
        "nse": compute_nse_approx(atdi, ahifd, n_countries),
        "kge": compute_kge_approx(atdi, ahifd),
        "wqi": round(max(30, min(90, 70 - atdi * 0.3 - ahifd * 0.2)), 1),
        "risk": risk, "articles": arts,
    }
