import json
import random
import subprocess
import sys
import unittest
from spark_rto import TestCase as Case, select, STRATEGIES

class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.tests = [Case("a", 6, 10, 9, 0), Case("b", 2, 10, 3, 1), Case("c", 1, 10, 0, .2)]

    def test_expected_rankings(self):
        expected = {"failure": ["a", "b", "c"], "cheapest": ["c", "b", "a"],
                    "change": ["b", "c", "a"], "budget": ["b", "a", "c"]}
        for strategy, ids in expected.items():
            self.assertEqual([t.id for t in select(self.tests, 9, strategy)], ids)

    def test_skip_expensive_and_continue(self):
        self.assertEqual([t.id for t in select(self.tests, 3, "failure")], ["b", "c"])

    def test_fractional_boundary(self):
        self.assertEqual(len(select([Case("a", .1), Case("b", .2)], .3)), 2)

    def test_zero_empty_and_too_small(self):
        for strategy in STRATEGIES:
            self.assertEqual(select(self.tests, 0, strategy), [])
            self.assertEqual(select([], 10, strategy), [])
            self.assertEqual(select(self.tests, .5, strategy), [])

    def test_invalid_budgets(self):
        for value in (-1, float("nan"), float("inf"), True, "5"):
            with self.assertRaises(ValueError): select(self.tests, value)

    def test_invalid_features(self):
        for kwargs in (dict(duration_s=0), dict(duration_s=-1), dict(duration_s=float("nan")),
                       dict(change_score=2), dict(failures=1), dict(runs=-1), dict(runs=True), dict(id="")):
            values = dict(id="x", duration_s=1); values.update(kwargs)
            with self.assertRaises(ValueError): Case(**values)

    def test_duplicate_and_unknown(self):
        with self.assertRaises(ValueError): select([self.tests[0]] * 2, 10)
        with self.assertRaises(ValueError): select(self.tests, 10, "optimal")

    def test_cold_start(self):
        self.assertEqual(Case("new", 1).risk, .5)

    def test_reproducible_order_without_global_rng_mutation(self):
        state = random.getstate()
        a = select(self.tests, 9, "random", 42)
        self.assertEqual(a, select(list(reversed(self.tests)), 9, "random", 42))
        self.assertEqual(random.getstate(), state)

    def test_budget_invariants(self):
        rng = random.Random(3)
        cases = [Case(str(i), rng.randint(1, 100), 10, rng.randint(0, 10), rng.random()) for i in range(100)]
        original = list(cases)
        for budget in (0, 1, 15, 100, 1000, 10000):
            for strategy in STRATEGIES:
                picked = select(cases, budget, strategy)
                self.assertLessEqual(sum(t.duration_s for t in picked), budget)
                self.assertEqual(len(picked), len(set(t.id for t in picked)))
                self.assertTrue(set(picked) <= set(cases))
        self.assertEqual(cases, original)

    def test_cli_and_heldout_evaluation(self):
        result = subprocess.run([sys.executable, "-m", "spark_rto", "examples/history.json", "--budget", "10", "--outcomes", "examples/outcomes.json"], capture_output=True, text=True, check=True)
        report = json.loads(result.stdout)
        self.assertLessEqual(report["estimated_duration_s"], 10)
        self.assertEqual(report["failing_tests_total"], 3)

    def test_cli_invalid_input(self):
        result = subprocess.run([sys.executable, "-m", "spark_rto", "examples/history.json", "--budget", "nan"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)

if __name__ == "__main__": unittest.main()
