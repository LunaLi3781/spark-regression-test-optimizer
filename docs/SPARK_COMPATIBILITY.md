# Spark upgrade compatibility diagnostics

`spark-compat` is a new independent tool in this repository. It compares observed
SQL behavior across isolated Spark processes, complementing test selection.
The smoke corpus contains 20 original synthetic, read-only SQL queries.
The optional historical corpus contains two XML probes for SPARK-52788.
No employer code or data is used. The existing MIT license applies.

## Run

Install this repository plus `pyspark==3.5.3` in one Python environment and
`pyspark==4.0.1` in another. Use Python 3.11 / Java 17 for the initial pair.
Run each collector in its own process/environment:

```sh
spark-compat collect --output results/3.5.3-defaults.json
# In the 4.0.1 environment:
spark-compat collect --output results/4.0.1-defaults.json
spark-compat compare results/3.5.3-defaults.json results/4.0.1-defaults.json --output results/diff.json
```

Repeat both collectors with `--profile ansi-off`, then compare those two outputs.
The controlled pair helps distinguish ANSI-default effects from other differences.
The defaults profile preserves installed defaults (and any external overrides);
effective ANSI setting and timezone are recorded, not assumed. UTC is pinned.
The workflow `Spark upgrade compatibility` reproduces both pairs on GitHub Actions.

## Interpretation

The report distinguishes outcome (success/error), structured error condition,
exact schema (including nullability), and result multiset differences. Row order
is ignored; duplicates are retained. Arrays retain order and maps ignore key order.
Decimals, binary, dates, timestamps and nonfinite floats use explicit encodings.
Floating comparisons are exact, not approximate. A bounded collection that exceeds
1,000 rows is inconclusive, never silently equal. Unclassified failures stop the
collector rather than appearing as a SQL compatibility observation.

A changed case is **needs_review**, not automatically a regression or new bug.
An unchanged error is also not a successful SQL execution; inspect the source
artifacts. Error text/parameters are not compared, and may still change.
A suite fingerprint prevents comparisons of different query definitions.
This MVP accepts only bundled cases; it does not run arbitrary customer SQL,
benchmark performance, test connectors, or prove whole-workload compatibility.

## Public reference and next evidence

[Apache's 4.0.1 SQL migration guide](https://spark.apache.org/docs/4.0.1/sql-migration-guide.html)
documents the ANSI default change. The invalid-cast, divide-by-zero and overflow
probes exercise that boundary; they are not claims of newly discovered bugs.
Queries and implementation are original and AI-assisted. Retrieved 2026-11-11.

Next: expand public historical defect coverage,
validate with an independent user's reproducible workload, and minimize any
unexplained differences before proposing upstream issues. No adoption or
algorithm-superiority claim is made.

## First measured results

See [80 local query observations](COMPATIBILITY_RESULTS.md): three default-profile
differences, zero differences after disabling ANSI on both versions.

## Historical defect mode and readable reports

```sh
# Run in each isolated Spark 4.0.0 / 4.0.1 environment:
spark-compat collect --suite historical --output results/4.0.0-historical.json
# Change the output filename to 4.0.1-historical.json in the fixed environment.
spark-compat compare results/4.0.0-historical.json results/4.0.1-historical.json --output results/history.json --markdown results/history.md
```

The string XML control must be correct on both versions. The binary XML probe
must match the specific known conversion error on 4.0.0; 4.0.1 must return valid
XML with the expected payload. Version expectations are checked separately by CI,
not used to manufacture observations. Unexpected unclassified exceptions abort.
This is independent reproduction of an existing fix, not new discovery credit.

[Measured historical report](validation/compatibility-historical/historical.md):
4.0.0 binary probe fails; 4.0.1 passes; both string controls pass.
Original upstream fix: [SPARK-52788 / PR 51610](https://github.com/apache/spark/pull/51610).

New collections use format 2: expected case IDs and suite fingerprint are checked,
empty/incomplete runs are rejected, both Python and Spark timezones are UTC, and
the ANSI-off profile is verified before comparison. The collector currently
requires a Unix host with `time.tzset`. Existing format-1 artifacts can still be
compared to each other, but retain their historical metadata limitations; formats
1 and 2 cannot be mixed. Markdown reports expose unchanged errors as errors,
not successful queries. Floating point results remain exact comparisons.
