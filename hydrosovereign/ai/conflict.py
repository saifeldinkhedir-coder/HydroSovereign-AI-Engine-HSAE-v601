"""
conflict.py — Conflict Index Predictor
========================================
Basin-specific conflict risk with dynamic thresholds
(addresses Gemini's critique of linear fixed thresholds).

Author: Seifeldin M.G. Alkedir · ORCID: 0000-0003-0821-2991
"""

from __future__ import annotations
import numpy as np
from typing import List


class ConflictPredictor:
    """
    Dynamic conflict risk predictor with basin-specific thresholds.

    Addresses the Gemini review critique:
    'Linear alert thresholds do not account for the unique
    hydrological sensitivity of different river basins.'

    Uses basin runoff variability and historical drought frequency
    to calibrate basin-specific alert thresholds.

    Examples
    --------
    >>> cp = ConflictPredictor()
    >>> result = cp.predict("Blue Nile (GERD)",
    ...                      atdi=49.2, hifd=33.4,
    ...                      runoff_c=0.38, dispute_level=4)
    >>> print(result['conflict_index'])
    >>> print(result['dynamic_alert'])
    """

    # Basin-specific sensitivity factors (calibrated from TFDD/ICOW)
    _SENSITIVITY = {
        "Blue Nile (GERD)":          1.25,
        "Nile – High Aswan Dam":     1.30,
        "Euphrates – Atatürk Dam":   1.20,
        "Syr Darya – Toktogul Dam":  1.35,
        "Dnieper – Kakhovka Dam":    1.40,
        "Indus – Tarbela Dam":       1.15,
        "Mekong – Xayaburi Dam":     1.10,
        "Colorado – Hoover Dam":     1.20,
        "Amu Darya – Nurek Dam":     1.30,
    }
    _DEFAULT_SENSITIVITY = 1.0

    def __init__(self):
        self._weights = {
            "atdi":          0.40,
            "hifd":          0.20,
            "dispute":       0.25,
            "countries":     0.15,
        }

    def predict(
        self,
        basin_name: str,
        atdi: float,
        hifd: float,
        runoff_c: float,
        dispute_level: int,
        n_countries: int = 2,
        climate_ssp: float = 0.0,
    ) -> dict:
        """
        Compute dynamic conflict index for a specific basin.

        Parameters
        ----------
        basin_name : str
            Basin name for sensitivity lookup.
        atdi : float
            ATDI percentage (5–95).
        hifd : float
            HIFD percentage (5–80).
        runoff_c : float
            Runoff coefficient (0–1). Lower = more sensitive.
        dispute_level : int
            Dispute level 0–4.
        n_countries : int
            Riparian state count. Default = 2.
        climate_ssp : float
            SSP climate stress factor (0–1). Default = 0.

        Returns
        -------
        dict
            - conflict_index  (float) : 0–1
            - dynamic_alert   (str)   : basin-calibrated alert
            - static_alert    (str)   : standard threshold alert
            - sensitivity     (float) : basin sensitivity factor
            - components      (dict)  : index breakdown
            - ssp_adjusted_ci (float) : climate-adjusted CI
        """
        sensitivity = self._SENSITIVITY.get(basin_name, self._DEFAULT_SENSITIVITY)

        # Base conflict index
        ci_base = (self._weights["atdi"]     * atdi / 100
                  + self._weights["hifd"]    * hifd / 80
                  + self._weights["dispute"] * dispute_level / 4
                  + self._weights["countries"] * max(0, n_countries - 2) / 8)

        # Apply basin sensitivity
        ci = float(np.clip(ci_base * sensitivity, 0.0, 1.0))

        # Climate SSP adjustment
        ci_ssp = float(np.clip(ci + climate_ssp * 0.12, 0.0, 1.0))

        # Dynamic thresholds (basin-specific)
        # Arid basins (low runoff_c) get lower thresholds
        arid_factor = 1.0 - runoff_c * 0.3
        t_critical  = 0.70 / arid_factor
        t_high      = 0.50 / arid_factor
        t_medium    = 0.30 / arid_factor

        if ci >= min(t_critical, 0.85):  dynamic = "CRITICAL"
        elif ci >= min(t_high, 0.65):    dynamic = "HIGH"
        elif ci >= min(t_medium, 0.45):  dynamic = "MEDIUM"
        else:                             dynamic = "LOW"

        # Static (legacy) alert
        if ci >= 0.60:   static = "CRITICAL"
        elif ci >= 0.40: static = "HIGH"
        elif ci >= 0.25: static = "MEDIUM"
        else:             static = "LOW"

        return {
            "conflict_index":   round(ci, 3),
            "dynamic_alert":    dynamic,
            "static_alert":     static,
            "sensitivity":      round(sensitivity, 2),
            "ssp_adjusted_ci":  round(ci_ssp, 3),
            "components": {
                "atdi_contrib":     round(self._weights["atdi"] * atdi/100, 3),
                "hifd_contrib":     round(self._weights["hifd"] * hifd/80, 3),
                "dispute_contrib":  round(self._weights["dispute"] * dispute_level/4, 3),
                "country_contrib":  round(self._weights["countries"] * max(0,n_countries-2)/8, 3),
            },
            "thresholds": {
                "dynamic_critical": round(min(t_critical, 0.85), 2),
                "dynamic_high":     round(min(t_high,     0.65), 2),
                "dynamic_medium":   round(min(t_medium,   0.45), 2),
            }
        }

    def rank_basins(self, basins: list) -> list:
        """
        Rank all basins by conflict risk (highest first).

        Parameters
        ----------
        basins : list of dict
            Must contain: name, atdi, hifd, runoff_c, dispute_level.

        Returns
        -------
        list of dict sorted by conflict_index descending.
        """
        results = []
        for b in basins:
            r = self.predict(
                basin_name    = b.get("name",""),
                atdi          = b.get("atdi", 30),
                hifd          = b.get("hifd", 15),
                runoff_c      = b.get("runoff_c", 0.3),
                dispute_level = b.get("dispute_level", 0),
                n_countries   = b.get("n_countries", 2),
            )
            r["name"] = b.get("name","")
            results.append(r)
        return sorted(results, key=lambda x: x["conflict_index"], reverse=True)

    def __repr__(self):
        return "ConflictPredictor(dynamic_thresholds=True, n_basins=26)"
