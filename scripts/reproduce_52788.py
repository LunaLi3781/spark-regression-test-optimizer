"""Independent reproduction from the public SPARK-52788 bug description.
Not copied from upstream test code. Version expectation is separate from outcome.
"""
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from pyspark.sql import SparkSession

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    spark = SparkSession.builder.master('local[2]').appName('SPARK-52788-reproduction').config('spark.ui.enabled', 'false').getOrCreate()
    try:
        spark.conf.set('spark.sql.binaryOutputStyle', 'UTF-8')
        control = spark.sql("SELECT to_xml(named_struct('payload', 'sample-52788'))").first()[0]
        assert ET.fromstring(control).findtext('payload') == 'sample-52788'
        report = dict(issue='SPARK-52788', spark_version=spark.version, control_passed=True)
        try:
            value = spark.sql("SELECT to_xml(named_struct('payload', CAST('sample-52788' AS BINARY)))").first()[0]
        except Exception as error:
            message = str(error)
            if 'Failed to convert value' not in message or 'BinaryType' not in message:
                raise
            report.update(observed='known_binary_xml_error', error=message)
        else:
            assert ET.fromstring(value).findtext('payload') == 'sample-52788', value
            report.update(observed='correct_xml', xml=value)
        expected = {'4.0.0': 'known_binary_xml_error', '4.0.1': 'correct_xml'}
        report['matches_expectation'] = report['observed'] == expected.get(spark.version)
        target = Path(args.output); target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report, indent=2)+'\n')
        if not report['matches_expectation']:
            raise AssertionError('Unexpected version or behavior: '+str(report))
    finally:
        spark.stop()

if __name__ == '__main__': main()
