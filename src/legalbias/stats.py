"""Statistical tests used in E1-E3."""
from __future__ import annotations

import numpy as np
from scipy import stats as st


def wilcoxon_p(d) -> float:
    """Two-sided Wilcoxon signed-rank test on paired differences d.
    Zero differences are dropped (zero_method='wilcox'). Returns 1.0 when
    every difference is zero (no evidence of any effect)."""
    d = np.asarray(d, dtype=float)
    d = d[~np.isnan(d)]
    if d.size == 0 or np.all(d == 0):
        return 1.0
    return float(st.wilcoxon(d, zero_method="wilcox", alternative="two-sided").pvalue)


def rank_biserial(d) -> float:
    """Matched-pairs rank-biserial correlation r = (W+ - W-) / (W+ + W-),
    in [-1, 1]; effect size for the Wilcoxon test (Kerby, 2014)."""
    d = np.asarray(d, dtype=float)
    d = d[(~np.isnan(d)) & (d != 0)]
    if d.size == 0:
        return 0.0
    ranks = st.rankdata(np.abs(d))
    w_pos, w_neg = ranks[d > 0].sum(), ranks[d < 0].sum()
    return float((w_pos - w_neg) / (w_pos + w_neg))


def mcnemar_exact(b_v, b_ref) -> tuple[float, int, int]:
    """Exact McNemar test on paired binary outcomes.
    Returns (p, n10, n01) with n10 = #(v=1, ref=0), n01 = #(v=0, ref=1)."""
    b_v = np.asarray(b_v, dtype=bool)
    b_ref = np.asarray(b_ref, dtype=bool)
    n10 = int(np.sum(b_v & ~b_ref))
    n01 = int(np.sum(~b_v & b_ref))
    n = n10 + n01
    if n == 0:
        return 1.0, n10, n01
    return float(st.binomtest(n10, n, 0.5).pvalue), n10, n01


def holm(pvals) -> np.ndarray:
    """Holm-Bonferroni step-down adjusted p-values (monotone, capped at 1)."""
    p = np.asarray(pvals, dtype=float)
    m = p.size
    order = np.argsort(p)
    adj = np.empty(m)
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, (m - rank) * p[idx])
        adj[idx] = min(1.0, running)
    return adj


def bootstrap_ci(x, stat=np.mean, B: int = 10_000, alpha: float = 0.05,
                 seed: int = 0) -> tuple[float, float]:
    """Percentile bootstrap CI. x is resampled with replacement (unit = scenario)."""
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    if x.size == 0:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, x.size, size=(B, x.size))
    boots = np.apply_along_axis(stat, 1, x[idx]) if stat is not np.mean else x[idx].mean(axis=1)
    return float(np.quantile(boots, alpha / 2)), float(np.quantile(boots, 1 - alpha / 2))


def spearman_perm(x, y, n_perm: int = 10_000, seed: int = 0) -> dict:
    """Spearman rho with a two-sided permutation p-value and a bootstrap CI."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = ~(np.isnan(x) | np.isnan(y))
    x, y = x[ok], y[ok]
    n = x.size
    if n < 3 or np.all(x == x[0]) or np.all(y == y[0]):
        return {"rho": float("nan"), "p_perm": float("nan"), "ci": (float("nan"),) * 2, "n": n}
    rho = st.spearmanr(x, y).statistic
    rng = np.random.default_rng(seed)
    rx, ry = st.rankdata(x), st.rankdata(y)
    rx_c = (rx - rx.mean()) / rx.std()
    perms = np.array([rng.permutation(ry) for _ in range(n_perm)])
    perms_c = (perms - perms.mean(axis=1, keepdims=True)) / perms.std(axis=1, keepdims=True)
    null = (perms_c * rx_c).mean(axis=1)
    p = (np.sum(np.abs(null) >= abs(rho) - 1e-12) + 1) / (n_perm + 1)
    boots = []
    for _ in range(2000):
        i = rng.integers(0, n, n)
        if np.all(x[i] == x[i][0]) or np.all(y[i] == y[i][0]):
            continue
        boots.append(st.spearmanr(x[i], y[i]).statistic)
    ci = (float(np.nanquantile(boots, 0.025)), float(np.nanquantile(boots, 0.975)))
    return {"rho": float(rho), "p_perm": float(p), "ci": ci, "n": int(n)}


def min_detectable_dz(n: int, alpha: float = 0.05, power: float = 0.8) -> float:
    """Smallest standardised paired effect d_z detectable with a two-sided test
    (normal approximation): d_z = (z_{1-a/2} + z_{power}) / sqrt(n)."""
    return float((st.norm.ppf(1 - alpha / 2) + st.norm.ppf(power)) / np.sqrt(n))
