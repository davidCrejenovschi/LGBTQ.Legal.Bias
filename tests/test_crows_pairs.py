import pandas as pd
import pytest

from legalbias import crows_pairs as cp


def test_load_keeps_only_sexual_orientation(tmp_path):
    csv = tmp_path / "crows.csv"
    pd.DataFrame({
        "sent_more": ["a", "b", "c"], "sent_less": ["x", "y", "z"],
        "stereo_antistereo": ["stereo", "antistereo", "stereo"],
        "bias_type": ["sexual-orientation", "sexual-orientation", "gender"],
    }).to_csv(csv)
    df = cp.load(csv)
    assert len(df) == 2 and set(df["bias_type"]) == {"sexual-orientation"}


def test_summarize_counts_preference_for_the_more_stereotyping_sentence():
    scores = pd.DataFrame({
        "ll_more": [-10.0, -12.0, -9.0, -20.0],
        "ll_less": [-11.0, -11.0, -10.0, -15.0],
        "n_more": [5, 6, 5, 10], "n_less": [5, 5, 5, 5],
        "stereo_antistereo": ["stereo", "stereo", "antistereo", "antistereo"],
    })
    s = cp.summarize(scores, n_boot=500)
    assert s["n_pairs"] == 4
    assert s["share_prefers_stereotype"] == pytest.approx(0.5)   # pairs 1 and 3
    assert s["share_stereo"] == pytest.approx(0.5)
    assert s["share_antistereo"] == pytest.approx(0.5)
    # per-token: -2.0 vs -2.2, -2.0 vs -2.2, -1.8 vs -2.0, -2.0 vs -3.0 -> all prefer sent_more
    assert s["share_prefers_stereotype_per_token"] == pytest.approx(1.0)
    assert 0 <= s["ci95"][0] <= 0.5 <= s["ci95"][1] <= 1
    assert s["p_binomial_vs_50"] == pytest.approx(1.0)
