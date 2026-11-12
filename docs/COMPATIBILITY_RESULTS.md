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
did not start any jobs and ended with startup_failure. A retry was requested;
no cloud pass is claimed.

All 41 unit tests passed. Queries and implementation are original and AI-assisted.
Future comparisons across different hosts must control their local timezone as well
as Spark timezone: collected timestamp values use Python datetime representation.


## Historical defect validation

Two new local JVM runs (4.0.0 and 4.0.1, Python 3.9 / Java 17) each executed a string
control and binary XML probe. Both controls passed. The binary probe reproduced
SPARK-52788 on 4.0.0 and returned the correct XML on 4.0.1.
[Generated report and raw evidence](validation/compatibility-historical/historical.md).
This demonstrates detection of one known repair, not broad defect recall or a
newly discovered vulnerability. 44 unit tests pass after report/integrity updates.


## Cloud confirmation and corpus expansion (2026-11-11)

[Run 43098909667](https://github.com/LunaLi3781/spark-regression-test-optimizer/actions/runs/43098909667)
completed successfully: Spark 3.5.3, 4.0.0 and 4.0.1 collectors plus the comparison
job all passed. This run validates the previous two-probe XML historical suite,
not the later six-probe expansion. Its default-profile comparison found 3
changes; ANSI-off found 0; XML historical comparison found 1.

The expanded six-probe suite has now passed local known-version validation on
4.0.0 and 4.0.1 (12 observations). All three defective probes fail their correctness
checks on 4.0.0 and pass on 4.0.1. All three controls pass on both versions.
[Expanded report and raw artifacts](validation/compatibility-three-defects/report.md).
The original four-run smoke evidence and earlier XML reports remain unchanged.
