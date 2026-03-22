# Contributing to HSAE

Thank you for your interest in contributing to the HydroSovereign AI Engine (HSAE).

## Code of Conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org) Code of Conduct.
Please be respectful and constructive in all interactions.

## How to Contribute

### Reporting Bugs

Open an issue at https://github.com/saifeldinkhedir-coder/HydroSovereign-AI-Engine-HSAE-/issues with:
- A clear title and description
- Steps to reproduce
- Expected vs actual behaviour
- HSAE version, Python version, OS

### Suggesting Enhancements

Open an issue labelled `enhancement` and describe:
- The use case (which transboundary basin problem does this address?)
- Proposed API / interface
- References to relevant literature

### Submitting Pull Requests

1. Fork the repository and create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Follow the coding standards (see below).

3. Add or update tests in `test_hsae_plugin.py`. All 296 tests must continue to pass:
   ```bash
   python test_hsae_plugin.py
   ```

4. Update docstrings. Every function must document:
   - Input parameters and types
   - Return value and type
   - Relevant literature reference (author year, journal, doi)

5. Open a pull request against `main` with a clear description.

## Coding Standards

- **Python 3.9+** — no f-strings requiring 3.10+
- **Zero QGIS imports at module level** — all `from qgis.*` inside `try/except`
  so the test suite can run without QGIS installed
- **No invented numbers** — every numeric constant must cite a source
- **Pure-Python fallbacks** — all optional dependencies (requests, numpy, ee)
  must have fallback paths
- **Type hints** on all public functions
- Line length ≤ 100 characters
- Docstrings in NumPy style

## Adding a New Basin

1. Add entry to `basins_data.py` `BASINS_26` list (or `GLOFAS_BASINS` for GloFAS-only)
2. Add GRDC station to `grdc_data_manager.py` `GRDC_STATION_CATALOG`
3. Add coordinates to `grace_fo.py` `GRACE_BASIN_COORDS`
4. Add coordinates to `smap_loader.py` `SMAP_BASIN_COORDS`
5. Add at least one entry to `benchmark_comparison.py` `LITERATURE_BENCHMARKS`
   (use `_gap()` if no published benchmark exists — never invent a value)
6. Add treaty entries to `treaty_diff.py` if applicable
7. Add test in Group A (`TestBasinsData`) verifying the new basin

## Adding a New Treaty

1. Add to `treaty_diff.py` `TREATIES` list with `un_treaty_url` pointing to
   the UN Treaty Collection entry (https://treaties.un.org/)
2. Add citation to `paper.bib`
3. The `n_treaties` count in test Group O will auto-update

## Scientific Integrity Policy

HSAE is an academic tool. All numeric benchmark values must be traceable to
peer-reviewed publications via DOI + table/figure number. See
`benchmark_comparison.py` for the `_rec()` / `_gap()` pattern.

## Contact

Seifeldin M. G. Alkedir  
saifeldinkhedir@gmail.com  
ORCID: 0000-0003-0821-2991
