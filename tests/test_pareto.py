import unittest
import numpy as np

from app.utils.pareto import dominates, non_dominated


class ParetoTest(unittest.TestCase):

    def test_dominance_allows_equality_in_one_objective(self):
        """Equal in one objective and better in another => dominance."""
        a = np.array([1.0, 2.0])
        b = np.array([1.0, 3.0])

        self.assertTrue(dominates(a, b))
        self.assertFalse(dominates(b, a))

    def test_identical_solutions_do_not_dominate(self):
        """A solution must be strictly better in at least one objective."""
        a = np.array([2.0, 3.0])
        b = np.array([2.0, 3.0])

        self.assertFalse(dominates(a, b))
        self.assertFalse(dominates(b, a))

    def test_clear_dominance(self):
        """Better in every objective => dominance."""
        a = np.array([1.0, 2.0])
        b = np.array([3.0, 4.0])

        self.assertTrue(dominates(a, b))
        self.assertFalse(dominates(b, a))

    def test_tradeoff_solutions_do_not_dominate_each_other(self):
        """Each solution is better in one objective."""
        a = np.array([1.0, 5.0])
        b = np.array([5.0, 1.0])

        self.assertFalse(dominates(a, b))
        self.assertFalse(dominates(b, a))

    def test_non_dominated_filter(self):
        """Dominated solutions should be removed."""
        objs = np.array([
            [1, 4],
            [2, 3],
            [3, 2],
            [4, 1],
            [4, 4]
        ], dtype=float)

        front = non_dominated(objs)

        self.assertEqual(len(front), 4)

        self.assertFalse(
            any(np.array_equal(row, [4, 4]) for row in front)
        )

    def test_duplicates_removed_from_front(self):
        """Duplicate objective vectors should appear only once."""
        objs = np.array([
            [1, 4],
            [1, 4],
            [2, 3],
            [3, 2]
        ], dtype=float)

        front = non_dominated(objs)

        self.assertEqual(len(front), 3)

    def test_single_solution_is_non_dominated(self):
        """A population containing one solution returns that solution."""
        objs = np.array([[2.0, 5.0]])

        front = non_dominated(objs)

        self.assertEqual(front.shape, (1, 2))
        np.testing.assert_array_equal(front[0], [2.0, 5.0])

    def test_empty_population(self):
        """An empty objective array should return an empty front."""
        objs = np.empty((0, 2))

        front = non_dominated(objs)

        self.assertEqual(front.shape, (0, 2))


if __name__ == "__main__":
    unittest.main()