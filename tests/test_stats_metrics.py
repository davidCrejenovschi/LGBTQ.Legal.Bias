import numpy as np
import pandas as pd
import pytest

from legalbias import metrics, stats


def test_holm_matches_hand_computation():
    p = [0.01, 0.04, 0.03, 0.20]
    # sorted: 0.01*4=0.04, 0.03*3=0.09, 0.04*2=0.08->0.09 (monotone), 0.20*1=0.20
    assert np.allclose(stats.holm(p), [0.04, 0.09, 0.09, 0.20])


def test_mcnemar_exact():
    b_v = np.array([1] * 8 + [0] * 2 + [1] * 5, bool)
    b_r = np.array([0] * 8 + [1] * 2 + [1] * 5, bool)
    p, n10, n01 = stats.mcnemar_exact(b_v, b_r)
    assert (n10, n01) == (8, 2)
    assert p == pytest.approx(0.109375)          # 2 * P(X >= 8 | n=10, 0.5)
    assert stats.mcnemar_exact(b_r, b_r)[0] == 1.0


def test_rank_biserial_and_wilcoxon():
    d = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], float)
    assert stats.rank_biserial(d) == 1.0
    assert stats.rank_biserial(-d) == -1.0
    assert stats.wilcoxon_p(d) < 0.01
    assert stats.wilcoxon_p(np.zeros(10)) == 1.0


def test_bootstrap_ci_contains_mean():
    x = np.random.default_rng(0).normal(1.0, 1.0, 200)
    lo, hi = stats.bootstrap_ci(x, B=2000)
    assert lo < x.mean() < hi
    assert lo > 0.7 and hi < 1.3


def test_min_detectable_effect():
    assert stats.min_detectable_dz(100) == pytest.approx(0.280, abs=0.002)


def test_spearman_perm_perfect():
    r = stats.spearman_perm(np.arange(10), np.arange(10) ** 2, n_perm=2000)
    assert r["rho"] == pytest.approx(1.0)
    assert r["p_perm"] < 0.01


def _fake_df(task, ref_vals, lgb_vals, vid="M_gay_exp"):
    rows = []
    for i, (a, b) in enumerate(zip(ref_vals, lgb_vals)):
        for v, val in ((metrics.ids.ref(vid), a), (vid, b)):
            rows.append({"model": "m", "task": task, "sid": f"s{i}", "vid": v,
                         "value": val, "status": "ok"})
    return pd.DataFrame(rows)


def test_pair_metrics_signed_harm_direction():
    # credibility: LGBTQ+ variant gets LOWER credibility -> positive harm
    m = metrics.pair_metrics(np.array([5., 5, 6]), np.array([7., 7, 6]), "CRED")
    assert m["MSD"] == pytest.approx(4 / 3)
    assert m["CFR"] == pytest.approx(2 / 3)
    assert m["CFR_worse"] == pytest.approx(2 / 3)
    # recidivism: LGBTQ+ variant gets HIGHER risk -> positive harm
    m = metrics.pair_metrics(np.array([8., 7]), np.array([6., 7]), "REC")
    assert m["MSD"] == pytest.approx(1.0)


def test_pair_metrics_pretrial_binary():
    # custodial (>=4): v = [5,5,4,2], ref = [3,5,2,2] -> rates 0.75 vs 0.25
    m = metrics.pair_metrics(np.array([5., 5, 4, 2]), np.array([3., 5, 2, 2]), "PRE")
    assert m["custodial_v"] == 0.75 and m["custodial_ref"] == 0.25
    assert m["RD"] == pytest.approx(0.5)
    assert m["DIR"] == pytest.approx(0.25 / 0.75)
    assert (m["n10"], m["n01"]) == (2, 0)


def test_missing_answers_are_excluded_pairwise():
    m = metrics.pair_metrics(np.array([5., np.nan, 4]), np.array([5., 5, np.nan]), "REC")
    assert m["n_pairs"] == 1


def test_e1_table_end_to_end():
    df = _fake_df("REC", [4] * 10, [5] * 10)
    t = metrics.e1_table(df)
    assert len(t) == 1
    row = t.iloc[0]
    assert row["MSD"] == 1.0 and row["CFR"] == 1.0
    assert row["p_wilcoxon"] < 0.01
