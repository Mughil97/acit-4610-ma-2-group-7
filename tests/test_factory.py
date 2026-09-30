import unittest

from app.algorithms import available_algorithms, create_algorithm
from app.algorithms.base import MOEA
from app.algorithms.nsga2 import NSGA2
from app.algorithms.vega import VEGA
from tests.helpers import tiny_config, tiny_instance


class FactoryTest(unittest.TestCase):
    def test_lists_registered_algorithms(self):
        self.assertEqual(available_algorithms(), ["nsga2", "vega"])

    def test_creates_matching_class(self):
        for name, cls in [("nsga2", NSGA2), ("vega", VEGA)]:
            algo = create_algorithm(name, tiny_instance(), tiny_config(), seed=1)
            self.assertIsInstance(algo, cls)
            self.assertIsInstance(algo, MOEA)

    def test_name_is_case_insensitive(self):
        self.assertIsInstance(create_algorithm("NSGA2", tiny_instance(), tiny_config(), seed=1), NSGA2)

    def test_passes_instance_config_and_seed(self):
        instance, config = tiny_instance(), tiny_config()
        algo = create_algorithm("vega", instance, config, seed=7)
        self.assertIs(algo.instance, instance)
        self.assertIs(algo.config, config)
        self.assertEqual(algo.evaluations, 0)

    def test_unknown_name_raises(self):
        instance, config = tiny_instance(), tiny_config()
        with self.assertRaisesRegex(ValueError, "Unknown algorithm 'spea2'"):
            create_algorithm("spea2", instance, config, seed=1)


if __name__ == "__main__":
    unittest.main()
