import copy
import unittest
from spark_rto.history import aggregate, evaluate

def report():
    return dict(run_id='a', started_at='2026-01-01T00:00:00+00:00', finished_at='2026-01-01T00:01:00+00:00',
        data_kind='measured', errors=0, spark_version='3.5.3', python='3.11', platform='test',
        selected_ids=None, total_wall_s=5,
        tests=[dict(id='a', duration_s=2, outcome='pass'), dict(id='b', duration_s=4, outcome='fail')])

class HistoryTests(unittest.TestCase):
    def test_median_and_counts(self):
        a,b=report(),report();b['run_id']='b';b['tests'][0]['duration_s']=4
        cases=aggregate([a,b], '2026-01-02T00:00:00+00:00')
        self.assertEqual(cases[0].duration_s,3)
        self.assertEqual(cases[1].failures,2)
    def test_future_leakage_and_naive_times(self):
        for cutoff in ('2026-01-01T00:01:00+00:00','2025-01-01T00:00:00+00:00','2026-01-02T00:00:00'):
            with self.assertRaises(ValueError): aggregate([report()],cutoff)
    def test_duplicate_runs_and_mixed_environment(self):
        a,b=report(),report()
        with self.assertRaises(ValueError): aggregate([a,b],'2026-01-02T00:00:00+00:00')
        b.update(run_id='b',spark_version='4.0.0')
        with self.assertRaises(ValueError): aggregate([a,b],'2026-01-02T00:00:00+00:00')
    def test_excludes_skips(self):
        a,b=report(),report();b['run_id']='b';b['tests'][1]['outcome']='skip'
        self.assertEqual(aggregate([a,b],'2026-01-02T00:00:00+00:00')[1].runs,1)
    def test_rejects_invalid_history(self):
        for update in ({'errors':1},{'selected_ids':['a']},{'tests':[]},{'data_kind':'synthetic'}):
            a=report();a.update(update)
            with self.assertRaises(ValueError): aggregate([a],'2026-01-02T00:00:00+00:00')
    def evaluation(self):
        full=report();selected=copy.deepcopy(full)
        selected.update(run_id='selected',selected_ids=['a'],tests=selected['tests'][:1])
        plan=dict(candidate_ids=['a','b'],selected_ids=['a'],budget_s=2,estimated_test_s=2)
        return selected,full,plan
    def test_missed_failure_and_wall_overrun(self):
        value=evaluate(*self.evaluation())
        self.assertEqual(value['missed_reference_failures'],['b'])
        self.assertEqual(value['failing_test_recall'],0)
        self.assertEqual(value['wall_budget_overrun_s'],3)
    def test_no_failure_recall_undefined(self):
        a,b,p=self.evaluation();b['tests'][1]['outcome']='pass'
        self.assertIsNone(evaluate(a,b,p)['failing_test_recall'])
    def test_disagreement_and_inventory(self):
        a,b,p=self.evaluation();a['tests'][0]['outcome']='fail'
        self.assertEqual(evaluate(a,b,p)['outcome_disagreements'],['a'])
        p['selected_ids']=['b']
        with self.assertRaises(ValueError): evaluate(a,b,p)
