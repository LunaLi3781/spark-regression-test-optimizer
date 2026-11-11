# Initial Spark compatibility results

Local validation on 2026-11-11: Spark 3.5.3 and 4.0.1, Python 3.9.6, Java 17,
same macOS host, isolated environments and separate JVM processes. Four runs,
20 cases each (80 query observations). UTC Spark session timezone; identical host timezone.

| Profile | Compared cases | Differences |
|---|---:|---:|
| Installed defaults | 20 | 3 |
| ANSI disabled on both versions | 20 | 0 |

Default-profile differences:

| Case | Spark 3.5.3 | Spark 4.0.1 |
|---|---|---|
| invalid_cast | [[null]] | CAST_INVALID_INPUT |
| divide_zero | [[null]] | DIVIDE_BY_ZERO |
| overflow | [[-2147483648]] | ARITHMETIC_OVERFLOW |

These are documented ANSI-default effects, not new defect discoveries.
No observed differences in the controlled profile do not prove general compatibility.
The missing-column probe fails identically on both versions; zero differences does
not mean every query succeeds.

[Raw evidence](validation/compatibility/) includes all four runs and both comparisons.
[Cloud reproduction](https://github.com/LunaLi3781/spark-regression-test-optimizer/actions/runs/43097643024)
was queued when this local report was recorded; no cloud pass is claimed.

All 41 unit tests passed. Queries and implementation are original and AI-assisted.
Future comparisons across different hosts must control their local timezone as well
as Spark timezone: collected timestamp values use Python datetime representation.
