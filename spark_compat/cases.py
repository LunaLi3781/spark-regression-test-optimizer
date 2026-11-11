"""Original synthetic queries; no employer data or upstream test code."""
GUIDE = "https://spark.apache.org/docs/4.0.1/sql-migration-guide.html"
QUERIES = [
    ("integer", "SELECT 7 + 5 AS value"),
    ("decimal", "SELECT CAST(1.25 AS DECIMAL(8,2)) AS value"),
    ("null", "SELECT CAST(NULL AS INT) AS value"),
    ("duplicates", "SELECT id % 2 AS value FROM range(6)"),
    ("aggregate", "SELECT sum(id) AS value FROM range(10)"),
    ("array", "SELECT array(1, NULL, 3) AS value"),
    ("map", "SELECT map('b', 2, 'a', 1) AS value"),
    ("struct", "SELECT named_struct('x', 1, 'y', 'hello') AS value"),
    ("date", "SELECT DATE '2024-02-29' AS value"),
    ("timestamp", "SELECT TIMESTAMP '2024-01-02 03:04:05' AS value"),
    ("binary", "SELECT unhex('00FF') AS value"),
    ("unicode", "SELECT concat('Spark', '测试') AS value"),
    ("nan", "SELECT CAST('NaN' AS DOUBLE) AS value"),
    ("window", "SELECT id, row_number() OVER (ORDER BY id) AS n FROM range(3)"),
    ("join", "SELECT a.id FROM range(3) a JOIN range(2) b ON a.id=b.id"),
    ("quoted_name", "SELECT 2 AS `a.b`, 3 AS `a``b`"),
    ("invalid_cast", "SELECT CAST('not-an-integer' AS INT) AS value"),
    ("divide_zero", "SELECT 1 / 0 AS value"),
    ("overflow", "SELECT CAST(2147483647 AS INT) + 1 AS value"),
    ("missing_column", "SELECT missing_column FROM range(1)"),
]
CASES = [{"id": key, "sql": sql, "reference": GUIDE if key in
          {"invalid_cast", "divide_zero", "overflow"} else None}
         for key, sql in QUERIES]
