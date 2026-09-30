import unittest

from app.config import CONFIGS, INSTANCES, N_RUNS


class ConfigTest(unittest.TestCase):
    def test_required_instances(self):
        self.assertEqual(
            INSTANCES,
            {"small": ["cap41", "cap42"], "medium": ["cap101", "cap102"], "large": ["cap121", "cap122"]},
        )

    def test_three_uniquely_named_configs(self):
        self.assertEqual(len({c.name for c in CONFIGS}), 3)

    def test_pop_sizes_are_even(self):
        # MOEA._vary pairs consecutive parents, so an odd pool would drop one.
        for c in CONFIGS:
            self.assertEqual(c.pop_size % 2, 0, c.name)

    def test_at_least_ten_runs(self):
        self.assertGreaterEqual(N_RUNS, 10)


if __name__ == "__main__":
    unittest.main()
