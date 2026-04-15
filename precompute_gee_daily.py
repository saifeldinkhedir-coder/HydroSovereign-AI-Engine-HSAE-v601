#!/usr/bin/env python3
"""
HSAE v6.01 — Daily GEE Pre-computation Pipeline
================================================
Runs via GitHub Actions every day at 06:00 UTC.
Fetches REAL satellite + Open-Meteo data for all basins.
Saves to data/gee_realtime.json

Sources:
  - GPM IMERG V07: NASA/GPM_L3/IMERG_V07 (via GEE)
  - GRACE-FO: NASA/GRACE/MASS_GRIDS_V04/LAND (via GEE, 2022-2023)
  - Temperature, Precipitation, Soil Moisture: Open-Meteo ERA5
  - Discharge: derived from P × runoff_c × area
"""

import ee, json, os, datetime, time, urllib.request
import numpy as np
from pathlib import Path

# ── Auth ──────────────────────────────────────────────────────────────────────
SA_KEY   = os.environ.get("GEE_SA_KEY_PATH", "hsae-gee-service.json")
SA_EMAIL = "hsae-gee-service@zinc-arc-484714-j8.iam.gserviceaccount.com"
PROJECT  = "zinc-arc-484714-j8"
credentials = ee.ServiceAccountCredentials(SA_EMAIL, SA_KEY)
ee.Initialize(credentials, project=PROJECT)
print(f"✅ GEE authenticated: {PROJECT}")

# ── Basin Registry ────────────────────────────────────────────────────────────
BASINS = {
    "blue_nile_gerd":    {"bbox":[33.0,8.0,37.5,13.0], "lat":10.53,"lon":35.09,
                          "area_km2":174000,"runoff_c":0.38,"cap":74.0},
    "nile_aswan":        {"bbox":[30.0,20.0,34.0,24.0], "lat":23.97,"lon":32.88,
                          "area_km2":2900000,"runoff_c":0.10,"cap":162.0},
    "euphrates_ataturk": {"bbox":[36.0,37.0,40.0,40.0], "lat":37.48,"lon":38.35,
                          "area_km2":444000,"runoff_c":0.20,"cap":48.7},
    "mekong_xayaburi":   {"bbox":[100.0,15.0,106.0,22.0],"lat":18.0,"lon":102.0,
                          "area_km2":795000,"runoff_c":0.45,"cap":7.4},
    "indus_tarbela":     {"bbox":[70.0,32.0,76.0,37.0], "lat":34.07,"lon":72.68,
                          "area_km2":363000,"runoff_c":0.32,"cap":13.7},
}

# ── Date ranges ───────────────────────────────────────────────────────────────
today      = datetime.date.today()
end_date   = today.strftime("%Y-%m-%d")
start_date = (today - datetime.timedelta(days=365)).strftime("%Y-%m-%d")
year       = today.year

print(f"📅 {start_date} → {end_date}")


def safe_get(v):
    try:
        return float(v) if v is not None else 0.0
    except Exception:
        return 0.0


def open_meteo_fetch(lat, lon, variables: list, start: str, end: str) -> dict:
    """Fetch daily Open-Meteo ERA5 data and return monthly aggregates (with retry)."""
    var_str = ",".join(variables)
    url = (f"https://archive-api.open-meteo.com/v1/archive"
           f"?latitude={lat}&longitude={lon}"
           f"&start_date={start}&end_date={end}"
           f"&daily={var_str}&timezone=UTC")
    # Retry up to 3 times with 5s delay
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=45) as r:
                d = json.loads(r.read())
            break
        except Exception as e:
            if attempt == 2: raise
            print(f"  ⏳ Open-Meteo retry {attempt+1}/3: {e}")
            time.sleep(5)
    daily  = d.get("daily", {})
    times  = daily.get("time", [])
    result = {}
    for var in variables:
        vals = daily.get(var, [])
        # Monthly aggregation
        monthly = {}
        for i, t in enumerate(times):
            m = t[:7]
            v = vals[i] if i < len(vals) else None
            if v is not None:
                monthly.setdefault(m, []).append(float(v))
        months_sorted = sorted(monthly.keys())
        result[var] = {
            "months": months_sorted,
            "monthly": [sum(monthly[m])/len(monthly[m]) for m in months_sorted],
            "mean":    round(sum(sum(monthly[m]) for m in months_sorted) /
                             sum(len(monthly[m]) for m in months_sorted), 4)
                       if months_sorted else 0
        }
    return result


