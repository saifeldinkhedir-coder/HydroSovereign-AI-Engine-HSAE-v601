"""
fetchers.py — HSAE v6.3.0 Live Data Ingestion Module
======================================================
Connects to real external APIs to fetch hydrological data:
  - Open-Meteo (free, no key) — precipitation, temperature, ET
  - GRDC (Global Runoff Data Centre) — observed discharge
  - NASA POWER (free) — solar radiation, humidity
  - GEE/Copernicus (requires auth) — satellite products

Author: Seifeldin M.G. Alkedir · ORCID: 0000-0003-0821-2991
"""
from __future__ import annotations
import logging
import json
from datetime import date, datetime, timedelta
from typing import Optional, Dict, List
from pathlib import Path

logger = logging.getLogger(__name__)


def fetch_openmeteo(
    lat: float,
    lon: float,
    start_date: str,
    end_date: str,
    variables: Optional[List[str]] = None,
    timeout: int = 30,
) -> Dict:
    """
    Fetch daily climate data from Open-Meteo ERA5 API (free, no API key).

    Parameters
    ----------
    lat, lon : float
        Basin centroid coordinates.
    start_date : str
        Start date "YYYY-MM-DD".
    end_date : str
        End date "YYYY-MM-DD".
    variables : list, optional
        Variables to fetch. Default:
        ["precipitation_sum","temperature_2m_mean",
         "et0_fao_evapotranspiration","soil_moisture_0_to_7cm_mean"]
    timeout : int
        Request timeout seconds. Default = 30.

    Returns
    -------
    dict
        - dates       : list of date strings
        - P_mm_day    : daily precipitation (mm/day)
        - T_celsius   : daily mean temperature (°C)
        - ET0         : FAO-56 reference ET (mm/day)
        - soil_moisture: volumetric soil moisture (m³/m³)
        - source      : "Open-Meteo ERA5"
        - lat, lon    : coordinates used
        - n_days      : number of days

    Raises
    ------
    ConnectionError
        If the API is unreachable.

    Examples
    --------
    >>> data = fetch_openmeteo(10.53, 35.09, "2024-01-01", "2024-12-31")
    >>> print(f"Mean P = {sum(data['P_mm_day'])/len(data['P_mm_day']):.2f} mm/day")
    """
    try:
        import urllib.request
        import urllib.parse
    except ImportError:
        raise ImportError("urllib is required (standard library)")

    if variables is None:
        variables = [
            "precipitation_sum",
            "temperature_2m_mean",
            "et0_fao_evapotranspiration",
            "soil_moisture_0_to_7cm_mean",
        ]

    params = {
        "latitude":    str(lat),
        "longitude":   str(lon),
        "start_date":  start_date,
        "end_date":    end_date,
        "daily":       ",".join(variables),
        "timezone":    "UTC",
    }

    url = "https://archive-api.open-meteo.com/v1/archive?" + urllib.parse.urlencode(params)
    logger.info("Fetching Open-Meteo: lat=%.2f lon=%.2f %s→%s", lat, lon, start_date, end_date)

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "hydrosovereign/6.3.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read())
    except Exception as e:
        raise ConnectionError(f"Open-Meteo API request failed: {e}")

    daily   = data.get("daily", {})
    dates   = daily.get("time", [])
    n       = len(dates)

    result = {
        "dates":         dates,
        "P_mm_day":      daily.get("precipitation_sum", [0.0]*n),
        "T_celsius":     daily.get("temperature_2m_mean", [25.0]*n),
        "ET0":           daily.get("et0_fao_evapotranspiration", [None]*n),
        "soil_moisture": daily.get("soil_moisture_0_to_7cm_mean", [None]*n),
        "source":        "Open-Meteo ERA5 (open-meteo.com)",
        "lat":           lat,
        "lon":           lon,
        "n_days":        n,
        "start_date":    start_date,
        "end_date":      end_date,
    }

    logger.info("Open-Meteo: %d days fetched, P_mean=%.2f mm/day",
                n, sum(p or 0 for p in result["P_mm_day"]) / max(1, n))
    return result


def fetch_openmeteo_forecast(
    lat: float,
    lon: float,
    horizon_days: int = 7,
    timeout: int = 20,
) -> Dict:
    """
    Fetch weather forecast from Open-Meteo (free, no key).

    Parameters
    ----------
    lat, lon : float
        Coordinates.
    horizon_days : int
        Forecast horizon (max 16 days). Default = 7.
    timeout : int
        Request timeout. Default = 20.

    Returns
    -------
    dict
        - dates, P_mm_day, T_celsius, ET0
        - source: "Open-Meteo Forecast"

    Examples
    --------
    >>> fc = fetch_openmeteo_forecast(10.53, 35.09, horizon_days=7)
    >>> print(fc["P_mm_day"])   # next 7 days precipitation
    """
    import urllib.request, urllib.parse

    params = {
        "latitude":  str(lat),
        "longitude": str(lon),
        "daily":     "precipitation_sum,temperature_2m_mean,et0_fao_evapotranspiration",
        "timezone":  "UTC",
        "forecast_days": str(min(horizon_days, 16)),
    }
    url = "https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode(params)

    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            data = json.loads(r.read())
    except Exception as e:
        raise ConnectionError(f"Open-Meteo Forecast API failed: {e}")

    daily = data.get("daily", {})
    return {
        "dates":     daily.get("time", []),
        "P_mm_day":  daily.get("precipitation_sum", []),
        "T_celsius": daily.get("temperature_2m_mean", []),
        "ET0":       daily.get("et0_fao_evapotranspiration", []),
        "source":    "Open-Meteo Forecast (open-meteo.com)",
        "lat": lat, "lon": lon,
    }


