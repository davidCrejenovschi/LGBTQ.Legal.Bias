import numpy as np
import pandas as pd
import pytest

from legalbias import compas, seat
from legalbias import scenarios as sc
from legalbias.representations import all_sentences, load_sets, target_sentences


def _clusters(seed=0):
    rng = np.random.default_rng(seed)
    a_dir, b_dir = np.eye(16)[0], np.eye(16)[1]
    A = a_dir + 0.1 * rng.normal(size=(8, 16))
    B = b_dir + 0.1 * rng.normal(size=(8, 16))
    X = 0.8 * a_dir + 0.2 * b_dir + 0.1 * rng.normal(size=(8, 16))   # close to A
    Y = 0.2 * a_dir + 0.8 * b_dir + 0.1 * rng.normal(size=(8, 16))   # close to B
    return X, Y, A, B


def test_effect_size_sign_and_permutation():
    X, Y, A, B = _clusters()
    d = seat.effect_size(X, Y, A, B)
    assert d > 1.5
    assert seat.effect_size(Y, X, A, B) == pytest.approx(-d)
    assert seat.permutation_p(X, Y, A, B) < 0.01          # exact: C(16, 8) = 12870
    assert seat.permutation_p(Y, X, A, B) > 0.99


def test_paired_effect_detects_consistent_shift():
    X, Y, A, B = _clusters()
    dz, p = seat.paired_effect(X, Y, A, B)
    assert dz > 1 and p <= 1 / 256 + 1e-12            # exact sign-flip, 2^8 patterns
    dz_rev, p_rev = seat.paired_effect(Y, X, A, B)
    assert dz_rev == pytest.approx(-dz) and p_rev > 0.99


def test_standardize_gives_unit_variance():
    rng = np.random.default_rng(3)
    H = rng.normal(size=(50, 8)) * np.array([1, 1, 1, 1, 1, 1, 1, 500.0])  # one "massive" dimension
    Z = seat.standardize(H)
    assert np.allclose(Z.mean(axis=0), 0, atol=1e-9)
    assert np.allclose(Z.std(axis=0), 1)


def _split_fixture(seed=0, signal=True):
    """8 negative + 8 positive words x 3 frames; X close to the first 4 negative words only."""
    rng = np.random.default_rng(seed)
    dim, frames = 24, 3
    neg_dirs = rng.normal(size=(8, dim))
    pos_dirs = rng.normal(size=(8, dim))
    A = np.repeat(neg_dirs, frames, axis=0) + 0.05 * rng.normal(size=(24, dim))
    B = np.repeat(pos_dirs, frames, axis=0) + 0.05 * rng.normal(size=(24, dim))
    shift = 3 * (neg_dirs[:4].mean(axis=0) - pos_dirs[:4].mean(axis=0))
    X = rng.normal(size=(10, dim)) + (shift if signal else 0)
    Y = rng.normal(size=(10, dim))
    return X, Y, A, B, np.repeat(np.arange(8), frames)


def test_split_test_matches_seat_effect_size():
    X, Y, A, B, word_of = _split_fixture()
    T = np.vstack([X, Y])
    cneg = seat.word_associations(T, A, word_of, 8)[None]
    cpos = seat.word_associations(T, B, word_of, 8)[None]
    r = seat.split_difference_test(cneg, cpos, len(X), [0, 1, 2, 3], [0, 1, 2, 3])
    first_A, first_B = A[np.isin(word_of, [0, 1, 2, 3])], B[np.isin(word_of, [0, 1, 2, 3])]
    rest_A, rest_B = A[np.isin(word_of, [4, 5, 6, 7])], B[np.isin(word_of, [4, 5, 6, 7])]
    assert r["d_first"] == pytest.approx(seat.effect_size(X, Y, first_A, first_B))
    assert r["d_second"] == pytest.approx(seat.effect_size(X, Y, rest_A, rest_B))
    assert r["n_splits"] == 70 * 70


def test_split_test_detects_a_half_specific_association():
    X, Y, A, B, word_of = _split_fixture(signal=True)
    T = np.vstack([X, Y])
    cneg = seat.word_associations(T, A, word_of, 8)[None]
    cpos = seat.word_associations(T, B, word_of, 8)[None]
    r = seat.split_difference_test(cneg, cpos, len(X), [0, 1, 2, 3], [0, 1, 2, 3])
    assert r["delta"] > 0 and r["p"] < 0.05


def test_split_test_identical_words_give_no_difference():
    rng = np.random.default_rng(4)
    cneg = np.repeat(rng.normal(size=(1, 20, 1)), 8, axis=2)   # every word identical
    cpos = np.repeat(rng.normal(size=(1, 20, 1)), 8, axis=2)
    r = seat.split_difference_test(cneg, cpos, 10, [0, 1, 2, 3], [0, 1, 2, 3])
    assert r["delta"] == pytest.approx(0) and r["p"] == 1.0


def test_effect_size_null_is_small():
    rng = np.random.default_rng(1)
    X, Y, A, B = (rng.normal(size=(10, 32)) for _ in range(4))
    assert abs(seat.effect_size(X, Y, A, B)) < 2
    assert 0.0 < seat.permutation_p(X, Y, A, B, n_perm=2000) <= 1.0


def test_centering_reduces_anisotropy():
    rng = np.random.default_rng(2)
    H = rng.normal(size=(200, 64)) + 5.0      # common offset -> narrow cone
    assert seat.anisotropy(H) > 0.8
    assert abs(seat.anisotropy(seat.center(H))) < 0.1


def test_seat_sentence_sets():
    sets = load_sets()
    allset = all_sentences(sets)
    assert len(target_sentences("M_gay_exp", sets)) == len(target_sentences("M_het_exp", sets))
    assert "He lives with his husband." in target_sentences("M_gay_imp", sets)
    assert "She lives with her wife." in target_sentences("F_les_imp", sets)
    assert len(allset["A:REC:neg"]) == len(allset["A:REC:pos"]) == 24


def test_legal_moral_split_partitions_the_guilt_concept():
    sets = load_sets()
    legal, moral = sets["pre_split"]["legal"], sets["pre_split"]["moral"]
    original = sets["concepts"]["PRE"]
    for pole in ("negative", "positive"):
        assert not set(legal[pole]) & set(moral[pole])
        assert set(legal[pole]) | set(moral[pole]) == set(original[pole])


def test_compas_scenarios(tmp_path):
    df = pd.DataFrame({
        "id": [1, 2], "sex": ["Male", "Female"], "age": [25, 41],
        "c_charge_desc": ["Battery", "Grand Theft (Motor Vehicle)"],
        "c_charge_degree": ["M", "F"], "priors_count": [1, 4],
        "juv_fel_count": [0, 1], "juv_misd_count": [2, 0],
        "two_year_recid": [0, 1], "decile_score": [3, 8],
    })
    scen = compas.to_scenarios(df)
    assert compas.variants_for(scen[0]) == ["M_het_exp", "M_gay_exp", "M_bi_exp",
                                            "M_het_imp", "M_gay_imp", "M_ctrl"]
    assert compas.variants_for(scen[1])[1] == "F_les_exp"
    text = sc.render(scen[1], "F_les_imp")
    assert text.startswith("The defendant is a 41-year-old woman. She lives with her wife")
    assert "4 prior crimes" in text and "1 juvenile felony charge " in text
    for s in scen:
        assert sc.check_invariance(s) == []


def test_auc():
    assert compas.auc([1, 2, 3, 4], [0, 0, 1, 1]) == 1.0
    assert compas.auc([1, 1, 1, 1], [0, 1, 0, 1]) == 0.5
