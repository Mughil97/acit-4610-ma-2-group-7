"""NSGA-II: fast non-dominated sorting, crowding distance, binary tournament
selection, and elitist (mu + lambda) environmental selection."""

from app.algorithms.base import MOEA


def non_dominated_sort(objectives):
    """Split the indices of objectives into Pareto fronts F1, F2, ... (a list of lists of indices)."""
    raise NotImplementedError


def crowding_distance(objectives, front):
    """Crowding distance of each member of one front (a list, in the same order as front)."""
    raise NotImplementedError


class NSGA2(MOEA):
    name = "NSGA-II"

    def select_parents(self, population, objectives):
        """Binary tournament: lower rank wins, ties broken by larger crowding distance.

        Return the mating pool: a list of pop_size individuals (use .copy() when adding one).
        """
        raise NotImplementedError

    def environmental_selection(self, population, objectives, offspring, offspring_objectives):
        """Merge parents and offspring, fill by front, truncate the last front by crowding.

        Return (next_population, next_objectives), both of length pop_size.
        """
        raise NotImplementedError
