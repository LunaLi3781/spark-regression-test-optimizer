import io
import unittest
from scripts.collect_spark import RecordingResult

class CollectorTests(unittest.TestCase):
    def run_suite(self, case):
        return unittest.TextTestRunner(stream=io.StringIO(), resultclass=RecordingResult).run(unittest.defaultTestLoader.loadTestsFromTestCase(case))

    def test_records_pass_failure_error_and_skip(self):
        class Sample(unittest.TestCase):
            def test_pass(self): pass
            def test_fail(self): self.fail('synthetic assertion')
            def test_error(self): raise RuntimeError('synthetic error')
            @unittest.skip('synthetic skip')
            def test_skip(self): pass
        result = self.run_suite(Sample)
        self.assertEqual({r['outcome'] for r in result.records}, {'pass', 'fail', 'error', 'skip'})
        self.assertEqual(len(result.records), 4)
        self.assertTrue(all(r['duration_s'] >= 0 for r in result.records))
        self.assertFalse(result.wasSuccessful())

    def test_class_setup_error_not_silently_successful(self):
        class Broken(unittest.TestCase):
            @classmethod
            def setUpClass(cls): raise RuntimeError('no JVM')
            def test_never(self): pass
        result = self.run_suite(Broken)
        self.assertEqual(result.records, [])
        self.assertEqual(len(result.errors), 1)
        self.assertFalse(result.wasSuccessful())

    def test_success(self):
        class Good(unittest.TestCase):
            def test_ok(self): pass
        result = self.run_suite(Good)
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(result.records[0]['outcome'], 'pass')
