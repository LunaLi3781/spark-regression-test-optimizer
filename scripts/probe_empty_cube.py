"""Original minimal SQL reproducer; records observations, not a claimed new bug."""
import argparse
import json
import os
import platform
from pathlib import Path

EMPTY = '(SELECT CAST(NULL AS STRING) AS region, CAST(NULL AS INT) AS amount WHERE false) src'
QUERIES = {
    'global_control': 'SELECT CAST(NULL AS STRING) AS region, SUM(amount) AS total, 1 AS gid FROM ' + EMPTY,
    'keyed_control': 'SELECT region, SUM(amount) AS total, 0 AS gid FROM ' + EMPTY + ' GROUP BY region',
    'cube': 'SELECT region, SUM(amount) AS total, grouping(region) AS gid FROM ' + EMPTY + ' GROUP BY CUBE(region)',
    'cube_having': 'SELECT region, SUM(amount) AS total, grouping(region) AS gid FROM ' + EMPTY + ' GROUP BY CUBE(region) HAVING count(*) > -1',
    'grouping_sets': 'SELECT region, SUM(amount) AS total, grouping(region) AS gid FROM ' + EMPTY + ' GROUP BY GROUPING SETS ((region), ())',
    'rollup': 'SELECT region, SUM(amount) AS total, grouping(region) AS gid FROM ' + EMPTY + ' GROUP BY ROLLUP(region)',
    'single_empty_set': 'SELECT SUM(amount) AS total FROM ' + EMPTY + ' GROUP BY GROUPING SETS (())',
    'nonempty_control': "SELECT region, SUM(amount) AS total, grouping(region) AS gid FROM VALUES ('east', 7) AS src(region,amount) GROUP BY CUBE(region)",
}


def assess(observations):
    if set(observations) != set(QUERIES):
        raise ValueError('Incomplete reproducer observations')
    expected = [[None, None, 1]]
    checks = {
        'global_control': observations['global_control']['rows'] == expected,
        'keyed_control': observations['keyed_control']['rows'] == [],
        'nonempty_control': sorted(observations['nonempty_control']['rows'], key=repr) ==
                            sorted([['east', 7, 0], [None, 7, 1]], key=repr),
    }
    if not all(checks.values()):
        raise ValueError('Control failed; cannot interpret candidate: ' + str(checks))
    return {'controls': checks, 'mismatches': [k for k in
            ('cube', 'cube_having', 'grouping_sets', 'rollup')
            if observations[k]['rows'] != expected],
            'note': 'Observed against a global-aggregate control; novelty is unestablished.'}


def main():
    from pyspark.sql import SparkSession
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    spark = (SparkSession.builder.master('local[2]').appName('empty-cube-probe')
             .config('spark.ui.enabled', 'false').config('spark.sql.shuffle.partitions', '2')
             .getOrCreate())
    spark.sparkContext.setLogLevel('ERROR')
    try:
        observations = {}
        for key, sql in QUERIES.items():
            frame = spark.sql(sql)
            observations[key] = {'sql': sql, 'rows': [list(r) for r in frame.collect()],
                                 'optimized_plan': frame._jdf.queryExecution().optimizedPlan().toString()}
        report = {'spark_version': spark.version, 'source_sha': os.environ.get('SPARK_SOURCE_SHA'),
                  'python': platform.python_version(),
                  'java': spark.sparkContext._jvm.java.lang.System.getProperty('java.version'),
                  'observations': observations, 'assessment': assess(observations)}
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report['assessment']))
    finally:
        spark.stop()


if __name__ == '__main__':
    main()
