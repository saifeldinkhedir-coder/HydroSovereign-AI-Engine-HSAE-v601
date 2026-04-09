# Changelog — hydrosovereign

All notable changes to this package are documented here.

## [6.0.1] — April 2026

### Added
- True SCE-UA calibration algorithm (Duan et al., 1992)
  - Complex shuffling and evolution
  - Competitive Complex Evolution (CCE) local search
  - Latin Hypercube Sampling for initial population
- HBV-96: 6 output arrays (Q_sim, SM, AET, SNOW, SUZ, SLZ)
- `BasinRegistry.get_by_id()` method
- 51 pytest tests across 8 test classes
- Full docstrings with mathematical formulas
- Input validation with descriptive ValueError messages

### Changed
- `calibrate_hbv_sceua()`: upgraded from LHS-only to true SCE-UA
- `run_hbv96()`: improved ET formulation, added snow/groundwater outputs
- `BASINS_26`: enriched with context, legal_arts, eff_cat_km2 fields

### Fixed
- HBV-96: soil moisture bounded correctly to [0, FC]
- ATDI/HIFD: added validation for all input parameters

## [6.0.0] — March 2026

### Added
- Initial release
- Core indices: ATDI, HIFD, NSE, KGE, WQI, CI, P(negotiation)
- HBV-96 rainfall-runoff model
- 26 transboundary basin registry
- UNWC 1997 legal engine
- 4-level alert system
