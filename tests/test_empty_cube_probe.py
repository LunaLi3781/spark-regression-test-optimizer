import unittest
from scripts.probe_empty_cube import QUERIES, assess


class ReproducerControlTests(unittest.TestCase):
    def observations(self):
        obs = {k: {'rows': [[None, None, 1]]} for k in QUERIES}
        obs['keyed_control']['rows'] = []
        obs['nonempty_control']['rows'] = [[None, 7, 1], ['east', 7, 0]]
        return obs

    def test_reports_missing_grand_total_without_calling_it_new(self):
        obs = self.observations()
        obs['cube']['rows'] = []
        self.assertEqual(assess(obs)['mismatches'], ['cube'])

    def test_control_failure_blocks_inference(self):
        obs = self.observations()
        obs['global_control']['rows'] = []
        with self.assertRaises(ValueError):
            assess(obs)

    def test_missing_query_is_not_success(self):
        obs = self.observations()
        del obs['rollup']
        with self.assertRaises(ValueError):
            assess(obs)
