"""WEAT / SEAT association tests (Caliskan et al., 2017; May et al., 2019).

    s(w, A, B) = mean_{a in A} cos(w, a) - mean_{b in B} cos(w, b)
    S(X, Y, A, B) = sum_{x in X} s(x, A, B) - sum_{y in Y} s(y, A, B)
    d = (mean_x s(x) - mean_y s(y)) / std_{w in X u Y} s(w)

With A = negative legal concept (dangerous / guilty / dishonest) and
B = its positive opposite, d > 0 means X (LGBTQ+) is closer to the negative
pole than Y (heterosexual).
"""
from __future__ import annotations

import itertools
import math

import numpy as np


def _unit(M: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(M, axis=-1, keepdims=True)
    return M / np.where(n == 0, 1, n)


def association(W: np.ndarray, A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """s(w, A, B) for every row w of W."""
    W, A, B = _unit(W), _unit(A), _unit(B)
    return (W @ A.T).mean(axis=1) - (W @ B.T).mean(axis=1)


def effect_size(X, Y, A, B) -> float:
    sx, sy = association(X, A, B), association(Y, A, B)
    sd = np.concatenate([sx, sy]).std(ddof=1)
    return float((sx.mean() - sy.mean()) / sd) if sd > 0 else 0.0


def permutation_p(X, Y, A, B, n_perm: int = 10_000, exact_limit: int = 20_000,
                  seed: int = 0) -> float:
    """One-sided p = P_i[S(X_i, Y_i) >= S(X, Y)] over equal-size re-partitions
    of X u Y. Exact enumeration when the number of partitions is small,
    otherwise Monte-Carlo with the (k+1)/(n+1) correction."""
    s = np.concatenate([association(X, A, B), association(Y, A, B)])
    nx, n = len(X), len(X) + len(Y)
    total = s.sum()
    observed = 2 * s[:nx].sum() - total
    if math.comb(n, nx) <= exact_limit:
        stats_ = np.array([2 * s[list(c)].sum() - total
                           for c in itertools.combinations(range(n), nx)])
        return float(np.mean(stats_ >= observed - 1e-12))
    rng = np.random.default_rng(seed)
    perms = np.argsort(rng.random((n_perm, n)), axis=1)[:, :nx]
    stats_ = 2 * s[perms].sum(axis=1) - total
    return float((np.sum(stats_ >= observed - 1e-12) + 1) / (n_perm + 1))


def paired_effect(X, Y, A, B) -> tuple[float, float]:
    """Paired (counterfactual) variant of SEAT.

    X[i] and Y[i] are the same frame with only the identity term changed, so
    the frame-to-frame variance is a nuisance. With delta_i = s(x_i) - s(y_i):
        d_z = mean(delta) / std(delta)
    and an exact one-sided sign-flip test (2^n sign patterns, n <= 16)
    or Monte-Carlo otherwise.
    Returns (d_z, p)."""
    delta = association(X, A, B) - association(Y, A, B)
    sd = delta.std(ddof=1)
    dz = float(delta.mean() / sd) if sd > 0 else 0.0
    n = delta.size
    if n <= 16:
        signs = np.array(list(itertools.product((1, -1), repeat=n)))
    else:
        signs = np.random.default_rng(0).choice((1, -1), size=(10_000, n))
    null = (signs * delta).mean(axis=1)
    p = float(np.mean(null >= delta.mean() - 1e-15))
    return dz, p


def center(H: np.ndarray, mu: np.ndarray | None = None) -> np.ndarray:
    """Remove the common mean direction (anisotropy correction, Ethayarajh 2019)."""
    mu = H.mean(axis=0) if mu is None else mu
    return H - mu


def standardize(H: np.ndarray) -> np.ndarray:
    """Center and scale every dimension to unit variance, so that the few
    'massive activation' dimensions do not dominate the cosine similarity."""
    sd = H.std(axis=0)
    return (H - H.mean(axis=0)) / np.where(sd == 0, 1, sd)


def anisotropy(H: np.ndarray, n_pairs: int = 2000, seed: int = 0) -> float:
    """Average cosine similarity between random pairs of different sentences."""
    rng = np.random.default_rng(seed)
    i = rng.integers(0, len(H), n_pairs)
    j = rng.integers(0, len(H), n_pairs)
    keep = i != j
    U = _unit(H)
    return float(np.mean(np.sum(U[i[keep]] * U[j[keep]], axis=1)))
