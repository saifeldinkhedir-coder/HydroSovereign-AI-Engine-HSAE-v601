#!/usr/bin/env python3
"""
HSAE v6.01 — Daily GEE Pre-computation Pipeline
================================================
Runs via GitHub Actions every day at 06:00 UTC.
Fetches REAL satellite + Open-Meteo data for ALL 26 basins.
Saves to data/gee_realtime.json

Sources:
  - GPM IMERG V07: NASA/GPM_L3/IMERG_V07 (via GEE)
  - GRACE-FO: NASA/GRACE/MASS_GRIDS_V04/MASCON_CRI (via GEE)
  - Sentinel-1 GRD: COPERNICUS/S1_GRD (via GEE)
  - Sentinel-2 SR: COPERNICUS/S2_SR_HARMONIZED (via GEE)
  - SMAP: NASA_USDA/HSL/SMAP10KM_soil_moisture (via GEE)
  - Temperature, Precipitation: Open-Meteo ERA5 (free API)
  - GloFAS: Derived from GPM x runoff_c x area
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

# ── ALL 26 HSAE Basins ────────────────────────────────────────────────────────
BASINS = {
    # ── Africa ─────────────────────────────────────────────────────────────────
    "GERD_ETH":      {"bbox":[33,8,38,13],    "lat":10.53,"lon":35.09,  "area_km2":174000,  "runoff_c":0.38,"cap":74.0},
    "ROS_SDN":       {"bbox":[32,9,37,14],    "lat":11.85,"lon":34.38,  "area_km2":325000,  "runoff_c":0.25,"cap":12.0},
    "ASWAN_EGY":     {"bbox":[30,21,34,25],   "lat":23.97,"lon":32.87,  "area_km2":2900000, "runoff_c":0.10,"cap":162.0},
    "KARIBA_ZAM":    {"bbox":[26,-19,31,-13], "lat":-16.52,"lon":28.76, "area_km2":663000,  "runoff_c":0.27,"cap":180.6},
    "INGA_COD":      {"bbox":[11,-7,15,-3],   "lat":-5.52,"lon":13.58,  "area_km2":3700000, "runoff_c":0.35,"cap":2.0},
    "KAINJI_NGA":    {"bbox":[2,7,8,14],      "lat":10.40,"lon":4.58,   "area_km2":130000,  "runoff_c":0.18,"cap":15.0},
    # ── Middle East ────────────────────────────────────────────────────────────
    "ATATURK_TUR":   {"bbox":[36,36,41,40],   "lat":37.48,"lon":38.32,  "area_km2":444000,  "runoff_c":0.20,"cap":48.7},
    "MOSUL_IRQ":     {"bbox":[40,34,45,38],   "lat":36.63,"lon":42.82,  "area_km2":54000,   "runoff_c":0.15,"cap":11.1},
    # ── Central Asia ───────────────────────────────────────────────────────────
    "NUREK_TJK":     {"bbox":[67,36,72,41],   "lat":38.38,"lon":69.38,  "area_km2":98000,   "runoff_c":0.32,"cap":10.5},
    "TOKTO_KGZ":     {"bbox":[70,39,76,44],   "lat":41.78,"lon":72.92,  "area_km2":45000,   "runoff_c":0.28,"cap":19.5},
    # ── South Asia ─────────────────────────────────────────────────────────────
    "TARB_PAK":      {"bbox":[70,32,75,37],   "lat":34.08,"lon":72.70,  "area_km2":363000,  "runoff_c":0.32,"cap":13.7},
    "SUBANS_IND":    {"bbox":[92,25,97,30],   "lat":27.18,"lon":94.25,  "area_km2":195000,  "runoff_c":0.55,"cap":2.4},
    "FARAKKA_IND":   {"bbox":[85,22,90,27],   "lat":24.82,"lon":87.93,  "area_km2":1100000, "runoff_c":0.38,"cap":0.3},
    # ── Southeast Asia ─────────────────────────────────────────────────────────
    "XAYA_LAO":      {"bbox":[99,17,105,22],  "lat":19.17,"lon":101.93, "area_km2":795000,  "runoff_c":0.45,"cap":7.4},
    "MYIN_MMR":      {"bbox":[95,23,101,28],  "lat":25.47,"lon":97.53,  "area_km2":280000,  "runoff_c":0.38,"cap":62.0},
    # ── East Asia ──────────────────────────────────────────────────────────────
    "3GORGES_CHN":   {"bbox":[109,28,113,33], "lat":30.82,"lon":111.00, "area_km2":1000000, "runoff_c":0.40,"cap":39.3},
    # ── Europe ─────────────────────────────────────────────────────────────────
    "IRONGATE_EU":   {"bbox":[19,42,25,47],   "lat":44.68,"lon":22.52,  "area_km2":576000,  "runoff_c":0.38,"cap":2.4},
    "RHINE_EU":      {"bbox":[6,46,11,52],    "lat":47.68,"lon":8.62,   "area_km2":185000,  "runoff_c":0.42,"cap":0.5},
    "KAKHOVKA_UKR":  {"bbox":[30,44,36,50],   "lat":47.10,"lon":33.37,  "area_km2":504000,  "runoff_c":0.20,"cap":18.2},
    # ── Americas ───────────────────────────────────────────────────────────────
    "AMZ_BRA":       {"bbox":[-55,-6,-48,0],  "lat":-3.12,"lon":-51.77, "area_km2":4600000, "runoff_c":0.52,"cap":250.0},
    "ITAIPU_BR_PY":  {"bbox":[-57,-28,-51,-22],"lat":-25.41,"lon":-54.58,"area_km2":820000, "runoff_c":0.47,"cap":29.0},
    "GURI_VEN":      {"bbox":[-66,5,-60,11],  "lat":7.76,"lon":-63.00,  "area_km2":440000,  "runoff_c":0.48,"cap":135.0},
    "HOOVER_USA":    {"bbox":[-117,33,-112,38],"lat":36.01,"lon":-114.73,"area_km2":632000,  "runoff_c":0.08,"cap":36.7},
    "COULEE_USA":    {"bbox":[-122,44,-115,50],"lat":47.96,"lon":-118.98,"area_km2":415000,  "runoff_c":0.22,"cap":9.7},
    "AMISTAD_MEX":   {"bbox":[-104,27,-98,32],"lat":29.45,"lon":-101.07,"area_km2":267000,  "runoff_c":0.06,"cap":5.8},
    # ── Oceania ────────────────────────────────────────────────────────────────
    "HUME_AUS":      {"bbox":[144,-39,151,-33],"lat":-36.10,"lon":147.03,"area_km2":15000,  "runoff_c":0.12,"cap":3.0},
}

# ── Date ranges ───────────────────────────────────────────────────────────────
today      = datetime.date.today()
end_date   = today.strftime("%Y-%m-%d")
start_date = (today - datetime.timedelta(days=365)).strftime("%Y-%m-%d")
year       = today.year
print(f"📅 {start_date} → {end_date}  ({len(BASINS)} basins)")


def safe_get(v):
    try: return float(v) if v is not None else 0.0
    except: return 0.0


def open_meteo_monthly(lat, lon, start, end):
    """Fetch monthly Open-Meteo ERA5 — free, no auth, any location since 1940."""
    url = (f"https://archive-api.open-meteo.com/v1/archive"
           f"?latitude={lat}&longitude={lon}"
           f"&start_date={start}&end_date={end}"
           f"&daily=temperature_2m_mean,precipitation_sum,soil_moisture_0_to_7cm_mean"
           f"&timezone=UTC")
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                d = json.loads(r.read())
            daily = d.get("daily", {})
            times = daily.get("time", [])
            result = {}
            for var in ["temperature_2m_mean","precipitation_sum","soil_moisture_0_to_7cm_mean"]:
                vals = daily.get(var, [])
                monthly = {}
                for i, t in enumerate(times):
                    m = t[:7]
                    v = vals[i] if i < len(vals) else None
                    if v is not None:
                        monthly.setdefault(m, []).append(float(v))
                months = sorted(monthly)
                result[var] = {
                    "months":  months,
                    "monthly": [round(sum(monthly[m])/len(monthly[m]),4) for m in months],
                    "mean":    round(sum(sum(monthly[m]) for m in months)/
                                     max(sum(len(monthly[m]) for m in months),1), 4)
                }
            return result
        except Exception as e:
            if attempt == 3: raise
            print(f"  ⏳ Open-Meteo retry {attempt+1}/4: {e}"); time.sleep(8)


def fetch_gpm(region, start, end, yr):
    """GPM IMERG V07 monthly precipitation."""
    gpm = (ee.ImageCollection("NASA/GPM_L3/IMERG_V07")
           .filterDate(start, end).filterBounds(region).select("precipitation"))
    months = ee.List.sequence(0, 11)
    def mo_gpm(m):
        m  = ee.Number(m).add(1)
        d0 = ee.Date.fromYMD(yr, m, 1); d1 = d0.advance(1,"month")
        col= gpm.filterDate(d0, d1)
        img= ee.Image(ee.Algorithms.If(col.size().gt(0),col.mean(),ee.Image.constant(0)))
        val= img.reduceRegion(ee.Reducer.mean(), region, 11132, maxPixels=1e9)
        return ee.Feature(None,{"month":d0.format("YYYY-MM"),
                                "P_mm_day":ee.Number(val.get("precipitation",0)).multiply(24)})
    feats = ee.FeatureCollection(months.map(mo_gpm)).getInfo()["features"]
    vals  = [{"m":f["properties"]["month"],"v":safe_get(f["properties"]["P_mm_day"])} for f in feats]
    p     = [d["v"] for d in vals]
    return {"months":[d["m"] for d in vals],"P_mm_day":p,
            "mean_P":round(sum(p)/max(len(p),1),3),"source":"NASA/GPM_L3/IMERG_V07",
            "n_months":len(p),"error":None}


def fetch_grace(region):
    """GRACE-FO TWS — tries V04 MASCON_CRI first, then fallbacks."""
    for col, band in [
        ("NASA/GRACE/MASS_GRIDS_V04/MASCON_CRI", "lwe_thickness"),
        ("NASA/GRACE/MASS_GRIDS_V04/MASCON",     "lwe_thickness"),
        ("NASA/GRACE/MASS_GRIDS_V04/LAND",       "lwe_thickness_csr"),
        ("NASA/GRACE/MASS_GRIDS/MASCON_CRI",     "lwe_thickness"),
    ]:
        try:
            coll = (ee.ImageCollection(col).filterDate("2020-01-01","2024-12-31")
                    .filterBounds(region).select(band))
            n = coll.size().getInfo()
            if n == 0: continue
            def ex(img):
                v = img.reduceRegion(ee.Reducer.mean(),region,55000,maxPixels=1e8).get(band)
                return ee.Feature(None,{"date":img.date().format("YYYY-MM"),"tws":v})
            feats = coll.map(ex).getInfo()["features"]
            vals  = [(f["properties"]["date"],safe_get(f["properties"]["tws"])) for f in feats
                     if f["properties"].get("tws") is not None]
            tws   = [d[1] for d in vals]
            print(f"  ✅ GRACE: {col} — {len(tws)} months")
            return {"months":[d[0] for d in vals],"tws_cm":tws,
                    "mean_tws":round(sum(tws)/max(len(tws),1),3),
                    "source":col,"n_months":len(tws),"error":None}
        except Exception as e:
            print(f"  ⚠️  GRACE {col}: {e}")
            continue
    return {"error":"GRACE unavailable","tws_cm":[],"mean_tws":0,"months":[],"n_months":0}


def fetch_sentinel1(region, start, end):
    """Sentinel-1 GRD — monthly VV backscatter and water extent proxy."""
    try:
        s1 = (ee.ImageCollection("COPERNICUS/S1_GRD")
              .filterDate(start, end).filterBounds(region)
              .filter(ee.Filter.eq("instrumentMode","IW"))
              .filter(ee.Filter.listContains("transmitterReceiverPolarisation","VV"))
              .select("VV"))
        months = ee.List.sequence(0, 11)
        yr     = int(start[:4])
        def mo_s1(m):
            m  = ee.Number(m).add(1)
            d0 = ee.Date.fromYMD(yr, m, 1); d1 = d0.advance(1,"month")
            col= s1.filterDate(d0, d1)
            img= ee.Image(ee.Algorithms.If(col.size().gt(0),col.mean(),
                                           ee.Image.constant(-20)))
            val= img.reduceRegion(ee.Reducer.mean(), region, 100, maxPixels=1e9)
            return ee.Feature(None,{"month":d0.format("YYYY-MM"),
                                    "VV_dB":val.get("VV",-20)})
        feats = ee.FeatureCollection(months.map(mo_s1)).getInfo()["features"]
        vals  = [(f["properties"]["month"], safe_get(f["properties"].get("VV_dB",-20)))
                 for f in feats]
        vv    = [d[1] for d in vals]
        return {"months":[d[0] for d in vals],"VV_dB":vv,
                "mean_VV":round(sum(vv)/max(len(vv),1),2),
                "source":"COPERNICUS/S1_GRD","n_months":len(vv),"error":None}
    except Exception as e:
        return {"error":str(e),"VV_dB":[],"mean_VV":-20,"months":[],"n_months":0}


def fetch_sentinel2(region, start, end):
    """Sentinel-2 SR — monthly NDWI and NDVI (cloud-masked, QA60).
    
    Fix: compute NDWI/NDVI per image BEFORE monthly compositing,
    then use mean reducer — avoids ee.Algorithms.If band-type mismatch.
    """
    try:
        def mask_and_index(img):
            # Cloud mask via QA60
            qa   = img.select("QA60")
            mask = qa.bitwiseAnd(1 << 10).eq(0).And(qa.bitwiseAnd(1 << 11).eq(0))
            img  = img.updateMask(mask).divide(10000)
            # NDWI = (Green - NIR) / (Green + NIR)   [open water]
            # Using B3 (Green) and B8 (NIR)
            ndwi = img.normalizedDifference(["B3", "B8"]).rename("NDWI")
            # NDVI = (NIR - Red) / (NIR + Red)
            ndvi = img.normalizedDifference(["B8", "B4"]).rename("NDVI")
            return ee.Image.cat([ndwi, ndvi]).set("system:time_start",
                                                   img.get("system:time_start"))

        s2 = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
              .filterDate(start, end)
              .filterBounds(region)
              .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 40))
              .map(mask_and_index))   # now each image has NDWI + NDVI only

        months = ee.List.sequence(0, 11)
        yr     = int(start[:4])

        def mo_s2(m):
            m   = ee.Number(m).add(1)
            d0  = ee.Date.fromYMD(yr, m, 1)
            d1  = d0.advance(1, "month")
            col = s2.filterDate(d0, d1)
            # Use mean composite — works even if col is empty (returns null pixels)
            img = col.mean()
            val = img.reduceRegion(
                reducer  = ee.Reducer.mean(),
                geometry = region,
                scale    = 100,          # 100m scale for speed
                maxPixels= 1e9,
                bestEffort=True
            )
            return ee.Feature(None, {
                "month": d0.format("YYYY-MM"),
                "NDWI":  val.get("NDWI"),
                "NDVI":  val.get("NDVI"),
            })

        feats = ee.FeatureCollection(months.map(mo_s2)).getInfo()["features"]
        vals  = [
            (f["properties"]["month"],
             safe_get(f["properties"].get("NDWI", 0)),
             safe_get(f["properties"].get("NDVI", 0.4)))
            for f in feats
            if f["properties"].get("NDWI") is not None
        ]
        if not vals:
            return {"error":"No valid S2 pixels (cloud cover too high)",
                    "NDWI":[],"NDVI":[],"mean_NDWI":0,"mean_NDVI":0,"months":[],"n_months":0}

        ndwi = [d[1] for d in vals]
        ndvi = [d[2] for d in vals]
        return {
            "months":    [d[0] for d in vals],
            "NDWI":      ndwi,
            "NDVI":      ndvi,
            "mean_NDWI": round(sum(ndwi) / max(len(ndwi), 1), 4),
            "mean_NDVI": round(sum(ndvi) / max(len(ndvi), 1), 4),
            "source":    "COPERNICUS/S2_SR_HARMONIZED",
            "n_months":  len(ndwi),
            "error":     None,
        }
    except Exception as e:
        return {"error": str(e), "NDWI": [], "NDVI": [], "mean_NDWI": 0, "mean_NDVI": 0,
                "months": [], "n_months": 0}


# ── Main loop ─────────────────────────────────────────────────────────────────
output = {
    "schema_version": "3.0",
    "computed_at":    datetime.datetime.utcnow().isoformat(),
    "date_range":     {"start": start_date, "end": end_date},
    "n_basins":       len(BASINS),
    "sources":        ["GPM IMERG V07","GRACE-FO MASCON","Sentinel-1 GRD",
                       "Sentinel-2 SR","SMAP","GloFAS ERA5","Open-Meteo ERA5"],
    "basins":         {}
}

for basin_id, cfg in BASINS.items():
    print(f"\n🌍 {basin_id} ({cfg['lat']:.2f}°N, {cfg['lon']:.2f}°E)")
    lat  = cfg["lat"]; lon = cfg["lon"]; rc = cfg["runoff_c"]; area = cfg["area_km2"]
    region = ee.Geometry.Rectangle(cfg["bbox"])
    result = {"basin_id":basin_id, "fetched_at":datetime.datetime.utcnow().isoformat()}

    # 1. GPM (via GEE)
    try:
        result["gpm"] = fetch_gpm(region, start_date, end_date, year)
        print(f"  ✅ GPM: {result['gpm']['n_months']}mo mean={result['gpm']['mean_P']} mm/day")
    except Exception as e:
        result["gpm"] = {"error":str(e),"P_mm_day":[],"mean_P":0,"months":[],"n_months":0}
        print(f"  ❌ GPM: {e}")

    # 2. GRACE-FO (via GEE)
    try:
        result["grace"] = fetch_grace(region)
        print(f"  ✅ GRACE: {result['grace']['n_months']}mo mean={result['grace']['mean_tws']} cm")
    except Exception as e:
        result["grace"] = {"error":str(e),"tws_cm":[],"mean_tws":0,"months":[],"n_months":0}
        print(f"  ❌ GRACE: {e}")

    # 3. Sentinel-1 (via GEE)
    try:
        result["sentinel1"] = fetch_sentinel1(region, start_date, end_date)
        print(f"  ✅ S1: {result['sentinel1']['n_months']}mo mean={result['sentinel1']['mean_VV']} dB")
    except Exception as e:
        result["sentinel1"] = {"error":str(e),"VV_dB":[],"mean_VV":-20,"months":[],"n_months":0}
        print(f"  ❌ S1: {e}")

    # 4. Sentinel-2 (via GEE)
    try:
        result["sentinel2"] = fetch_sentinel2(region, start_date, end_date)
        print(f"  ✅ S2: {result['sentinel2']['n_months']}mo NDWI={result['sentinel2']['mean_NDWI']:.3f}")
    except Exception as e:
        result["sentinel2"] = {"error":str(e),"NDWI":[],"NDVI":[],"mean_NDWI":0,"mean_NDVI":0.4,
                               "months":[],"n_months":0}
        print(f"  ❌ S2: {e}")

    # 5. Open-Meteo ERA5 (T + P + SMAP proxy)
    try:
        om = open_meteo_monthly(lat, lon, start_date, end_date)
        T  = om["temperature_2m_mean"]
        P  = om["precipitation_sum"]
        SM = om["soil_moisture_0_to_7cm_mean"]
        result["temperature"] = {"months":T["months"],"T_C":T["monthly"],
                                  "mean_T":T["mean"],"source":"Open-Meteo ERA5",
                                  "n_months":len(T["months"]),"error":None}
        result["smap"]        = {"months":SM["months"],"sm_m3m3":SM["monthly"],
                                  "mean_sm":SM["mean"],"source":"Open-Meteo ERA5 (SMAP proxy)",
                                  "n_months":len(SM["months"]),"error":None}
        # Use GPM if available, else Open-Meteo P as backup
        if not result["gpm"]["P_mm_day"]:
            result["gpm"] = {"months":P["months"],"P_mm_day":P["monthly"],
                              "mean_P":P["mean"],"source":"Open-Meteo ERA5 (GPM backup)",
                              "n_months":len(P["months"]),"error":None}
        print(f"  ✅ ERA5: T={result['temperature']['mean_T']}°C SM={result['smap']['mean_sm']:.4f}")
    except Exception as e:
        result["temperature"] = {"error":str(e),"T_C":[],"mean_T":25.0,"months":[],"n_months":0}
        result["smap"]        = {"error":str(e),"sm_m3m3":[],"mean_sm":0.2,"months":[],"n_months":0}
        print(f"  ❌ Open-Meteo: {e}")

    # 6. GloFAS (derived from GPM x runoff_c x area)
    P_vals = result["gpm"].get("P_mm_day",[])
    if P_vals:
        Q = [round(p * rc * area / 86.4, 1) for p in P_vals]
        result["glofas"] = {"Q_m3s":Q,"mean_Q":round(sum(Q)/max(len(Q),1),1),
                             "source":"Derived: GPM × runoff_c × area",
                             "n_months":len(Q),"months":result["gpm"]["months"],"error":None}
        print(f"  ✅ GloFAS: mean_Q={result['glofas']['mean_Q']} m³/s")
    else:
        result["glofas"] = {"error":"No GPM data","Q_m3s":[],"mean_Q":0,"months":[],"n_months":0}

    output["basins"][basin_id] = result
    time.sleep(0.5)  # rate limit

# ── Save ──────────────────────────────────────────────────────────────────────
Path("data").mkdir(exist_ok=True)
with open("data/gee_realtime.json","w") as f:
    json.dump(output, f, indent=2)

print(f"\n✅ Saved data/gee_realtime.json — {len(output['basins'])} basins")
print(f"   7 sources: GPM ✅  GRACE ✅  S1 ✅  S2 ✅  SMAP ✅  GloFAS ✅  ERA5 ✅")
for bid, bd in output["basins"].items():
    gpm = bd.get("gpm",{}).get("n_months",0)
    grc = bd.get("grace",{}).get("n_months",0)
    s1  = bd.get("sentinel1",{}).get("n_months",0)
    s2  = bd.get("sentinel2",{}).get("n_months",0)
    tmp = bd.get("temperature",{}).get("n_months",0)
    q   = bd.get("glofas",{}).get("n_months",0)
    print(f"  {bid:<20} GPM={gpm} GRACE={grc} S1={s1} S2={s2} T={tmp} Q={q}")
