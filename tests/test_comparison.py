import unittest
from spark_rto import TestCase as Case
from spark_rto.comparison import build_plans, schedule

class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.features=[Case('a',1,2,0),Case('b',2,2,2),Case('c',.5,2,0)]
    def test_shared_features_and_equal_budgets(self):
        plans=build_plans(self.features)
        self.assertEqual(len(plans),14)
        self.assertEqual(len({p['feature_sha256'] for p in plans}),1)
        for budget in (1,2):
            subset=[p for p in plans if p['budget_s']==budget]
            self.assertEqual({p['strategy'] for p in subset},{'random','failure','cheapest','change','budget'})
            self.assertEqual(len([p for p in subset if p['strategy']=='random']),3)
            self.assertTrue(all(p['estimated_test_s']<=budget for p in subset))
    def test_reproducible_plans_and_schedule(self):
        plans=build_plans(self.features)
        self.assertEqual(plans,build_plans(list(reversed(self.features))))
        self.assertEqual(schedule(plans,0),list(reversed(schedule(plans,1))))
        self.assertEqual({p['id'] for p in plans},{p['id'] for p in schedule(plans,0)})
    def test_digest_changes_with_history(self):
        first=build_plans(self.features)[0]['feature_sha256']
        self.assertNotEqual(first,build_plans([Case('a',2)])[0]['feature_sha256'])
    def test_invalid_configuration(self):
        for budgets,seeds in (([],[0]),([1,1],[0]),([1],[]),([1],[0,0]),([-1],[0])):
            with self.assertRaises(ValueError): build_plans(self.features,budgets,seeds)
