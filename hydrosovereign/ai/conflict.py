"""
conflict.py — HSAE v6.2.0 Dynamic Conflict Predictor
======================================================
Basin sensitivity calculated dynamically from aridity index,
drought frequency, and storage ratio — NOT hardcoded per basin.

Author: Seifeldin M.G. Alkedir · ORCID: 0000-0003-0821-2991
"""
from __future__ import annotations
import logging
import numpy as np

logger = logging.getLogger(__name__)


class ConflictPredictor:
    """
    Dynamic conflict risk predictor with computed basin sensitivity.

    Sensitivity is computed from basin metadata rather than hardcoded
    per-basin lookup — works for any basin including unlisted ones.

    Formula:
        sensitivity = 1 + w_arid*(1-runoff_c) + w_stor*(cap/area_norm) + w_nc*(nc-2)/8

    Examples
    --------
    >>> cp = ConflictPredictor()
    >>> r  = cp.predict("Blue Nile (GERD)", atdi=53.5, hifd=33.4,
    ...                  runoff_c=0.38, cap_bcm=74.0, area_km2=174000,
    ...                  dispute_level=4, n_countries=3)
    >>> print(r['conflict_index'], r['dynamic_alert'])
    """

    def __init__(self):
        self._w = {"atdi":0.40,"hifd":0.20,"dispute":0.25,"countries":0.15}
        # Dynamic sensitivity weights (calibrated)
        self._ws = {"aridity":0.35, "storage_density":0.30, "countries":0.20, "dispute":0.15}

    def _compute_sensitivity(self, runoff_c, cap_bcm, area_km2, n_countries, dispute_level):
        """
        Compute basin sensitivity dynamically from physical/geopolitical metadata.

        High aridity + high storage density + many countries = higher sensitivity.
        """
        aridity_idx    = max(0.0, 1.0 - runoff_c)                 # 0 (humid) → 1 (arid)
        storage_density= min(1.0, cap_bcm / max(area_km2/10000,1))# BCM per 10k km²
        nc_factor      = min(1.0, max(0, n_countries-2) / 8.0)
        disp_factor    = dispute_level / 4.0
        sensitivity    = (1.0
                        + self._ws["aridity"]          * aridity_idx
                        + self._ws["storage_density"]  * storage_density
                        + self._ws["countries"]        * nc_factor
                        + self._ws["dispute"]          * disp_factor)
        return round(float(np.clip(sensitivity, 0.8, 2.0)), 3)

    def predict(self, basin_name, atdi, hifd, runoff_c, dispute_level,
                n_countries=2, cap_bcm=10.0, area_km2=100000, climate_ssp=0.0):
        """
        Compute conflict index with dynamic sensitivity.

        Parameters
        ----------
        basin_name : str
            Basin name (for logging only — no longer used for lookup).
        atdi : float
            ATDI percentage (5–95).
        hifd : float
            HIFD percentage (5–80).
        runoff_c : float
            Runoff coefficient (0–1). Used to compute aridity sensitivity.
        dispute_level : int
            Dispute level 0–4.
        n_countries : int
            Riparian states. Default = 2.
        cap_bcm : float
            Storage capacity BCM. Default = 10.
        area_km2 : float
            Catchment area. Default = 100,000.
        climate_ssp : float
            SSP stress factor 0–1. Default = 0.

        Returns
        -------
        dict
            conflict_index, dynamic_alert, sensitivity, components,
            ssp_adjusted_ci, dynamic_thresholds.
        """
        sensitivity = self._compute_sensitivity(runoff_c, cap_bcm, area_km2, n_countries, dispute_level)

        ci_base = (self._w["atdi"]     * atdi     / 95.0
                 + self._w["hifd"]     * hifd     / 80.0
                 + self._w["dispute"]  * dispute_level / 4.0
                 + self._w["countries"]* min(1.0, max(0, n_countries-2) / 8.0))

        ci      = float(np.clip(ci_base * sensitivity, 0.0, 1.0))
        ci_ssp  = float(np.clip(ci + climate_ssp*0.12, 0.0, 1.0))

        # Dynamic thresholds — scale with aridity
        arid_f = 1.0 - runoff_c*0.25
        t_crit = float(np.clip(0.70/arid_f, 0.55, 0.90))
        t_high = float(np.clip(0.50/arid_f, 0.35, 0.70))
        t_med  = float(np.clip(0.30/arid_f, 0.20, 0.50))

        dynamic = ("CRITICAL" if ci >= t_crit else "HIGH" if ci >= t_high
                   else "MEDIUM" if ci >= t_med else "LOW")
        static  = ("CRITICAL" if ci >= 0.60 else "HIGH" if ci >= 0.40
                   else "MEDIUM" if ci >= 0.25 else "LOW")

        logger.debug("ConflictPredictor %s: CI=%.3f sensitivity=%.3f dynamic=%s",
                     basin_name, ci, sensitivity, dynamic)

        return {
            "conflict_index":   round(ci, 3),
            "dynamic_alert":    dynamic,
            "static_alert":     static,
            "sensitivity":      sensitivity,
            "ssp_adjusted_ci":  round(ci_ssp, 3),
            "components": {
                "atdi_contrib":    round(self._w["atdi"]*atdi/95, 3),
                "hifd_contrib":    round(self._w["hifd"]*hifd/80, 3),
                "dispute_contrib": round(self._w["dispute"]*dispute_level/4, 3),
                "country_contrib": round(self._w["countries"]*min(1,max(0,n_countries-2)/8), 3),
            },
            "dynamic_thresholds":{"critical":round(t_crit,2),"high":round(t_high,2),"medium":round(t_med,2)},
        }

    def rank_basins(self, basins):
        """Rank list of basin dicts by conflict_index descending."""
        results = []
        for b in basins:
            r = self.predict(
                basin_name    = b.get("name",""),
                atdi          = b.get("atdi", 30),
                hifd          = b.get("hifd", 15),
                runoff_c      = float(b.get("runoff_c", 0.3)),
                dispute_level = int(b.get("dispute_level", 0)),
                n_countries   = int(b.get("n_countries", len(b.get("country",["?","?"])) if isinstance(b.get("country"),list) else 2)),
                cap_bcm       = float(b.get("cap", b.get("cap_bcm", 10))),
                area_km2      = float(b.get("eff_cat_km2", b.get("area_km2", 100000))),
            )
            r["name"] = b.get("name","")
            results.append(r)
        return sorted(results, key=lambda x: x["conflict_index"], reverse=True)

    def __repr__(self):
        return "ConflictPredictor(dynamic_sensitivity=True, no_hardcoding)"
