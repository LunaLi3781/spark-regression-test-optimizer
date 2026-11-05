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

    def scalar(self, sql):
        return self.spark.sql(sql).first()[0]
    def test_coalesce(self):
        self.assertEqual(self.scalar('SELECT coalesce(NULL, 7)'), 7)
    def test_null_safe_equality(self):
        self.assertTrue(self.scalar('SELECT NULL <=> NULL'))
    def test_decimal(self):
        self.assertEqual(str(self.scalar('SELECT CAST(1.25 AS DECIMAL(5,2)) + CAST(2.50 AS DECIMAL(5,2))')), '3.75')
    def test_array(self):
        self.assertEqual(self.scalar('SELECT array_sort(array(3,1,2))'), [1,2,3])
    def test_map(self):
        self.assertEqual(self.scalar("SELECT element_at(map('key', 9), 'key')"), 9)
    def test_explode(self):
        self.assertEqual([r[0] for r in self.spark.sql('SELECT explode(array(4,5))').collect()], [4,5])
    def test_json(self):
        self.assertEqual(self.scalar('SELECT from_json(\'{"n":7}\', \'n INT\').n'), 7)
    def test_date(self):
        self.assertEqual(str(self.scalar("SELECT date_add(DATE '2024-02-28', 1)")), '2024-02-29')
    def test_union_all(self):
        self.assertEqual(self.spark.sql('SELECT 1 UNION ALL SELECT 1').count(), 2)
    def test_left_join(self):
        self.assertEqual(self.scalar('SELECT count(*) FROM (SELECT 1 k) a LEFT JOIN (SELECT 2 k) b ON a.k=b.k WHERE b.k IS NULL'), 1)
    def test_empty_aggregate(self):
        self.assertIsNone(self.scalar('SELECT sum(id) FROM range(0)'))
    def test_try_cast(self):
        self.assertIsNone(self.scalar("SELECT try_cast('not-an-integer' AS INT)"))
