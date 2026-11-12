import copy
import unittest

from spark_compat.cases import HISTORICAL
from spark_compat.core import fingerprint
from spark_compat.oracles import check
from spark_compat.validation import DEFECTS, verify_historical


class OracleTests(unittest.TestCase):
    def test_json_rejects_nonstandard_constants_and_wrong_values(self):
        case = {'oracle': 'strict_json', 'expected_json': {'reading': '-Infinity'}}
        self.assertTrue(check(case, [['{"reading":"-Infinity"}']]))
        for value in ['{"reading":-Infinity}', '{"reading":NaN}', '{"reading":"Infinity"}']:
            self.assertFalse(check(case, [[value]]))

    def test_rows_detect_missing_totals_and_duplicates(self):
        case = {'oracle': 'rows', 'expected_rows': [['north', 10], [None, 15]]}
        self.assertTrue(check(case, [(None, 15), ('north', 10)]))
        self.assertFalse(check(case, [('north', 10)]))
        self.assertFalse(check(case, [(None, 15), ('north', 10), ('north', 10)]))

    def test_xml_rejects_wrong_payload(self):
        case = {'oracle': 'xml_payload'}
        self.assertTrue(check(case, [('<ROW><payload>compat-sample</payload></ROW>',)]))
        self.assertFalse(check(case, [('<ROW><payload>wrong</payload></ROW>',)]))

    def expected_run(self, version):
        rows = []
        for c in HISTORICAL:
            bad = version == '4.0.0' and c['id'] in DEFECTS
            rows.append({'id': c['id'], 'oracle_result': 'fail' if bad else 'pass',
                         'status': 'error' if bad and c['id'] == 'xml_binary_52788' else 'ok',
                         'error': 'SPARK-52788_BINARY_XML_CONVERSION'})
        return {'spark_version': version, 'case_fingerprint': fingerprint(HISTORICAL), 'cases': rows}

    def test_version_expectations_reject_wrong_output_even_when_execution_succeeds(self):
        for version in ['4.0.0', '4.0.1']:
            self.assertEqual(verify_historical(self.expected_run(version))['known_defects'], 3)
        run = self.expected_run('4.0.1')
        run['cases'][3]['oracle_result'] = 'fail'
        with self.assertRaises(ValueError):
            verify_historical(run)

    def test_expectations_reject_missing_control_and_unexpected_error(self):
        run = self.expected_run('4.0.0')
        missing = copy.deepcopy(run)
        missing['cases'].pop(0)
        with self.assertRaises(ValueError):
            verify_historical(missing)
        run['cases'][1]['error'] = 'UNRELATED_ERROR'
        with self.assertRaises(ValueError):
            verify_historical(run)
