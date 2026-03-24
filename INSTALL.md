# HSAE v10.0 — Installation Guide
# ==================================
# Author: Seifeldin M.G. Alkedir · ORCID: 0000-0003-0821-2991

## Quick Start (Simulation Mode — no data needed)

```bash
git clone https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-
cd HydroSovereign-AI-Engine-HSAE-
pip install -r requirements.txt
streamlit run app.py                            # UI
uvicorn api_server:app --port 8000 --reload     # API (separate terminal)
python test_hsae_v10.py                         # 240 tests
```

## Docker (Recommended)

```bash
docker-compose up          # starts both API (8000) and Streamlit (8501)
docker-compose down        # stop
```

## Step 1 — Google Earth Engine

```bash
pip install earthengine-api
earthengine authenticate        # opens browser — login with Google
earthengine set_project zinc-arc-484714-j8
```

## Step 2 — NASA Earthdata (GRACE-FO, SMAP)

1. Register: https://urs.earthdata.nasa.gov/users/new (free)
2. Approve PODAAC in Applications → Authorized Apps
3. Create ~/.netrc:
   ```
   machine urs.earthdata.nasa.gov login YOUR_USER password YOUR_PASS
   ```
4. `pip install earthaccess`

## Step 3 — GRDC Discharge Data (free, 1-3 business days)

1. Register: https://grdc.bafg.de → Data → Request Data
2. Request stations for your basin (see GRDC_STATION_CATALOG in grdc_data_manager.py)
3. Place CSV files in `HSAE_Data/` folder
4. GRDC Manager page → Upload & Validate

## Step 4 — GloFAS / Copernicus CDS

1. Register: https://cds.climate.copernicus.eu
2. Accept GloFAS terms: https://cds.climate.copernicus.eu/datasets/cems-glofas-forecast
3. Create ~/.cdsapirc:
   ```
   url: https://cds.climate.copernicus.eu/api/v2
   key: YOUR_UID:YOUR_API_KEY
   ```
4. `pip install cdsapi`

## Step 5 — Telegram Alerts (optional)

1. Message @BotFather on Telegram → /newbot → get BOT_TOKEN
2. Get your CHAT_ID from @userinfobot
3. Copy .env.example to .env and fill in:
   ```
   TELEGRAM_BOT_TOKEN=your_token
   TELEGRAM_CHAT_ID=your_chat_id
   ```

## Environment Variables

See .env.example for all configurable variables.

## Data Directory Structure

```
hsae_v10/
├── data/
│   ├── NileFlow_v228_RSE_SAR.csv       ← Blue Nile SAR archive
│   ├── NileFlow_Rainfall_GPM_Daily.csv ← Nile GPM rainfall
│   ├── grdc/                           ← GRDC station CSVs
│   └── gee/                            ← GEE export outputs
├── HSAE_Data/                          ← GRDC bulk data
└── outputs/                            ← Generated reports
```

## Troubleshooting

| Error | Solution |
|-------|---------|
| GEE not authenticated | Run: earthengine authenticate |
| GRACE-FO 401 error | Check ~/.netrc credentials |
| GloFAS 403 error | Accept terms at CDS portal |
| GRDC data missing | Register and request at grdc.bafg.de |
| API connection refused | Run: uvicorn api_server:app --port 8000 |
| streamlit not found | pip install streamlit |

## Python Version

Requires Python 3.10+ (tested on 3.10, 3.11, 3.12).
