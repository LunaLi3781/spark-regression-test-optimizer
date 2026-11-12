"""Correctness checks derived from SQL semantics, independent of version labels."""
import json
import xml.etree.ElementTree as ET

from .core import canonical, dumps


def check(case, rows):
    kind = case['oracle']
    if kind == 'rows':
        return sorted([canonical(row) for row in rows], key=dumps) == sorted(
            case['expected_rows'], key=dumps)
    if kind == 'xml_payload':
        try:
            return len(rows) == 1 and ET.fromstring(rows[0][0]).findtext('payload') == 'compat-sample'
        except (ET.ParseError, TypeError, IndexError):
            return False
    if kind == 'strict_json':
        def reject_constant(value):
            raise ValueError('Non-JSON numeric constant: ' + value)
        try:
            return len(rows) == 1 and json.loads(
                rows[0][0], parse_constant=reject_constant) == case['expected_json']
        except (ValueError, TypeError, IndexError):
            return False
    raise ValueError('Unknown oracle: ' + kind)
