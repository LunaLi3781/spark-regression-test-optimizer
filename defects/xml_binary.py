import xml.etree.ElementTree as ET

def test_xml_binary(self):
    """SPARK-52788 correctness oracle: known error is a failure, never a pass."""
    previous = self.spark.conf.get('spark.sql.binaryOutputStyle')
    try:
        self.spark.conf.set('spark.sql.binaryOutputStyle', 'UTF-8')
        control = self.spark.sql("SELECT to_xml(named_struct('payload', 'sample-52788'))").first()[0]
        self.assertEqual(ET.fromstring(control).findtext('payload'), 'sample-52788')
        try:
            value = self.spark.sql("SELECT to_xml(named_struct('payload', CAST('sample-52788' AS BINARY)))").first()[0]
        except Exception as error:
            if 'Failed to convert value' in str(error) and 'BinaryType' in str(error):
                self.fail('SPARK-52788: binary XML serialization failed')
            raise
        self.assertEqual(ET.fromstring(value).findtext('payload'), 'sample-52788')
    finally:
        self.spark.conf.set('spark.sql.binaryOutputStyle', previous)
