"""Paired statistical comparison of MOEA hypervolume values across common random seeds."""

from scipy.stats import wilcoxon


def paired_wilcoxon(values_a, values_b):
    """Return a paired two-sided Wilcoxon signed-rank result for equal-length HV samples.

    Runs are paired by seed, so this test compares the two algorithms under matched stochastic runs.
    If every paired difference is exactly zero, return statistic=0 and p=1.
    """
    if len(values_a) != len(values_b):
        raise ValueError("Paired Wilcoxon samples must have the same length")
    if not values_a:
        raise ValueError("Paired Wilcoxon samples must not be empty")
    if all(a == b for a, b in zip(values_a, values_b)):
        return 0.0, 1.0
    result = wilcoxon(values_a, values_b, alternative="two-sided", method="auto")
    return float(result.statistic), float(result.pvalue)
