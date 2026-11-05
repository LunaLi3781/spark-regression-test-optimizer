"""Original public-API smoke tests, not copied from Apache Spark tests."""
import unittest
from pyspark.sql import SparkSession, functions as F, Window

class SparkSQLTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.master("local[2]").appName("spark-rto-smoke").config("spark.ui.enabled", "false").config("spark.sql.shuffle.partitions", "2").getOrCreate()

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    def test_filter(self):
        self.assertEqual(self.spark.range(5).filter("id > 2").count(), 2)
    def test_aggregate(self):
        self.assertEqual(self.spark.range(5).agg(F.sum("id")).first()[0], 10)
    def test_join(self):
        self.assertEqual(self.spark.range(3).join(self.spark.range(1, 4), "id").count(), 2)
    def test_null(self):
        self.assertEqual(self.spark.createDataFrame([(1,), (None,)], "v int").filter("v IS NULL").count(), 1)
    def test_sort(self):
        self.assertEqual([r.id for r in self.spark.range(3).orderBy(F.desc("id")).collect()], [2, 1, 0])
    def test_distinct(self):
        self.assertEqual(self.spark.createDataFrame([(1,), (1,), (2,)], "v int").distinct().count(), 2)
    def test_cast(self):
        self.assertEqual(self.spark.sql("SELECT CAST('42' AS INT)").first()[0], 42)
    def test_window(self):
        rows = self.spark.range(3).withColumn("n", F.row_number().over(Window.orderBy("id"))).collect()
        self.assertEqual([r.n for r in rows], [1, 2, 3])
