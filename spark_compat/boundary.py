"""Deterministic synthetic edge cases with independently computed expectations."""
from collections import defaultdict


def cube_expected(data, count_column, threshold):
    groups = defaultdict(list)
    for region, amount in data:
        groups[region].append((region, amount))
    rows = []
    for region, values, gid in [(k, v, 0) for k, v in groups.items()] + [(None, data, 1)]:
        count = sum(r is not None for r, _ in values) if count_column else len(values)
        if count > threshold:
            amounts = [a for _, a in values if a is not None]
            rows.append([region, sum(amounts) if amounts else None, gid])
    return rows


def build_cases():
    datasets = {
        'empty': [],
        'null_only': [(None, None), (None, 2)],
        'mixed': [('east', 3), (None, 5), ('east', None)],
        'duplicates': [('west', 4), ('west', 4), ('east', 1)],
        'cancellation': [('east', 7), ('east', -7), ('west', None)],
    }
    cases = []
    for name, data in datasets.items():
        if data:
            def literal(value):
                if value is None:
                    return 'NULL'
                return "'" + value + "'" if isinstance(value, str) else str(value)
            source = ('SELECT CAST(r AS STRING) AS region, CAST(a AS INT) AS amount FROM VALUES ' +
                      ','.join('(' + literal(r) + ',' + literal(a) + ')' for r, a in data) +
                      ' AS input(r,a)')
        else:
            source = 'SELECT CAST(NULL AS STRING) AS region, CAST(NULL AS INT) AS amount WHERE false'
        for count_column in (False, True):
            count = 'region' if count_column else '*'
            for threshold in (-1, 0):
                cases.append({
                    'id': f'cube_{name}_{"column" if count_column else "star"}_{threshold}',
                    'sql': 'SELECT region, SUM(amount) AS total, grouping(region) AS gid FROM (' +
                           source + ') src GROUP BY CUBE(region) HAVING count(' + count + ')>' +
                           str(threshold),
                    'oracle': 'rows', 'expected_rows': cube_expected(data, count_column, threshold),
                    'reference': 'https://github.com/apache/spark/pull/51820',
                })
    values = [('nan', "CAST('NaN' AS DOUBLE)", 'NaN'),
              ('positive_inf', "CAST('Infinity' AS DOUBLE)", 'Infinity'),
              ('negative_inf', "CAST('-Infinity' AS DOUBLE)", '-Infinity'),
              ('fraction', 'CAST(1.25 AS DOUBLE)', 1.25),
              ('negative_zero', 'CAST(-0.0 AS DOUBLE)', -0.0),
              ('null', 'CAST(NULL AS DOUBLE)', None)]
    for name, expr, value in values:
        for shape in ('object', 'array'):
            inner = "named_struct('reading', " + expr + ')' if shape == 'object' else 'array(' + expr + ')'
            cases.append({
                'id': f'json_{shape}_{name}',
                'sql': 'SELECT to_json(to_variant_object(' + inner + ')) AS value',
                'oracle': 'strict_json',
                'expected_json': {'reading': value} if shape == 'object' else [value],
                'reference': 'https://github.com/apache/spark/pull/50901',
            })
    return cases


BOUNDARY = build_cases()
