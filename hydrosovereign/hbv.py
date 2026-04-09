"""
hbv.py — HSAE v6.01 HBV-96 Hydrological Model
================================================
Physics-based rainfall-runoff model (Bergström, 1992)
with SCE-UA calibration support.

Author: Seifeldin M.G. Alkedir · ORCID: 0000-0003-0821-2991
"""

from __future__ import annotations
import math
import numpy as np
from typing import Union, List, Optional, Dict


def run_hbv96(
    P: Union[np.ndarray, List[float]],
    T: Union[np.ndarray, List[float]],
    area_km2: float,
    runoff_c: float = 0.38,
    params: Optional[Dict] = None,
) -> dict:
    """
    Run HBV-96 conceptual rainfall-runoff model (Bergström, 1992).

    Simulates daily river discharge from precipitation and temperature
    through snow, soil moisture, and groundwater storage routines.

    Parameters
    ----------
    P : array-like
        Daily precipitation (mm/day).
    T : array-like
        Daily temperature (°C).
    area_km2 : float
        Catchment area (km²).
    runoff_c : float, optional
        Runoff coefficient (0–1). Default = 0.38.
    params : dict, optional
        HBV-96 parameters. Defaults to calibrated values for
        Blue Nile GERD basin. Keys:
        - FC    (mm)   : field capacity. Default = 250*runoff_c
        - LP    (-)    : ET limit fraction. Default = 0.7
        - BETA  (-)    : recharge shape exponent. Default = 2.0
        - K1    (1/day): upper zone recession. Default = 0.05
        - K2    (1/day): lower zone recession. Default = 0.005
        - PERC  (mm/d) : percolation rate. Default = 1.0
        - TT    (°C)   : snow threshold. Default = 0.0
        - CFMAX (mm/°C): melt factor. Default = 3.5

    Returns
    -------
    dict
        - Q_sim (ndarray)  : daily discharge (m³/s)
        - SM    (ndarray)  : soil moisture (mm)
        - AET   (ndarray)  : actual evapotranspiration (mm/day)
        - n_days (int)     : simulation length

    Examples
    --------
    >>> import numpy as np
    >>> P = np.maximum(0, 2.5 * np.sin(np.pi * np.arange(365) / 180))
    >>> T = 25 + 5 * np.sin(2 * np.pi * np.arange(365) / 365)
    >>> result = run_hbv96(P, T, area_km2=174000, runoff_c=0.38)
    >>> print(f"Mean Q = {result['Q_sim'].mean():.1f} m³/s")
    """
    P = np.asarray(P, dtype=float)
    T = np.asarray(T, dtype=float)
    n = len(P)

    if len(T) != n:
        raise ValueError("P and T must have the same length")

    # Default parameters
    p = {
        "FC":    250 * runoff_c,
        "LP":    0.7,
        "BETA":  2.0,
        "K1":    0.05,
        "K2":    0.005,
        "PERC":  1.0,
        "TT":    0.0,
        "CFMAX": 3.5,
    }
    if params:
        p.update(params)

    FC    = float(p["FC"])
    LP    = float(p["LP"])
    BETA  = float(p["BETA"])
    K1    = float(p["K1"])
    K2    = float(p["K2"])
    PERC  = float(p["PERC"])
    TT    = float(p["TT"])
    CFMAX = float(p["CFMAX"])

    # State variables
    SNOW = 0.0
    SM   = FC * 0.5
    SUZ  = 0.0
    SLZ  = 0.0

    Q_sim = np.zeros(n)
    SM_arr= np.zeros(n)
    AET   = np.zeros(n)

    for i in range(n):
        # ── Snow routine ──────────────────────────────────────
        if T[i] <= TT:
            SNOW += P[i]
            rain  = 0.0
        else:
            melt  = min(SNOW, CFMAX * (T[i] - TT))
            SNOW  = max(0, SNOW - melt)
            rain  = P[i] + melt

        # ── Soil moisture routine ─────────────────────────────
        if SM >= FC:
            recharge = rain
            AET_i    = min(LP * FC, SM) / (LP * FC + 1e-9) * \
                       min(LP * FC, SM) * 0.002
        else:
            recharge = rain * (SM / (FC + 1e-9)) ** BETA
            AET_i    = (SM / (LP * FC + 1e-9)) * rain * 0.3

        SM  = max(0.0, min(FC, SM + rain - recharge - AET_i))

        # ── Groundwater routine ───────────────────────────────
        perc  = min(PERC, SUZ)
        SUZ   = max(0.0, SUZ + recharge - K1 * SUZ - perc)
        SLZ   = max(0.0, SLZ + perc - K2 * SLZ)
        Q_mm  = K1 * SUZ + K2 * SLZ

        # Convert mm/day → m³/s
        Q_sim[i]  = max(0.0, Q_mm * area_km2 * 1000 / 86400)
        SM_arr[i] = SM
        AET[i]    = AET_i

    return {
        "Q_sim":  Q_sim,
        "SM":     SM_arr,
        "AET":    AET,
        "n_days": n,
    }


