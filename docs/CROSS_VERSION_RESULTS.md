# Spark 3.5.3 → 4.0.0 smoke comparison

Run: https://github.com/LunaLi3781/spark-regression-test-optimizer/actions/runs/41977105892

Python 3.11, Java 17, GitHub Ubuntu runners; three fresh JVM runs per version.

| Spark | Executions passed | Suite wall times (seconds) | Median |
|---|---:|---|---:|
| 3.5.3 | 24 / 24 | 9.02, 5.85, 5.80 | 5.85 |
| 4.0.0 | 24 / 24 | 11.46, 11.07, 10.82 | 11.07 |

All 48 test executions passed. No regression was observed in these eight small tests.
This does not establish general upgrade compatibility or optimizer effectiveness.
Separate hosted runners and startup/JIT effects prevent attributing timing differences to Spark alone.
All outcomes pass, so failing-test recall is undefined; these runs cannot demonstrate improved failure discovery.

Next: expand public SQL cases, include documented version-sensitive semantics, and reproduce a public historical regression before evaluating selection effectiveness.

Version requirements: https://spark.apache.org/docs/4.0.0/api/python/getting_started/install.html