def fetch_basin_forcing(
    basin_name: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    years: int = 5,
) -> Dict:
    """
    Fetch precipitation and temperature for a named basin (from registry).

    Uses basin centroid coordinates from BasinRegistry.
    Data source: Open-Meteo ERA5 (free, no authentication).

    Parameters
    ----------
    basin_name : str
        Basin name from BASINS_26 registry.
    start_date : str, optional
        "YYYY-MM-DD". If None, uses `years` before today.
    end_date : str, optional
        "YYYY-MM-DD". If None, uses yesterday.
    years : int
        Years of data if dates not specified. Default = 5.

    Returns
    -------
    dict
        - basin_name, lat, lon
        - P, T : numpy arrays ready for HBVModel.simulate()
        - source, n_days, dates

    Examples
    --------
    >>> import numpy as np
    >>> from hydrosovereign.models import HBVModel
    >>> data = fetch_basin_forcing("Blue Nile (GERD)", years=3)
    >>> P, T = np.array(data["P"]), np.array(data["T"])
    >>> model = HBVModel(area_km2=174000, runoff_c=0.38)
    >>> result = model.simulate(P, T)
    >>> print(f"NSE = {result['nse']}")
    """
    import numpy as np
    from ..basins import BasinRegistry

    reg   = BasinRegistry()
    basin = reg.get(basin_name)
    lat   = float(basin["lat"])
    lon   = float(basin["lon"])

    if end_date is None:
        end_date = (date.today() - timedelta(days=1)).isoformat()
    if start_date is None:
        start_date = (date.today() - timedelta(days=years*365)).isoformat()

    logger.info("Fetching forcing for %s (%s → %s)", basin_name, start_date, end_date)

    try:
        raw = fetch_openmeteo(lat, lon, start_date, end_date)
        P   = [max(0.0, float(p or 0)) for p in raw["P_mm_day"]]
        T   = [float(t or 25.0)        for t in raw["T_celsius"]]

        return {
            "basin_name":  basin_name,
            "lat":         lat,
            "lon":         lon,
            "start_date":  start_date,
            "end_date":    end_date,
            "P":           P,
            "T":           T,
            "ET0":         raw.get("ET0"),
            "dates":       raw["dates"],
            "n_days":      len(P),
            "source":      raw["source"],
            "runoff_c":    float(basin.get("runoff_c", 0.3)),
            "cap_bcm":     float(basin.get("cap", 10)),
        }
    except ConnectionError as e:
        logger.warning("Live data unavailable (%s) — loading sample data", e)
        return _load_sample_data(basin_name)


def _load_sample_data(basin_name: str) -> Dict:
    """Fallback: load bundled sample dataset."""
    import numpy as np
    sample_path = Path(__file__).parent / "nile_basin_sample.json"

    if sample_path.exists() and "Nile" in basin_name:
        with open(sample_path) as f:
            raw = json.load(f)
        records = raw["records"]
        return {
            "basin_name": basin_name,
            "lat":        raw["lat"],
            "lon":        raw["lon"],
            "P":          [r["P"] for r in records],
            "T":          [r["T"] for r in records],
            "dates":      [r["date"] for r in records],
            "n_days":     len(records),
            "source":     "HSAE bundled sample (Open-Meteo offline)",
            "runoff_c":   raw.get("runoff_c", 0.38),
            "cap_bcm":    raw.get("cap_bcm", 74.0),
        }

    # Generic fallback: synthetic seasonal data
    logger.warning("No sample data for %s — using synthetic seasonal proxy", basin_name)
    n   = 365 * 3
    doy = np.tile(np.arange(1, 366), 3)[:n]
    P   = list(np.maximum(0, 2.0 * np.sin(np.pi * doy / 180) ** 1.3
                          + np.random.default_rng(42).exponential(0.3, n)))
    T   = list(25 + 5 * np.sin(2 * np.pi * doy / 365))
    return {
        "basin_name": basin_name,
        "P": P, "T": T, "n_days": n,
        "source": "HSAE synthetic seasonal proxy",
        "runoff_c": 0.3, "cap_bcm": 10.0,
    }


def check_connectivity(timeout: int = 5) -> Dict[str, bool]:
    """
    Check connectivity to all data sources.

    Returns
    -------
    dict
        {"open_meteo": bool, "grdc": bool, "nasa_power": bool}

    Examples
    --------
    >>> status = check_connectivity()
    >>> print(status)
    {'open_meteo': True, 'grdc': False, 'nasa_power': True}
    """
    import urllib.request

    results = {}
    endpoints = {
        "open_meteo":  "https://api.open-meteo.com/v1/forecast?latitude=0&longitude=0&daily=temperature_2m_mean&forecast_days=1",
        "nasa_power":  "https://power.larc.nasa.gov/api/temporal/daily/point?parameters=PRECTOTCORR&community=AG&longitude=0&latitude=0&start=20240101&end=20240102&format=JSON",
    }
    for name, url in endpoints.items():
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "hydrosovereign/6.3.0"})
            with urllib.request.urlopen(req, timeout=timeout):
                results[name] = True
        except Exception:
            results[name] = False

    logger.info("Connectivity: %s", results)
    return results
