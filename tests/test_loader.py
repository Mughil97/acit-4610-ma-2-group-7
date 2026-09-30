import tempfile
import unittest
from pathlib import Path

import numpy as np

from app.config import INSTANCES
from app.problem.loader import load_by_name, load_instance

# 3 facilities, 2 customers; customer 1's costs wrap onto a second line like the real files.
TINY = """ 3 2
 100 10.
 200 20.
 300 0.
 5
 1.5 2.5
 3.5
 7
 4.0 5.0 6.0
"""


class LoadInstanceTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)

    def _write(self, text: str, name: str = "tiny") -> Path:
        path = self.dir / f"{name}.txt"
        path.write_text(text)
        return path

    def test_parses_all_fields(self):
        inst = load_instance(self._write(TINY))
        self.assertEqual(inst.name, "tiny")
        self.assertEqual((inst.m, inst.n), (3, 2))
        np.testing.assert_array_equal(inst.capacity, [100, 200, 300])
        np.testing.assert_array_equal(inst.fixed_cost, [10, 20, 0])
        np.testing.assert_array_equal(inst.demand, [5, 7])

    def test_alloc_cost_is_facility_by_customer(self):
        inst = load_instance(self._write(TINY))
        np.testing.assert_array_equal(inst.alloc_cost, [[1.5, 4.0], [2.5, 5.0], [3.5, 6.0]])

    def test_wrong_value_count_raises(self):
        path = self._write(TINY + " 99\n")
        with self.assertRaisesRegex(ValueError, "expected 16 values"):
            load_instance(path)

    def test_non_numeric_capacity_raises(self):
        # capa/capb/capc files use the literal word "capacity" as a placeholder.
        path = self._write(TINY.replace(" 100 10.", " capacity 10."))
        with self.assertRaises(ValueError):
            load_instance(path)

    def test_arrays_are_read_only(self):
        inst = load_instance(self._write(TINY))
        with self.assertRaises(ValueError):
            inst.fixed_cost[0] = 0

    def test_load_by_name_uses_data_dir(self):
        self._write(TINY, name="cap00")
        self.assertEqual(load_by_name("cap00", data_dir=self.dir).name, "cap00")


class RequiredInstancesTest(unittest.TestCase):
    SIZES = {"small": (16, 50), "medium": (25, 50), "large": (50, 50)}

    def test_sizes_match_assignment(self):
        for category, names in INSTANCES.items():
            for name in names:
                with self.subTest(name=name):
                    inst = load_by_name(name)
                    self.assertEqual((inst.m, inst.n), self.SIZES[category])
                    self.assertEqual(inst.alloc_cost.shape, (inst.m, inst.n))

    def test_total_capacity_covers_demand(self):
        for names in INSTANCES.values():
            for name in names:
                with self.subTest(name=name):
                    inst = load_by_name(name)
                    self.assertGreaterEqual(inst.capacity.sum(), inst.demand.sum())

    def test_cap41_spot_values(self):
        inst = load_by_name("cap41")
        self.assertEqual(inst.capacity[0], 5000)
        self.assertEqual(inst.fixed_cost[0], 7500)
        self.assertEqual(inst.fixed_cost[10], 0)  # really 0 in the OR-Library file
        self.assertEqual(inst.demand[0], 146)
        self.assertAlmostEqual(inst.alloc_cost[0, 0], 6739.725)
        self.assertAlmostEqual(inst.alloc_cost[15, 0], 6051.7)

    def test_cap121_last_value(self):
        inst = load_by_name("cap121")
        self.assertAlmostEqual(inst.alloc_cost[-1, -1], 2000.775)


if __name__ == "__main__":
    unittest.main()
