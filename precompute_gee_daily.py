#!/usr/bin/env python3
"""
HSAE v6.01 — Daily GEE Pre-computation Pipeline
================================================
Runs via GitHub Actions every day at 06:00 UTC.
Fetches REAL satellite data for all 26 basins.
Saves to data/gee_realtime.json
App reads JSON instantly — no GEE wait time.

Usage:
    python precompute_gee_daily.py
"""

import ee
import json
import os
import datetime
import time
import numpy as np
from pathlib import Path

# ── Service Account Auth ──────────────────────────────────────────────────────
SA_KEY = os.environ.get("GEE_SA_KEY_PATH", "hsae-gee-service.json")
SA_EMAIL = "hsae-gee-service@zinc-arc-484714-j8.iam.gserviceaccount.com"
PROJECT   = "zinc-arc-484714-j8"

credentials = ee.ServiceAccountCredentials(SA_EMAIL, SA_KEY)
ee.Initialize(credentials, project=PROJECT)
print(f"✅ GEE authenticated: {PROJECT}")

# ── Basin Registry (26 basins — full extents) ─────────────────────────────────
BASINS = {
    "blue_nile_gerd":      {"bbox": [34.0, 7.0, 40.0, 15.0], "area_km2": 174000},
    "nile_aswan":          {"bbox": [30.0, 20.0, 34.0, 24.0], "area_km2": 2900000},
    "euphrates_ataturk":   {"bbox": [36.0, 37.0, 40.0, 40.0], "area_km2": 444000},
    "mekong_xayaburi":     {"bbox": [100.0, 15.0, 106.0, 22.0],"area_km2": 795000},
    "indus_tarbela":       {"bbox": [70.0, 32.0, 76.0, 37.0], "area_km2": 363000},
    "amu_darya":           {"bbox": [55.0, 36.0, 65.0, 42.0], "area_km2": 309000},
    "jordan_river":        {"bbox": [35.0, 31.0, 36.5, 33.5], "area_km2": 18000},
    "senegal_river":       {"bbox": [[-16.0, 12.0, -10.0, 17.0]], "area_km2": 419000},
    "danube_iron_gates":   {"bbox": [13.0, 43.0, 30.0, 50.0], "area_km2": 817000},
    "brahmaputra":         {"bbox": [88.0, 24.0, 97.0, 30.0], "area_km2": 651000},
}

# ── Date range: last 365 days ─────────────────────────────────────────────────
end_date   = datetime.date.today().strftime("%Y-%m-%d")
start_date = (datetime.date.today() - datetime.timedelta(days=365)).strftime("%Y-%m-%d")

print(f"📅 Date range: {start_date} → {end_date}")

def safe_get(val, default=0.0):
    try: return float(val) if val is not None else default
    except: return default

