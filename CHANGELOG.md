# Changelog — hydrosovereign

## [6.2.0] — April 2026 (current)

### Fixed 🔴 Critical
- **ATDI formula** recalibrated with scipy L-BFGS-B against 14 published basin values (RMSE=4.1%, was ~40%)
- **HIFD formula** recalibrated (RMSE=1.8%)
- **NegotiationAI** switched to GBM Regressor (was Classifier) — GERD now gives p≈0.40 (was 0.21)
- **WQI** DO sub-index fixed (was using wrong normalization)

### Added 🟢
- `analyze_basin()` + `analyze_all_basins()` unified high-level API
- `hydrosovereign/cli.py` — CLI: `hydrosovereign analyze "Blue Nile (GERD)"`
- `hydrosovereign/async_alerts.py` — asyncio concurrent basin monitoring
- `hydrosovereign/data/nile_basin_sample.json` — 5-year Nile Basin sample dataset
- `LinearForecast` — honest Ridge Regression forecaster (renamed from LSTMForecast proxy)
- `LSTMForecast` — real MLP (sklearn MLPRegressor) with hidden layers
- `NegotiationAI.save/load()` — joblib model persistence
- `NegotiationAI.feature_importance()` — GBM feature importances
- WQI physicochemical mode (WHO 2017 standard: ph, do, bod, turbidity, nitrates, tds, ec)
- Dynamic `ConflictPredictor` sensitivity (aridity + storage density + nc — no hardcoding)
- Python logging throughout all modules

### Changed 🟡
- `compute_negotiation_probability()` intercept recalibrated (0.82→0.846)
- `compute_conflict_index()` denominator corrected (now uses /95 and /80)
- `pyproject.toml` updated: scikit-learn, geo, ml, cli entry point

## [6.1.0] — April 2026
- Added hydrosovereign.ai (NegotiationAI, BayesianRisk, ConflictPredictor, LSTMForecast)
- Added hydrosovereign.models (HBVModel OOP)
- Added hydrosovereign.viz (plots, maps)
- 51 pytest tests

## [6.0.1] — April 2026
- True SCE-UA calibration
- 37 pytest tests
- CHANGELOG.md

## [6.0.0] — March 2026
- Initial release: ATDI, HIFD, NSE, KGE, WQI, CI, HBV-96, 26 basins, UNWC 1997