def fetch_gpm_gee(region, start: str, end: str, year: int) -> dict:
    """GPM IMERG V07 monthly precipitation via GEE."""
    gpm = (ee.ImageCollection("NASA/GPM_L3/IMERG_V07")
           .filterDate(start, end)
           .filterBounds(region)
           .select("precipitation"))
    months = ee.List.sequence(0, 11)

    def monthly_gpm(m):
        m   = ee.Number(m).add(1)
        d0  = ee.Date.fromYMD(year, m, 1)
        d1  = d0.advance(1, "month")
        col = gpm.filterDate(d0, d1)
        img = ee.Image(ee.Algorithms.If(col.size().gt(0), col.mean(),
                                        ee.Image.constant(0)))
        val = img.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=region, scale=11132, maxPixels=1e9
        )
        p = ee.Number(val.get("precipitation", 0))
        return ee.Feature(None, {
            "month": d0.format("YYYY-MM"),
            "P_mm_day": p.multiply(24)
        })

    feats = ee.FeatureCollection(months.map(monthly_gpm)).getInfo()["features"]
    data  = [{"month": f["properties"]["month"],
               "P_mm_day": safe_get(f["properties"]["P_mm_day"])}
             for f in feats if f["properties"].get("P_mm_day") is not None]
    p_vals = [d["P_mm_day"] for d in data]
    return {
        "months":   [d["month"] for d in data],
        "P_mm_day": p_vals,
        "mean_P":   round(sum(p_vals)/len(p_vals), 3) if p_vals else 0,
        "source":   "NASA/GPM_L3/IMERG_V07",
        "n_months": len(p_vals),
        "error":    None
    }


def fetch_grace_gee(region) -> dict:
    """GRACE-FO TWS via GEE (2022-2023 range — confirmed available)."""
    # Try multiple GRACE collections (dataset names changed in GEE)
    for grace_col, grace_band in [
        ("NASA/GRACE/MASS_GRIDS_V04/LAND", "lwe_thickness_csr"),
        ("NASA/GRACE/MASS_GRIDS/LAND",     "lwe_thickness_csr"),
        ("NASA_USDA/HSL/SMAP10KM_soil_moisture", "ssm"),  # SMAP fallback
    ]:
        try:
            grace = (ee.ImageCollection(grace_col)
                     .filterDate("2022-01-01", "2024-06-30")
                     .filterBounds(region)
                     .select(grace_band))
            # Test if it has data
            n = grace.size().getInfo()
            if n > 0:
                break
        except Exception:
            continue

    def extract_tws(img):
        val = img.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=region, scale=300000, maxPixels=1e8
        ).get("lwe_thickness_csr")
        return ee.Feature(None, {
            "date":    img.date().format("YYYY-MM"),
            "tws_cm":  val
        })

    feats    = grace.map(extract_tws).getInfo()["features"]
    tws_data = [(f["properties"]["date"], safe_get(f["properties"]["tws_cm"]))
                for f in feats if f["properties"].get("tws_cm") is not None]
    tws_vals = [d[1] for d in tws_data]
    return {
        "months":   [d[0] for d in tws_data],
        "tws_cm":   tws_vals,
        "mean_tws": round(sum(tws_vals)/len(tws_vals), 3) if tws_vals else 0,
        "source":   "NASA/GRACE/MASS_GRIDS_V04/LAND",
        "n_months": len(tws_vals),
        "error":    None
    }


def derive_discharge(P_mm_day: list, runoff_c: float, area_km2: float) -> dict:
    """Derive monthly discharge from P × runoff_c × area."""
    Q_vals = [round(p * runoff_c * area_km2 / 86.4, 1) for p in P_mm_day]
    return {
        "Q_m3s":    Q_vals,
        "mean_Q":   round(sum(Q_vals)/len(Q_vals), 1) if Q_vals else 0,
        "source":   "Derived: GPM × runoff_c × area",
        "n_months": len(Q_vals),
        "error":    None
    }


# ── Main loop ─────────────────────────────────────────────────────────────────
output = {
    "schema_version": "2.0",
    "computed_at":    datetime.datetime.utcnow().isoformat(),
    "date_range":     {"start": start_date, "end": end_date},
    "n_basins":       len(BASINS),
    "basins":         {}
}

