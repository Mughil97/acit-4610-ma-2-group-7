"""Multi-objective performance metrics.

Both MOEAs use the same normalisation bounds and HV reference point per instance.
"""


def normalise(objectives, ideal, nadir):
    """Min-max scale a list of (f1, f2) points using bounds shared across all compared runs."""
    raise NotImplementedError


def hypervolume_2d(objectives, ref_point):
    """Exact 2-D hypervolume of a list of (f1, f2) points for minimisation."""
    raise NotImplementedError
