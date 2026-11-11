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
