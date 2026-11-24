import pandas as pd
import pytest

from legalbias import metrics


def _run(values, task="CRED", model="m"):
    return pd.DataFrame([{"model": model, "task": task, "pid": f"p{i}", "value": v, "status": "ok"}
                         for i, v in enumerate(values)])


def test_identical_runs_are_fully_stable():
    t = metrics.stability_table(_run([5, 6, 7, 8]), _run([5, 6, 7, 8]))
    row = t.iloc[0]
    assert row["agreement"] == 1.0 and row["noise_flip_rate"] == 0.0 and row["n"] == 4


def test_noise_flip_rate_and_differences():
    t = metrics.stability_table(_run([5, 6, 7, 8]), _run([5, 6, 9, 8]))
    row = t.iloc[0]
    assert row["noise_flip_rate"] == pytest.approx(0.25)
    assert row["mean_abs_diff"] == pytest.approx(0.5)
    assert row["max_abs_diff"] == 2


def test_failed_answers_are_left_out():
    b = _run([5, 6, 7, 8])
    b.loc[3, "status"] = "refusal"
    assert metrics.stability_table(_run([5, 6, 7, 8]), b).iloc[0]["n"] == 3


def test_replication_requires_same_sign_and_both_significant():
    a = pd.DataFrame({"model": "m", "task": "CRED", "vid": ["v1", "v2", "v3"],
                      "MSD": [-0.6, -0.5, 0.3], "CFR": [0.5, 0.4, 0.2],
                      "p_wilcoxon_holm": [0.01, 0.01, 0.01]})
    b = a.copy()
    b["MSD"] = [-0.5, -0.4, -0.2]           # v3 changes sign
    b["p_wilcoxon_holm"] = [0.02, 0.20, 0.01]  # v2 not significant in run B
    r = metrics.replication_table(a, b).set_index("vid")
    assert r.loc["v1", "replicated"]
    assert not r.loc["v2", "replicated"]
    assert not r.loc["v3", "replicated"]
