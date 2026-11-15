import unittest
from spark_compat.boundary import BOUNDARY, cube_expected
from spark_compat.core import compare, fingerprint
from spark_compat.validation import audit_boundary


class BoundaryTests(unittest.TestCase):
    def test_empty_global_aggregate_and_having(self):
        self.assertEqual(cube_expected([], False, -1), [[None, None, 1]])
        self.assertEqual(cube_expected([], False, 0), [])

    def test_null_keys_are_distinct_from_total_and_nulls_excluded_from_count(self):
        data = [(None, 5), ('east', None)]
        self.assertCountEqual(cube_expected(data, False, 0),
                              [[None, 5, 0], ['east', None, 0], [None, 5, 1]])
        self.assertCountEqual(cube_expected(data, True, 0),
                              [['east', None, 0], [None, 5, 1]])

    def test_duplicates_and_cancellation(self):
        self.assertCountEqual(cube_expected([('x', 7), ('x', 7), ('x', -14)], True, 0),
                              [['x', 0, 0], [None, 0, 1]])

    def test_audit_rejects_missing_results_and_reports_failed_oracle(self):
        run = {'suite': 'boundary', 'spark_version': 'test', 'case_fingerprint': fingerprint(BOUNDARY),
               'cases': [{'id': c['id'], 'status': 'ok', 'oracle_result': 'pass'} for c in BOUNDARY]}
        self.assertEqual(audit_boundary(run)['passed'], 32)
        run['cases'][0]['oracle_result'] = 'fail'
        self.assertEqual(len(audit_boundary(run)['failures']), 1)
        run['cases'].pop()
        with self.assertRaises(ValueError):
            audit_boundary(run)

    def test_equal_wrong_results_are_not_clean(self):
        run = {'format': 1, 'case_fingerprint': 'x', 'profile': 'defaults', 'row_limit': 100,
               'spark_version': 'test', 'cases': [{'id': 'x', 'status': 'ok', 'rows': [],
                                                  'schema': {}, 'oracle_result': 'fail'}]}
        report = compare(run, run)
        self.assertEqual(report['changed'], 0)
        self.assertEqual(report['cases'][0]['interpretation'], 'correctness_failure')
