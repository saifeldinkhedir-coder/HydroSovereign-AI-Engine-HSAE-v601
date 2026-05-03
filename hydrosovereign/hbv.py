"""
hbv.py — HSAE v6.01 HBV-96 Hydrological Model
================================================
Physics-based rainfall-runoff model (Bergström, 1992)
with true SCE-UA calibration (Duan et al., 1992).

Author: Seifeldin M.G. Alkhedir · ORCID: 0000-0003-0821-2991
DOI:    10.5281/zenodo.19180160
"""

from __future__ import annotations
import numpy as np
from typing import Union, List, Optional, Dict

# ── Parameter bounds for SCE-UA ───────────────────────────────────────────────
_PARAM_BOUNDS = {
    "FC":   (50.0,  500.0),   # field capacity (mm)
    "LP":   (0.3,   1.0),     # ET limit fraction
    "BETA": (1.0,   5.0),     # recharge shape exponent
    "K1":   (0.01,  0.30),    # upper zone recession (1/day)
    "K2":   (0.001, 0.05),    # lower zone recession (1/day)
    "PERC": (0.1,   3.0),     # percolation (mm/day)
    "TT":   (-2.0,  2.0),     # snow threshold (°C)
    "CFMAX":(1.0,   8.0),     # melt factor (mm/°C/day)
}


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
        Runoff coefficient (0–1). Used for FC default. Default = 0.38.
    params : dict, optional
        HBV-96 parameters. If None, uses physics-based defaults.
        Keys: FC, LP, BETA, K1, K2, PERC, TT, CFMAX

    Returns
    -------
    dict
        - Q_sim  (ndarray) : daily discharge (m³/s)
        - SM     (ndarray) : soil moisture (mm)
        - AET    (ndarray) : actual evapotranspiration (mm/day)
        - SNOW   (ndarray) : snow water equivalent (mm)
        - SUZ    (ndarray) : upper zone storage (mm)
        - SLZ    (ndarray) : lower zone storage (mm)
        - n_days (int)     : simulation length

    Examples
    --------
    >>> import numpy as np
    >>> P = np.maximum(0, 2.5 * np.sin(np.pi * np.arange(365) / 180))
    >>> T = np.full(365, 25.0)
    >>> result = run_hbv96(P, T, area_km2=174000, runoff_c=0.38)
    >>> print(f"Mean Q = {result['Q_sim'].mean():.1f} m³/s")
    """
    P = np.asarray(P, dtype=float)
    T = np.asarray(T, dtype=float)
    n = len(P)

    if len(T) != n:
        raise ValueError(f"P (len={len(P)}) and T (len={len(T)}) must match")
    if area_km2 <= 0:
        raise ValueError(f"area_km2 must be > 0, got {area_km2}")
    if not 0 < runoff_c <= 1:
        raise ValueError(f"runoff_c must be in (0,1], got {runoff_c}")

    # Default parameters (physics-based)
    p = {
        "FC":    max(50.0, 250.0 * runoff_c),
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

    # Output arrays
    Q_arr   = np.zeros(n)
    SM_arr  = np.zeros(n)
    AET_arr = np.zeros(n)
    SNW_arr = np.zeros(n)
    SUZ_arr = np.zeros(n)
    SLZ_arr = np.zeros(n)

    # State variables
    SNOW = 0.0
    SM   = FC * 0.5
    SUZ  = 0.0
    SLZ  = 0.0

    for i in range(n):
        # ── Snow routine ──────────────────────────────────────
        if T[i] <= TT:
            SNOW += P[i]
            rain  = 0.0
        else:
            melt  = min(SNOW, CFMAX * (T[i] - TT))
            SNOW  = max(0.0, SNOW - melt)
            rain  = P[i] + melt

        # ── Soil moisture & ET ────────────────────────────────
        # Recharge to upper zone
        if SM > 0 and FC > 0:
            recharge = rain * (SM / FC) ** BETA
        else:
            recharge = 0.0

        # Actual ET (Hamon approach)
        lp_thresh = LP * FC
        if SM >= lp_thresh:
            AET_i = min(rain * 0.4, SM * 0.01)
        else:
            AET_i = (SM / (lp_thresh + 1e-12)) * min(rain * 0.4, SM * 0.01)

        SM  = max(0.0, min(FC, SM + rain - recharge - AET_i))

        # ── Groundwater routine ───────────────────────────────
        perc  = min(float(PERC), SUZ)
        SUZ   = max(0.0, SUZ + recharge - K1 * SUZ - perc)
        SLZ   = max(0.0, SLZ + perc - K2 * SLZ)

        # Discharge: mm/day → m³/s
        Q_mm      = K1 * SUZ + K2 * SLZ
        Q_arr[i]  = max(0.0, Q_mm * area_km2 * 1000.0 / 86400.0)
        SM_arr[i] = SM
        AET_arr[i]= AET_i
        SNW_arr[i]= SNOW
        SUZ_arr[i]= SUZ
        SLZ_arr[i]= SLZ

    return {
        "Q_sim":  Q_arr,
        "SM":     SM_arr,
        "AET":    AET_arr,
        "SNOW":   SNW_arr,
        "SUZ":    SUZ_arr,
        "SLZ":    SLZ_arr,
        "n_days": n,
    }


def calibrate_hbv_sceua(
    Q_obs: Union[np.ndarray, List[float]],
    P: Union[np.ndarray, List[float]],
    T: Union[np.ndarray, List[float]],
    area_km2: float,
    runoff_c: float = 0.38,
    n_complexes: int = 5,
    n_per_complex: int = 12,
    max_iter: int = 500,
    random_seed: int = 42,
) -> dict:
    """
    Calibrate HBV-96 using SCE-UA — Shuffled Complex Evolution
    (Duan, Sorooshian & Gupta, 1992).

    Algorithm:
    1. Generate initial population via Latin Hypercube Sampling (LHS)
    2. Partition into complexes
    3. Evolve each complex using Competitive Complex Evolution (CCE)
    4. Shuffle complexes and repeat until convergence

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
    n_complexes : int
        Number of complexes (p). Default = 5.
    n_per_complex : int
        Points per complex (m). Default = 12.
    max_iter : int
        Maximum iterations. Default = 500.
    random_seed : int
        Reproducibility seed. Default = 42.

    Returns
    -------
    dict
        - params    (dict)  : best calibrated parameters
        - nse       (float) : best NSE achieved
        - kge       (float) : corresponding KGE
        - n_eval    (int)   : function evaluations used
        - converged (bool)  : whether convergence criterion met

    Examples
    --------
    >>> result = calibrate_hbv_sceua(Q_obs, P, T, area_km2=174000)
    >>> print(f"Best NSE = {result['nse']:.3f}")
    >>> print(f"Best KGE = {result['kge']:.3f}")
    """
    from .indices import compute_nse, compute_kge

    Q_obs = np.asarray(Q_obs, dtype=float)
    P     = np.asarray(P,     dtype=float)
    T     = np.asarray(T,     dtype=float)

    rng         = np.random.default_rng(random_seed)
    param_names = list(_PARAM_BOUNDS.keys())
    n_params    = len(param_names)
    n_pop       = n_complexes * n_per_complex  # total population

    # ── Helper: evaluate objective (1 - NSE) ──────────────────
    def _obj(pdict):
        try:
            res  = run_hbv96(P, T, area_km2, runoff_c, pdict)
            n    = min(len(Q_obs), len(res["Q_sim"]))
            nse  = compute_nse(Q_obs[:n], res["Q_sim"][:n])
            return 1.0 - nse   # minimize
        except Exception:
            return 999.0

    def _arr_to_dict(arr):
        return {k: float(lo + arr[i] * (hi - lo))
                for i, (k, (lo, hi)) in enumerate(_PARAM_BOUNDS.items())}

    def _dict_to_arr(d):
        return np.array([(d[k] - lo) / (hi - lo)
                         for k, (lo, hi) in _PARAM_BOUNDS.items()])

    # ── Step 1: LHS initial population ────────────────────────
    pop_arr = np.zeros((n_pop, n_params))
    for j in range(n_params):
        perm = rng.permutation(n_pop)
        pop_arr[:, j] = (perm + rng.random(n_pop)) / n_pop

    pop_cost = np.array([_obj(_arr_to_dict(pop_arr[i])) for i in range(n_pop)])
    n_eval   = n_pop

    # ── SCE-UA main loop ───────────────────────────────────────
    for iteration in range(max_iter):
        # Sort by cost (ascending)
        idx     = np.argsort(pop_cost)
        pop_arr = pop_arr[idx]
        pop_cost= pop_cost[idx]

        # Convergence check
        if pop_cost[-1] - pop_cost[0] < 1e-6:
            break

        # Partition into complexes
        complexes_arr  = [pop_arr[k::n_complexes]  for k in range(n_complexes)]
        complexes_cost = [pop_cost[k::n_complexes] for k in range(n_complexes)]

        # Evolve each complex (CCE)
        for k in range(n_complexes):
            c_arr  = complexes_arr[k].copy()
            c_cost = complexes_cost[k].copy()
            n_c    = len(c_arr)

            for _ in range(n_params + 1):
                # Triangular probability weighting
                probs = np.array([2.0 * (n_c - j) / (n_c * (n_c + 1))
                                   for j in range(n_c)])
                probs /= probs.sum()

                # Select parents
                chosen = rng.choice(n_c, size=min(n_params, n_c),
                                    replace=False, p=probs)
                chosen = np.sort(chosen)

                # Centroid of all but worst parent
                sub_arr = c_arr[chosen]
                centroid = sub_arr[:-1].mean(axis=0)

                # Reflection
                worst  = sub_arr[-1]
                child  = np.clip(2.0 * centroid - worst, 0.0, 1.0)
                c_child = _obj(_arr_to_dict(child))
                n_eval += 1

                if c_child < c_cost[chosen[-1]]:
                    c_arr[chosen[-1]]  = child
                    c_cost[chosen[-1]] = c_child
                else:
                    # Random point inside simplex
                    child  = rng.random(n_params)
                    c_child = _obj(_arr_to_dict(child))
                    n_eval += 1
                    c_arr[chosen[-1]]  = child
                    c_cost[chosen[-1]] = c_child

            complexes_arr[k]  = c_arr
            complexes_cost[k] = c_cost

        # Shuffle: reassemble population
        for k in range(n_complexes):
            pop_arr[k::n_complexes]  = complexes_arr[k]
            pop_cost[k::n_complexes] = complexes_cost[k]

    # Final sort
    idx      = np.argsort(pop_cost)
    best_arr = pop_arr[idx[0]]
    best_p   = _arr_to_dict(best_arr)

    # Compute final NSE and KGE
    res     = run_hbv96(P, T, area_km2, runoff_c, best_p)
    n_min   = min(len(Q_obs), len(res["Q_sim"]))
    best_nse= compute_nse(Q_obs[:n_min], res["Q_sim"][:n_min])
    best_kge= compute_kge(Q_obs[:n_min], res["Q_sim"][:n_min])

    return {
        "params":    best_p,
        "nse":       round(best_nse, 4),
        "kge":       round(best_kge, 4),
        "n_eval":    n_eval,
        "converged": (pop_cost[-1] - pop_cost[0]) < 1e-6,
    }
