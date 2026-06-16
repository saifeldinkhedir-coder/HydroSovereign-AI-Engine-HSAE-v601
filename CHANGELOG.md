# Changelog

## [6.8.1] — 2026-06 — Documentation consistency fix

### Fixed
- README/PyPI description fully reconciled with the v6.8.0 provenance
  engine: removed contradictory legacy examples and claims (the old
  `ATDI(**params)` heuristic call, "478 TFDD/ICOW", "NSE=0.63 vs GloFAS
  ERA5"), relabelled tabulated index values as *illustrative framework
  outputs* (not validated field measurements), updated the quick-start to
  the provenance-based API, citation to v6.8.1, and test count to 117.
- No code/behaviour change from 6.8.0; documentation only.


## [6.8.0] — 2026-06 — Major Scientific Revision

### Changed (breaking in spirit; backward-compatible via legacy module)
- **Provenance-bound index engine.** All indices now compute only from
  documented observations (`DataPoint` with source/reference/dates/quality)
  and return `INSUFFICIENT_DATA` when real data are absent — never a
  fabricated value.
- **HIFD fixed.** Takes independent `Q_nat` and `Q_obs`; no longer collapses
  algebraically to a constant.
- **ATDI is empirical.** Mean of per-period TDI (paper Eq. 1–2), computed
  from observed inflow/outflow series.
- **Empirical vs. normative separated.** AFSF/AHLB are empirical; ASI/ATCI/
  AWGI are declared normative composites with explicit, sensitivity-tested
  weights.
- **Treaty classifier genuinely trained** on the TFDD database (429 labelled
  treaties) with an honest model card (F1, ROC-AUC, CV, baseline).
- **Independent validation.** `validate_model_skill` rejects benchmarks that
  share the model's forcing source.

### Added
- `provenance`, `ingestion`, `validation`, `treaty_classifier` modules.
- `correlation_matrix` for honest disclosure of index independence.

### Deprecated
- `hydrosovereign.indices_legacy` — the original heuristic formulas, retained
  for backward compatibility with a `DeprecationWarning`. **Removal planned
  for v7.0.0.**

## [6.7.2] and earlier
- Heuristic index engine (now in `indices_legacy`).
