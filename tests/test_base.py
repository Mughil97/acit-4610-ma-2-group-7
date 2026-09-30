"""Tests for the shared MOEA loop, with problem and operator stubs patched out."""

import unittest
from unittest import mock

import numpy as np

from app.algorithms.base import MOEA
from tests.helpers import tiny_config, tiny_instance


class _PassThroughMOEA(MOEA):
    """Keeps the whole population as parents and replaces it with the offspring."""

    name = "pass-through"

    def select_parents(self, population, objectives):
        return np.arange(len(population))

    def environmental_selection(self, population, objectives, offspring, offspring_objectives):
        return offspring, offspring_objectives


class BaseLoopTest(unittest.TestCase):
    def setUp(self):
        base = "app.algorithms.base"
        self.repair = mock.Mock(side_effect=lambda c, instance, rng: c)
        patches = [
            mock.patch(f"{base}.init_population", side_effect=lambda inst, n, rng: [np.zeros(2) for _ in range(n)]),
            mock.patch(f"{base}.repair", self.repair),
            mock.patch(f"{base}.crossover", side_effect=lambda a, b, prob, rng: (a.copy(), b.copy())),
            mock.patch(f"{base}.mutate", side_effect=lambda c, prob, rng: c),
            mock.patch(f"{base}.decode", side_effect=lambda c, inst: (c, c)),
            mock.patch(f"{base}.evaluate", return_value=(1.0, 2.0)),
            mock.patch(f"{base}.non_dominated", side_effect=lambda objs: objs[:1]),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

    def test_moea_is_abstract(self):
        with self.assertRaises(TypeError):
            MOEA(tiny_instance(), tiny_config(), seed=1)

    def test_stops_once_budget_is_spent(self):
        # 4 initial + 4 per generation: 4 -> 8 -> 12, which is the first count >= 10.
        algo = _PassThroughMOEA(tiny_instance(), tiny_config(pop_size=4, max_evaluations=10), seed=1)
        algo.run()
        self.assertEqual(algo.evaluations, 12)

    def test_every_individual_is_repaired(self):
        algo = _PassThroughMOEA(tiny_instance(), tiny_config(pop_size=4, max_evaluations=10), seed=1)
        algo.run()
        self.assertEqual(self.repair.call_count, algo.evaluations)

    def test_returns_non_dominated_objectives(self):
        front = _PassThroughMOEA(tiny_instance(), tiny_config(), seed=1).run()
        np.testing.assert_array_equal(front, [[1.0, 2.0]])


if __name__ == "__main__":
    unittest.main()
