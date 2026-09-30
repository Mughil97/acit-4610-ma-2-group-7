"""Statistical comparison of the two MOEAs over independent runs."""


def summarise(values):
    """Mean, std, best and worst of a list of metric values over runs, as a dict."""
    raise NotImplementedError


def mann_whitney_u(a, b):
    """Two-sided Mann-Whitney U test on two lists of values; returns (U, p-value)."""
    raise NotImplementedError


def results_table(rows):
    """Per instance/config/algorithm table (a list of dicts): HV mean/std/best/worst, #ND, mean time."""
    raise NotImplementedError
