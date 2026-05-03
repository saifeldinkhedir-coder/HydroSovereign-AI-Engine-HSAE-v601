"""
tests/test_package.py — hydrosovereign package test suite
==========================================================
Comprehensive pytest suite covering all package modules.
Run: pytest tests/ -v

Author: Seifeldin M.G. Alkhedir · ORCID: 0000-0003-0821-2991
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
import pytest
from hydrosovereign.indices import (
    compute_atdi, compute_hifd, compute_nse, compute_kge,
    compute_wqi, compute_conflict_index,
    compute_negotiation_probability, compute_all_indices,
)
from hydrosovereign.hbv import run_hbv96, calibrate_hbv_sceua
from hydrosovereign.basins import BasinRegistry, get_basin, list_basins, BASINS_26
from hydrosovereign.legal import (
    get_triggered_articles, get_legal_assessment,
    check_art7_nsh, check_art20_envflow,
    check_art33_dispute, check_art35_emergency,
)
from hydrosovereign.alerts import (
    AlertLevel, check_atdi_alert, check_hifd_alert,
    format_alert_message,
)


# ── Fixtures ───────────────────────────────────────────────────────────────────
@pytest.fixture
def gerd():
    return dict(runoff_c=0.38, cap_bcm=74.0, n_countries=3, dispute_level=4)

@pytest.fixture
def amazon():
    return dict(runoff_c=0.65, cap_bcm=0.4, n_countries=1, dispute_level=1)

@pytest.fixture
def forcing():
    n   = 365
    doy = np.arange(n)
    P   = np.maximum(0, 2.5*np.sin(np.pi*doy/180)
                     + np.random.default_rng(42).exponential(0.3, n))
    T   = 25 + 5*np.sin(2*np.pi*doy/365)
    return P, T


# ── 1. ATDI ────────────────────────────────────────────────────────────────────
class TestATDI:

    def test_bounds(self):
        for rc in [0.05, 0.3, 0.7, 0.95]:
            for cap in [0, 10, 74, 200]:
                for nc in [1, 2, 5]:
                    for d in range(5):
                        v = compute_atdi(rc, cap, nc, d)
                        assert 5 <= v <= 95

    def test_gerd_high(self, gerd):
        assert compute_atdi(**gerd) >= 45

    def test_amazon_low(self, amazon):
        assert compute_atdi(**amazon) < 40

    def test_monotone_dispute(self):
        vals = [compute_atdi(0.3, 10, 2, d) for d in range(5)]
        assert all(vals[i] <= vals[i+1] for i in range(4))

    def test_monotone_storage(self):
        assert compute_atdi(0.3, 5, 2, 0) < compute_atdi(0.3, 74, 2, 0)

    def test_monotone_countries(self):
        assert compute_atdi(0.3, 10, 2, 0) < compute_atdi(0.3, 10, 5, 0)

    def test_invalid_runoff_zero(self):
        with pytest.raises(ValueError): compute_atdi(0.0, 74, 3, 4)

    def test_invalid_dispute(self):
        with pytest.raises(ValueError): compute_atdi(0.38, 74, 3, 5)

    def test_invalid_countries(self):
        with pytest.raises(ValueError): compute_atdi(0.38, 74, 0, 4)

    def test_invalid_cap(self):
        with pytest.raises(ValueError): compute_atdi(0.38, -1, 3, 4)


# ── 2. HIFD ────────────────────────────────────────────────────────────────────
class TestHIFD:

    def test_bounds(self):
        for rc in [0.05, 0.3, 0.8]:
            for cap in [0, 10, 162]:
                for nc in [1, 3]:
                    for d in range(5):
                        v = compute_hifd(rc, cap, nc, d)
                        assert 5 <= v <= 80

    def test_gerd_triggers_art20(self, gerd):
        assert compute_hifd(**gerd) >= 25

    def test_arid_higher_than_humid(self):
        assert compute_hifd(0.08, 10, 2, 0) > compute_hifd(0.65, 10, 2, 0)

    def test_large_storage_increases_hifd(self):
        assert compute_hifd(0.3, 1, 2, 0) < compute_hifd(0.3, 50, 2, 0)


# ── 3. NSE / KGE ───────────────────────────────────────────────────────────────
class TestModelMetrics:

    def test_nse_perfect(self):
        q = np.array([100., 200., 150.])
        assert abs(compute_nse(q, q) - 1.0) < 1e-9

    def test_nse_mean(self):
        q = np.array([100., 200., 150., 180.])
        assert abs(compute_nse(q, np.full_like(q, q.mean()))) < 1e-9

    def test_nse_mismatch_raises(self):
        with pytest.raises(ValueError): compute_nse([1,2,3],[1,2])

    def test_nse_zero_variance_raises(self):
        with pytest.raises(ValueError): compute_nse([5,5,5],[4,5,6])

    def test_kge_perfect(self):
        q = np.array([100., 200., 150.])
        assert abs(compute_kge(q, q) - 1.0) < 1e-9

    def test_kge_finite(self):
        q_obs = np.array([100., 200., 150., 180.])
        q_bad = np.array([10., 5., 3., 8.])
        kge = compute_kge(q_obs, q_bad)
        assert np.isfinite(kge)


# ── 4. Conflict Index ──────────────────────────────────────────────────────────
class TestConflictIndex:

    def test_range(self):
        for d in range(5):
            for nc in [1, 2, 5]:
                atdi = compute_atdi(0.3, 10, nc, d)
                hifd = compute_hifd(0.3, 10, nc, d)
                ci   = compute_conflict_index(atdi, hifd, d, nc)
                assert 0 <= ci <= 1

    def test_gerd_high(self, gerd):
        atdi = compute_atdi(**gerd)
        hifd = compute_hifd(**gerd)
        ci   = compute_conflict_index(atdi, hifd, gerd['dispute_level'], gerd['n_countries'])
        assert ci >= 0.5

    def test_amazon_low(self, amazon):
        atdi = compute_atdi(**amazon)
        hifd = compute_hifd(**amazon)
        ci   = compute_conflict_index(atdi, hifd, amazon['dispute_level'], amazon['n_countries'])
        assert ci < 0.4


# ── 5. Negotiation AI ──────────────────────────────────────────────────────────
class TestNegotiationAI:

    def test_probability_range(self):
        for atdi in [5, 40, 80]:
            for hifd in [5, 30, 70]:
                r = compute_negotiation_probability(atdi, hifd, 2)
                assert 0.20 <= r["p_success"] <= 0.90

    def test_low_tension_cooperative(self):
        r = compute_negotiation_probability(15, 8, 2)
        assert r["p_success"] >= 0.55

    def test_high_tension_critical(self):
        r = compute_negotiation_probability(85, 70, 6)
        assert r["risk"] == "CRITICAL"

    def test_result_keys(self):
        r = compute_negotiation_probability(50, 35, 3)
        assert set(r.keys()) == {"p_success","strategy","un_path","risk"}


# ── 6. HBV-96 ─────────────────────────────────────────────────────────────────
class TestHBV96:

    def test_no_negative_discharge(self, forcing):
        P, T = forcing
        assert np.all(run_hbv96(P, T, 174000)["Q_sim"] >= 0)

    def test_output_length(self, forcing):
        P, T = forcing
        res  = run_hbv96(P, T, 174000)
        assert len(res["Q_sim"]) == len(P)

    def test_output_keys(self, forcing):
        P, T = forcing
        res  = run_hbv96(P, T, 174000)
        for k in ["Q_sim","SM","AET","SNOW","SUZ","SLZ","n_days"]:
            assert k in res

    def test_soil_moisture_bounds(self, forcing):
        P, T = forcing
        res  = run_hbv96(P, T, 174000, runoff_c=0.38)
        FC   = 250.0 * 0.38
        assert np.all(res["SM"] >= 0)
        assert np.all(res["SM"] <= FC + 1e-3)

    def test_mismatched_raises(self):
        with pytest.raises(ValueError):
            run_hbv96([1,2,3],[1,2], area_km2=100000)

    def test_zero_area_raises(self):
        with pytest.raises(ValueError):
            run_hbv96([1,2],[20,20], area_km2=0)

    def test_sceua_returns_nse(self, forcing):
        P, T   = forcing
        Q_obs  = run_hbv96(P, T, 174000)["Q_sim"]
        result = calibrate_hbv_sceua(Q_obs, P, T, 174000,
                                      n_complexes=2, n_per_complex=6,
                                      max_iter=20)
        assert "nse" in result
        assert "params" in result
        assert "converged" in result
        assert result["nse"] > -2.0


# ── 7. Basin Registry ──────────────────────────────────────────────────────────
class TestBasinRegistry:

    def test_count(self):
        assert len(BasinRegistry()) == 26

    def test_get_gerd(self):
        b = get_basin("Blue Nile (GERD)")
        assert b["runoff_c"] == 0.38
        assert "Ethiopia" in b["country"]

    def test_filter_africa(self):
        assert len(BasinRegistry().filter_by_continent("Africa")) == 6

    def test_filter_americas(self):
        assert len(BasinRegistry().filter_by_continent("Americas")) == 6

    def test_filter_dispute(self):
        assert len(BasinRegistry().filter_by_dispute(min_level=4)) >= 4

    def test_list_names(self):
        names = list_basins()
        assert len(names) == 26
        assert "Blue Nile (GERD)" in names

    def test_unknown_raises(self):
        with pytest.raises(KeyError): get_basin("Unknown XYZ")

    def test_all_have_lat_lon(self):
        for b in BASINS_26:
            assert b.get("lat"), f"{b['name']} missing lat"
            assert b.get("lon"), f"{b['name']} missing lon"


# ── 8. Legal & Alerts ──────────────────────────────────────────────────────────
class TestLegalAlerts:

    def test_art5_always(self):
        arts = get_triggered_articles(5, 5)
        assert "Art.5 ERU" in arts

    def test_art7_threshold(self):
        assert check_art7_nsh(40.0) is True
        assert check_art7_nsh(39.9) is False

    def test_art20_threshold(self):
        assert check_art20_envflow(25.0) is True
        assert check_art20_envflow(24.9) is False

    def test_art33_threshold(self):
        assert check_art33_dispute(55.0) is True
        assert check_art33_dispute(54.9) is False

    def test_art35_threshold(self):
        assert check_art35_emergency(70.0) is True
        assert check_art35_emergency(69.9) is False

    def test_legal_assessment_keys(self):
        result = get_legal_assessment(49.2, 33.4, 4, 3)
        for k in ["articles","recommendation","pathway","art7_nsh"]:
            assert k in result

    def test_atdi_alerts(self):
        assert check_atdi_alert(75.0) == AlertLevel.CRITICAL
        assert check_atdi_alert(60.0) == AlertLevel.WARNING
        assert check_atdi_alert(45.0) == AlertLevel.ALERT
        assert check_atdi_alert(30.0) == AlertLevel.INFO

    def test_hifd_alerts(self):
        assert check_hifd_alert(65.0) == AlertLevel.CRITICAL
        assert check_hifd_alert(45.0) == AlertLevel.WARNING
        assert check_hifd_alert(30.0) == AlertLevel.ALERT
        assert check_hifd_alert(20.0) == AlertLevel.INFO

    def test_format_message(self):
        msg = format_alert_message("Blue Nile", 49.2, 33.4, AlertLevel.ALERT)
        assert "Blue Nile" in msg
        assert "ALERT" in msg


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