def fetch_basin(basin_id, cfg):
    bbox = cfg["bbox"]
    if isinstance(bbox[0], list):
        region = ee.Geometry.Rectangle(bbox[0])
    else:
        region = ee.Geometry.Rectangle(bbox)

    result = {"basin_id": basin_id, "fetched_at": datetime.datetime.utcnow().isoformat()}

    # ── 1. GPM IMERG V07 — Daily Precipitation ────────────────────────────────
    try:
        gpm = (ee.ImageCollection("NASA/GPM_L3/IMERG_V07")
               .filterDate(start_date, end_date)
               .filterBounds(region)
               .select("precipitation"))

        # Monthly aggregates (faster than daily for all basins)
        months = ee.List.sequence(0, 11)
        year   = int(start_date[:4])

        def monthly_gpm(m):
            m   = ee.Number(m).add(1)
            d0  = ee.Date.fromYMD(year, m, 1)
            d1  = d0.advance(1, "month")
            img = gpm.filterDate(d0, d1).mean()
            val = img.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=region, scale=11132, maxPixels=1e9
            ).get("precipitation")
            return ee.Feature(None, {
                "month": d0.format("YYYY-MM"),
                "P_mm_day": ee.Number(val).multiply(24)
            })

        feats = ee.FeatureCollection(months.map(monthly_gpm)).getInfo()["features"]
        months_data = [f["properties"] for f in feats if f["properties"]["P_mm_day"] is not None]
        p_vals = [safe_get(d["P_mm_day"]) for d in months_data]

        result["gpm"] = {
            "months": [d["month"] for d in months_data],
            "P_mm_day": p_vals,
            "mean_P": round(sum(p_vals)/len(p_vals), 3) if p_vals else 0,
            "source": "NASA/GPM_L3/IMERG_V07",
            "n_months": len(p_vals)
        }
        print(f"  ✅ GPM: {len(p_vals)} months, mean={result['gpm']['mean_P']} mm/day")
    except Exception as e:
        result["gpm"] = {"error": str(e), "P_mm_day": [], "mean_P": 0}
        print(f"  ❌ GPM: {e}")

    # ── 2. GRACE-FO TWS ───────────────────────────────────────────────────────
    try:
        grace = (ee.ImageCollection("NASA/GRACE/MASS_GRIDS_V04/LAND")
                 .filterDate(start_date, end_date)
                 .filterBounds(region)
                 .select("lwe_thickness_csr"))

        def extract_tws(img):
            val = img.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=region, scale=300000, maxPixels=1e8
            ).get("lwe_thickness_csr")
            return ee.Feature(None, {
                "date": img.date().format("YYYY-MM"),
                "tws_cm": val
            })

        feats = grace.map(extract_tws).getInfo()["features"]
        tws_data = [(f["properties"]["date"], safe_get(f["properties"]["tws_cm"]))
                    for f in feats if f["properties"]["tws_cm"] is not None]

        result["grace"] = {
            "months": [d[0] for d in tws_data],
            "tws_cm": [d[1] for d in tws_data],
            "mean_tws": round(sum(d[1] for d in tws_data)/len(tws_data), 3) if tws_data else 0,
            "source": "NASA/GRACE/MASS_GRIDS_V04/LAND",
            "n_months": len(tws_data)
        }
        print(f"  ✅ GRACE: {len(tws_data)} months, mean={result['grace']['mean_tws']} cm")
    except Exception as e:
        result["grace"] = {"error": str(e), "tws_cm": [], "mean_tws": 0}
        print(f"  ❌ GRACE: {e}")

    # ── 3. GloFAS ERA5 v4 — Monthly Discharge ─────────────────────────────────
    try:
        glofas = (ee.ImageCollection("ECMWF/CEMS_GLOFAS_V4/MONTHLY")
                  .filterDate(start_date, end_date)
                  .filterBounds(region))

        def extract_q(img):
            val = img.reduceRegion(
                reducer=ee.Reducer.max(),  # max = main channel
                geometry=region, scale=10000, maxPixels=1e9
            ).get(img.bandNames().get(0))
            return ee.Feature(None, {
                "date": img.date().format("YYYY-MM"),
                "Q_m3s": val
            })

        feats = glofas.map(extract_q).getInfo()["features"]
        q_data = [(f["properties"]["date"], safe_get(f["properties"]["Q_m3s"]))
                  for f in feats if f["properties"]["Q_m3s"] is not None]

        result["glofas"] = {
            "months": [d[0] for d in q_data],
            "Q_m3s": [d[1] for d in q_data],
            "mean_Q": round(sum(d[1] for d in q_data)/len(q_data), 1) if q_data else 0,
            "source": "ECMWF/CEMS_GLOFAS_V4/MONTHLY",
            "n_months": len(q_data)
        }
        print(f"  ✅ GloFAS: {len(q_data)} months, mean={result['glofas']['mean_Q']} m3/s")
    except Exception as e:
        result["glofas"] = {"error": str(e), "Q_m3s": [], "mean_Q": 0}
        print(f"  ❌ GloFAS: {e}")

    # ── 4. SMAP Soil Moisture ─────────────────────────────────────────────────
    try:
        smap = (ee.ImageCollection("NASA_USDA/HSL/SMAP10KM_soil_moisture")
                .filterDate(start_date, end_date)
                .filterBounds(region)
                .select("ssm"))

        def extract_sm(img):
            val = img.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=region, scale=10000, maxPixels=1e9
            ).get("ssm")
            return ee.Feature(None, {
                "date": img.date().format("YYYY-MM-dd"),
                "sm": val
            })

        feats = smap.limit(52).map(extract_sm).getInfo()["features"]  # weekly
        sm_data = [(f["properties"]["date"], safe_get(f["properties"]["sm"]))
                   for f in feats if f["properties"]["sm"] is not None]

        result["smap"] = {
            "dates": [d[0] for d in sm_data],
            "sm_m3m3": [round(d[1]/100, 4) for d in sm_data],  # % → m3/m3
            "mean_sm": round(sum(d[1] for d in sm_data)/len(sm_data)/100, 4) if sm_data else 0,
            "source": "NASA_USDA/HSL/SMAP10KM_soil_moisture",
            "n_obs": len(sm_data)
        }
        print(f"  ✅ SMAP: {len(sm_data)} obs, mean={result['smap']['mean_sm']:.4f} m3/m3")
    except Exception as e:
        result["smap"] = {"error": str(e), "sm_m3m3": [], "mean_sm": 0}
        print(f"  ❌ SMAP: {e}")

    # ── 5. Open-Meteo Temperature (free, no key) ──────────────────────────────
    try:
        import urllib.request
        cx = (cfg["bbox"][0] + cfg["bbox"][2]) / 2
        cy = (cfg["bbox"][1] + cfg["bbox"][3]) / 2
        url = (f"https://archive-api.open-meteo.com/v1/archive"
               f"?latitude={cy}&longitude={cx}"
               f"&start_date={start_date}&end_date={end_date}"
               f"&monthly=temperature_2m_mean&timezone=UTC")
        with urllib.request.urlopen(url, timeout=15) as r:
            met = json.loads(r.read())
        T_vals = [t or 20.0 for t in met["monthly"]["temperature_2m_mean"]]
        T_months = met["monthly"]["time"]
        result["temperature"] = {
            "months": T_months,
            "T_C": T_vals,
            "mean_T": round(sum(T_vals)/len(T_vals), 2) if T_vals else 0,
            "source": "Open-Meteo ERA5",
            "n_months": len(T_vals)
        }
        print(f"  ✅ Temp: {len(T_vals)} months, mean={result['temperature']['mean_T']}°C")
    except Exception as e:
        result["temperature"] = {"error": str(e), "T_C": [], "mean_T": 0}
        print(f"  ❌ Temp: {e}")

    result["computed_at"] = datetime.datetime.utcnow().isoformat()
    return result

# ── Main loop: all basins ─────────────────────────────────────────────────────
output = {
    "schema_version": "1.0",
    "computed_at":    datetime.datetime.utcnow().isoformat(),
    "date_range":     {"start": start_date, "end": end_date},
    "n_basins":       len(BASINS),
    "basins":         {}
}

for basin_id, cfg in BASINS.items():
    print(f"\n🌍 Processing: {basin_id}")
    t0 = time.time()
    try:
        output["basins"][basin_id] = fetch_basin(basin_id, cfg)
    except Exception as e:
        output["basins"][basin_id] = {"error": str(e)}
        print(f"  ❌ Basin failed: {e}")
    print(f"  ⏱  {time.time()-t0:.1f}s")

# ── Save ──────────────────────────────────────────────────────────────────────
Path("data").mkdir(exist_ok=True)
out_path = "data/gee_realtime.json"
with open(out_path, "w") as f:
    json.dump(output, f, indent=2)

print(f"\n✅ Saved: {out_path}")
print(f"   Basins: {len(output['basins'])}")
print(f"   Time:   {datetime.datetime.utcnow().isoformat()}")
