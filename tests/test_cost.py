import unittest
from unittest.mock import Mock, patch
from spark_rto.cost import reserve_budget
from scripts.spark_timing import start_session, stop_session, PHASES
from defects.xml_binary import test_xml_binary as oracle

class CostTests(unittest.TestCase):
    def test_reserve_uses_only_historical_overhead(self):
        history=[dict(process_wall_s=10,tests=[dict(duration_s=3)]), dict(process_wall_s=12,tests=[dict(duration_s=3)])]
        self.assertEqual(reserve_budget(history,12,'wall'),(4,8))
        self.assertEqual(reserve_budget(history,2,'wall'),(0,8))
        self.assertEqual(reserve_budget(history,2,'test'),(2,8))
    def test_invalid_budget(self):
        for value in (-1,float('nan'),float('inf')):
            with self.assertRaises(ValueError): reserve_budget([],value,'wall')
    def test_fixture_phases(self):
        builder=Mock();spark=builder.getOrCreate.return_value
        for k in PHASES: PHASES[k]=0
        with patch('scripts.spark_timing.time.perf_counter',side_effect=[0,2,2,5,5,6]):
            self.assertIs(start_session(builder),spark)
            stop_session(spark)
        self.assertEqual(PHASES,dict(spark_startup_s=2,warmup_s=3,cleanup_s=1))
    def test_warmup_failure_closes_session(self):
        builder=Mock();spark=builder.getOrCreate.return_value
        spark.range.side_effect=RuntimeError('warmup failed')
        with self.assertRaises(RuntimeError): start_session(builder)
        spark.stop.assert_called_once()
    def test_known_defect_is_failure_not_pass(self):
        self.spark=Mock()
        self.spark.sql.return_value.first.return_value=['<ROW><payload>sample-52788</payload></ROW>']
        self.spark.sql.side_effect=[self.spark.sql.return_value, RuntimeError('Failed to convert value x BinaryType')]
        with self.assertRaises(AssertionError): oracle(self)
        self.spark.conf.set.assert_called_with('spark.sql.binaryOutputStyle', self.spark.conf.get.return_value)
    def test_other_error_is_not_labeled_defect(self):
        self.spark=Mock()
        control=Mock();control.first.return_value=['<ROW><payload>sample-52788</payload></ROW>']
        self.spark.sql.side_effect=[control,RuntimeError('connection lost')]
        with self.assertRaises(RuntimeError): oracle(self)
    def test_correct_xml_passes(self):
        self.spark=Mock()
        self.spark.sql.return_value.first.return_value=['<ROW><payload>sample-52788</payload></ROW>']
        oracle(self)

    def test_unset_config_restored_without_null_assignment(self):
        self.spark=Mock()
        self.spark.conf.get.return_value=None
        self.spark.sql.return_value.first.return_value=['<ROW><payload>sample-52788</payload></ROW>']
        oracle(self)
        self.spark.conf.unset.assert_called_once_with('spark.sql.binaryOutputStyle')
        self.spark.conf.set.assert_called_once_with('spark.sql.binaryOutputStyle', 'UTF-8')
