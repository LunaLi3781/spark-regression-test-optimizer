import copy
import decimal
import unittest

from spark_compat.core import canonical, compare, dumps


class CompatibilityTests(unittest.TestCase):
    def run_data(self):
        return {"format": 1, "case_fingerprint": "same", "profile": "defaults",
                "row_limit": 1000, "spark_version": "test", "cases": [
                    {"id": "x", "status": "ok", "schema": {"type": "int"}, "rows": [[1], [1]]}]}

    def test_duplicates_preserved(self):
        left = self.run_data()
        right = copy.deepcopy(left)
        right["cases"][0]["rows"].pop()
        self.assertEqual(compare(left, right)["cases"][0]["changes"], ["rows"])

    def test_typed_values_and_map_order(self):
        self.assertNotEqual(canonical(decimal.Decimal("1.0")), "1.0")
        self.assertEqual(canonical({"a": 1, "b": 2}), canonical({"b": 2, "a": 1}))
        self.assertEqual(dumps(canonical(float("nan"))), '{"float": "nan"}')
        self.assertNotEqual(canonical(b"01"), "3031")

    def test_schema_difference(self):
        left = self.run_data()
        right = copy.deepcopy(left)
        right["cases"][0]["schema"] = {"type": "long"}
        self.assertEqual(compare(left, right)["cases"][0]["changes"], ["schema"])

    def test_error_and_outcome(self):
        left = self.run_data()
        right = copy.deepcopy(left)
        right["cases"][0] = {"id": "x", "status": "error", "error": "DIVIDE_BY_ZERO"}
        self.assertEqual(compare(left, right)["cases"][0]["changes"], ["outcome"])
        self.assertEqual(compare(right, right)["changed"], 0)

    def test_refuse_incompatible_or_missing_results(self):
        left = self.run_data()
        for field, value in [("profile", "ansi-off"), ("case_fingerprint", "other"),
                             ("row_limit", 3), ("cases", [])]:
            right = copy.deepcopy(left)
            right[field] = value
            with self.assertRaises(ValueError):
                compare(left, right)

    def test_truncation_is_not_equality(self):
        left = self.run_data()
        left["cases"][0] = {"id": "x", "status": "inconclusive"}
        self.assertEqual(compare(left, left)["cases"][0]["changes"], ["inconclusive"])

    def test_reject_invalid_or_empty_observations(self):
        for cases in ([], [{"id": "x", "status": "unknown"}]):
            run = self.run_data()
            run['cases'] = cases
            with self.assertRaises(ValueError):
                compare(run, run)

    def test_v2_rejects_jointly_missing_cases_and_timezone_mismatch(self):
        left = self.run_data()
        left.update(format=2, suite='smoke', host_timezone='UTC',
                    expected_case_ids=['x', 'missing'], config={
                        'spark.sql.session.timeZone': 'UTC', 'spark.sql.ansi.enabled': 'false'})
        with self.assertRaises(ValueError):
            compare(left, left)
        left['expected_case_ids'] = ['x']
        right = copy.deepcopy(left)
        right['host_timezone'] = 'America/Los_Angeles'
        with self.assertRaises(ValueError):
            compare(left, right)
        left['profile'] = 'ansi-off'
        left['config']['spark.sql.ansi.enabled'] = 'true'
        with self.assertRaises(ValueError):
            compare(left, left)

    def test_report_exposes_unchanged_errors(self):
        from spark_compat.core import markdown
        left = self.run_data()
        left['cases'] = [{'id': 'x', 'status': 'error', 'error': 'KNOWN', 'oracle_result': 'fail'}]
        report = markdown(compare(left, left))
        self.assertIn('error → error', report)
        self.assertIn('fail → fail', report)
