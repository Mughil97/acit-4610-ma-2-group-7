"""Hypervolume: how much of the objective space a front dominates (bigger is better)."""

REFERENCE_POINT = (1.1, 1.1)  # after scaling, a bit worse than the worst value found on the instance


def normalise(points, ideal, nadir):
    """Scale each objective to 0..1, from the best (ideal) to the worst (nadir) value found on the instance."""
    return [tuple((value - low) / ((high - low) or 1) for value, low, high in zip(point, ideal, nadir))
            for point in points]


def hypervolume_2d(front, reference_point=REFERENCE_POINT):
    """Area dominated by the front up to the reference point; both objectives minimised."""
    area, height = 0.0, reference_point[1]
    for f1, f2 in sorted(set(front)):  # left to right
        if f1 < reference_point[0] and f2 < height:
            area += (reference_point[0] - f1) * (height - f2)
            height = f2
    return area