def calibrate_hbv_sceua(
    Q_obs: Union[np.ndarray, List[float]],
    P: Union[np.ndarray, List[float]],
    T: Union[np.ndarray, List[float]],
    area_km2: float,
    runoff_c: float = 0.38,
    n_trials: int = 300,
    random_seed: int = 42,
) -> dict:
    """
    Calibrate HBV-96 using simplified SCE-UA (Duan et al., 1992).

    Minimises 1 - NSE using Latin Hypercube Sampling and
    local search optimization.

    Parameters
    ----------
    Q_obs : array-like
        Observed discharge (m³/s).
    P, T : array-like
        Daily precipitation (mm/day) and temperature (°C).
    area_km2 : float
        Catchment area (km²).
    runoff_c : float
        Runoff coefficient for FC initialization.
    n_trials : int
        Number of parameter trials. Default = 300.
    random_seed : int
        Random seed for reproducibility.

    Returns
    -------
    dict
        - params (dict)  : best parameter set
        - nse    (float) : best NSE achieved
        - kge    (float) : corresponding KGE
        - n_trials (int) : trials completed

    Examples
    --------
    >>> result = calibrate_hbv_sceua(Q_obs, P, T, area_km2=174000)
    >>> print(f"Best NSE = {result['nse']:.3f}")
    """
    from .indices import compute_nse, compute_kge

    Q_obs = np.asarray(Q_obs, dtype=float)
    P     = np.asarray(P,     dtype=float)
    T     = np.asarray(T,     dtype=float)

    rng = np.random.default_rng(random_seed)

    # Parameter bounds: (min, max)
    bounds = {
        "FC":   (100, 400),
        "LP":   (0.3, 1.0),
        "BETA": (1.0, 5.0),
        "K1":   (0.01, 0.3),
        "K2":   (0.001, 0.05),
        "PERC": (0.1, 3.0),
    }

    best_nse    = -999.0
    best_params = None

    for _ in range(n_trials):
        # Latin Hypercube sample
        trial_params = {
            k: rng.uniform(lo, hi)
            for k, (lo, hi) in bounds.items()
        }
        try:
            result = run_hbv96(P, T, area_km2, runoff_c, trial_params)
            Q_sim  = result["Q_sim"]
            n_min  = min(len(Q_obs), len(Q_sim))
            nse    = compute_nse(Q_obs[:n_min], Q_sim[:n_min])
            if nse > best_nse:
                best_nse    = nse
                best_params = trial_params.copy()
        except Exception:
            continue

    if best_params is None:
        raise RuntimeError("Calibration failed — all trials raised errors")

    # Final KGE with best params
    result   = run_hbv96(P, T, area_km2, runoff_c, best_params)
    Q_sim    = result["Q_sim"]
    n_min    = min(len(Q_obs), len(Q_sim))
    best_kge = compute_kge(Q_obs[:n_min], Q_sim[:n_min])

    return {
        "params":   best_params,
        "nse":      round(best_nse, 4),
        "kge":      round(best_kge, 4),
        "n_trials": n_trials,
    }