for basin_id, cfg in BASINS.items():
    print(f"\n🌍 {basin_id}")
    lat  = cfg["lat"]
    lon  = cfg["lon"]
    bbox = cfg["bbox"]
    rc   = cfg.get("runoff_c", 0.3)
    area = cfg.get("area_km2", 100000)

    region = ee.Geometry.Rectangle(bbox)
    result = {"basin_id": basin_id, "fetched_at": datetime.datetime.utcnow().isoformat()}

    # 1. GPM via GEE
    try:
        result["gpm"] = fetch_gpm_gee(region, start_date, end_date, year)
        print(f"  ✅ GPM: n={result['gpm']['n_months']}, mean={result['gpm']['mean_P']} mm/day")
    except Exception as e:
        result["gpm"] = {"error": str(e), "P_mm_day": [], "mean_P": 0, "months": [], "n_months": 0}
        print(f"  ❌ GPM: {e}")

    # 2. GRACE-FO via GEE
    try:
        result["grace"] = fetch_grace_gee(region)
        print(f"  ✅ GRACE: n={result['grace']['n_months']}, mean={result['grace']['mean_tws']} cm")
    except Exception as e:
        result["grace"] = {"error": str(e), "tws_cm": [], "mean_tws": 0, "months": [], "n_months": 0}
        print(f"  ❌ GRACE: {e}")

    # 3-5. Open-Meteo: Temperature + Precipitation + Soil Moisture
    try:
        om = open_meteo_fetch(lat, lon,
             ["temperature_2m_mean", "precipitation_sum",
              "soil_moisture_0_to_7cm_mean"],
             start_date, end_date)

        T_data = om["temperature_2m_mean"]
        P_data = om["precipitation_sum"]
        SM_data = om["soil_moisture_0_to_7cm_mean"]

        result["temperature"] = {
            "months":   T_data["months"],
            "T_C":      [round(v, 2) for v in T_data["monthly"]],
            "mean_T":   round(T_data["mean"], 2),
            "source":   "Open-Meteo ERA5",
            "n_months": len(T_data["months"]),
            "error":    None
        }
        print(f"  ✅ Temp: n={result['temperature']['n_months']}, mean={result['temperature']['mean_T']}°C")

        result["smap"] = {
            "months":   SM_data["months"],
            "sm_m3m3":  [round(v, 4) for v in SM_data["monthly"]],
            "mean_sm":  round(SM_data["mean"], 4),
            "source":   "Open-Meteo ERA5 soil moisture (SMAP proxy)",
            "n_months": len(SM_data["months"]),
            "error":    None
        }
        print(f"  ✅ SMAP proxy: n={result['smap']['n_months']}, mean={result['smap']['mean_sm']:.4f}")

        # Use Open-Meteo P as backup if GPM failed
        if result["gpm"]["n_months"] == 0:
            result["gpm"] = {
                "months":   P_data["months"],
                "P_mm_day": [round(v, 3) for v in P_data["monthly"]],
                "mean_P":   round(P_data["mean"], 3),
                "source":   "Open-Meteo ERA5 precipitation (backup)",
                "n_months": len(P_data["months"]),
                "error":    None
            }
            print(f"  ✅ GPM backup: n={result['gpm']['n_months']}, mean={result['gpm']['mean_P']} mm/day")

    except Exception as e:
        result["temperature"] = {"error": str(e), "T_C": [], "mean_T": 0}
        result["smap"]        = {"error": str(e), "sm_m3m3": [], "mean_sm": 0}
        print(f"  ❌ Open-Meteo: {e}")

    # 6. Discharge (derived from GPM × runoff_c × area)
    try:
        P_vals = result["gpm"].get("P_mm_day", [])
        if P_vals:
            result["glofas"] = derive_discharge(P_vals, rc, area)
            result["glofas"]["months"] = result["gpm"].get("months", [])
            print(f"  ✅ Q derived: mean={result['glofas']['mean_Q']} m3/s")
        else:
            raise ValueError("No GPM data for discharge derivation")
    except Exception as e:
        result["glofas"] = {"error": str(e), "Q_m3s": [], "mean_Q": 0}
        print(f"  ❌ GloFAS: {e}")

    output["basins"][basin_id] = result
    time.sleep(1)

# ── Save ──────────────────────────────────────────────────────────────────────
Path("data").mkdir(exist_ok=True)
with open("data/gee_realtime.json", "w") as f:
    json.dump(output, f, indent=2)

print(f"\n✅ Saved: data/gee_realtime.json")
print(f"   Basins: {len(output['basins'])}")
for bid, bd in output['basins'].items():
    gpm_ok   = bd.get('gpm',{}).get('n_months',0) > 0
    grace_ok = bd.get('grace',{}).get('n_months',0) > 0
    temp_ok  = bd.get('temperature',{}).get('n_months',0) > 0
    q_ok     = bd.get('glofas',{}).get('n_months',0) > 0
    sm_ok    = bd.get('smap',{}).get('n_months',0) > 0
    print(f"   {bid[:25]:<25} GPM={'✅' if gpm_ok else '❌'} "
          f"GRACE={'✅' if grace_ok else '❌'} "
          f"T={'✅' if temp_ok else '❌'} "
          f"Q={'✅' if q_ok else '❌'} "
          f"SM={'✅' if sm_ok else '❌'}")
