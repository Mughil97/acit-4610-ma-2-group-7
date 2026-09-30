"""Pareto dominance, both objectives minimised."""


def dominates(a, b):
    """a is not worse in any objective and strictly better in at least one."""
    return all(x <= y for x, y in zip(a, b)) and any(x < y for x, y in zip(a, b))


def non_dominated(objectives):
    """The unique points no other point dominates, sorted by f1."""
    unique = sorted({tuple(point) for point in objectives})
    return [point for point in unique if not any(dominates(other, point) for other in unique)]
