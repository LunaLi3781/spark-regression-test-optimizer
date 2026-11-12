"""Known-version acceptance criteria kept separate from the collector."""
from .cases import HISTORICAL
from .core import fingerprint

DEFECTS = {
    'xml_binary_52788': 'SPARK-52788',
    'json_variant_52153': 'SPARK-52153',
    'cube_having_53094': 'SPARK-53094',
}


def verify_historical(run):
    version = run['spark_version']
    if version not in ('4.0.0', '4.0.1'):
        raise ValueError('No historical expectations for version ' + version)
    if run.get('case_fingerprint') != fingerprint(HISTORICAL):
        raise ValueError('Historical suite does not match current definitions')
    cases = {c['id']: c for c in run['cases']}
    if len(cases) != len(run['cases']) or set(cases) != {c['id'] for c in HISTORICAL}:
        raise ValueError('Historical observations are incomplete or duplicated')
    for key, case in cases.items():
        expected = 'fail' if version == '4.0.0' and key in DEFECTS else 'pass'
        if case.get('oracle_result') != expected:
            raise ValueError('Unexpected correctness result for ' + key)
        expected_status = 'error' if version == '4.0.0' and key == 'xml_binary_52788' else 'ok'
        if case['status'] != expected_status:
            raise ValueError('Unexpected execution status for ' + key)
    if version == '4.0.0' and cases['xml_binary_52788']['error'] != 'SPARK-52788_BINARY_XML_CONVERSION':
        raise ValueError('Unexpected XML error')
    return {'version': version, 'cases': len(cases), 'known_defects': len(DEFECTS)}
