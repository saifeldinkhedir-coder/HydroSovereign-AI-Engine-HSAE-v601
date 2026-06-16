# Changelog

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
