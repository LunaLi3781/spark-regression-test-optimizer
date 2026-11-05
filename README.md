# spark-regression-test-optimizer

An independent, runnable research MVP for **cost-aware regression test selection
for Apache Spark upgrades**. Not an Apache Software Foundation project or an
Amazon/Oracle product. MIT licensed. Python 3.9+; core has no runtime dependencies.

Local verification: **15 baseline tests + 8 real PySpark 3.5.3 smoke tests passed**.
See [validation details](docs/VALIDATION.md). This is not an upgrade benchmark.

## Quick start

From this repository directory:

```bash
python3 -m unittest discover -s tests -v
python3 -m spark_rto examples/history.json --budget 10 --strategy budget --outcomes examples/outcomes.json
python3 -m scripts.evaluate_demo
```

Optional installation (also installs the `spark-rto` command):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
spark-rto examples/history.json --budget 10
```

## What is implemented

| Strategy | Ordering before budget filtering |
| --- | --- |
| random | Seeded shuffle of ID-sorted candidates |
| failure | Decreasing smoothed historical failure probability |
| cheapest | Increasing estimated duration |
| change | Decreasing user-provided change relevance |
| budget | Decreasing `risk * (1 + change_score) / duration_s` |

`risk = (failures + 1) / (runs + 2)`. This explicit Laplace prior gives new tests
risk 0.5. Non-random ties use test ID. Every strategy skips tests that cannot fit
and continues scanning. Budget comparisons use decimal representations to avoid
0.1 + 0.2 boundary errors. The budget strategy is a **greedy heuristic**, not an
optimal knapsack solver or a demonstrated research novelty.

## Input and output

`examples/history.json` is a JSON array with unique `id`, positive finite
`duration_s`, integer `runs` and `failures` (`0 <= failures <= runs`), and a
`change_score` between 0 and 1. The last three fields default to 0. Unknown
fields and invalid records are rejected. Change relevance is supplied manually;
this MVP does not infer coverage or parse a Spark git diff.

The CLI emits ordered selected IDs, estimated serial cost, budget and seed.
Optional held-out outcomes must map every candidate ID to `pass` or `fail`.
They are never used for selection. Recall is the fraction of **failing tests**
selected, not unique bugs discovered; it is null if no test fails.

All files in `examples/` are **hand-authored synthetic data**. The demo compares
four budgets, five strategies, and ten random seeds (56 rows). It does not prove
performance improvements on Spark or report APFD/APFDc.

## Real Spark smoke tests

Twenty original public-API tests cover joins, aggregates, nulls, sorting, filters,
casts, distinct and windows. They are small correctness smoke tests, not the
Apache Spark regression suite. Install Java 17 and use an isolated Python 3.11
environment for the initial pinned reproducibility target (not a latest-version recommendation):

```bash
python3.11 -m venv .venv-spark
source .venv-spark/bin/activate
python -m pip install pyspark==3.5.3
python -m scripts.collect_spark --output results/spark-3.5.3-run01.json
```

Repeat runs and retain logs. The collector records Spark/Python/platform metadata,
per-test duration/outcome and whole-suite wall time; it exits nonzero on failures
or errors. JVM setup/teardown and shared-session overhead are excluded from
individual durations but included in wall time. This means the selection budget
is an **estimate**, not a hard CI wall-clock limit. Selected-test execution and strict history aggregation are now available through
the closed-loop runner below. Parallel scheduling and coverage inference remain future work.

To prepare measured features, group prior successful infrastructure runs by stable
test ID; use median durations, count completed pass/fail outcomes and record
failures. Exclude or investigate errors/skips rather than treating them as pass.
Keep the target run completely held out. Preserve version/configuration/commit
metadata separately, and do not mix incompatible environments blindly.

For an upgrade study, create separate environments for the baseline and target
versions, verify each version's published Python/Java requirements, and run the
same tests/data/configuration. Expand beyond these twenty tests using public
regression reproductions. See [research protocol](docs/EXPERIMENTS.md).

## Repository map

- `spark_rto/`: validated data model, selectors and JSON CLI
- `scripts/`: synthetic comparison and optional Spark measurement
- `tests/`: dependency-free unit and CLI tests
- `integration/`: optional real PySpark smoke tests
- `.github/workflows/ci.yml`: Python matrix CI plus manually triggered Spark job
- `docs/`: provenance, experiment protocol and publishing/upstream steps

CI installs the package and exercises the CLI on Python 3.9, 3.11 and 3.12.
The real Spark matrix compares pinned 3.5.3 and 4.0.0 with three fresh JVM runs each
on Python 3.11 / Java 17. Hosted runners may differ, so timings are descriptive,
not a controlled performance comparison. The real Spark job runs only with **Actions → CI → Run workflow** to keep routine
CI lightweight. No cloud account or credentials are needed.

## Provenance and contribution

The referenced starter ZIP was not accessible during creation; this is a fresh
implementation of the visible project plan, not a verified migration of that ZIP.
No employer source code, internal logs, datasets or documents were used.
See [provenance](docs/PROVENANCE.md) and [contribution rules](CONTRIBUTING.md).

Start with [GitHub publishing and Spark upstream steps](docs/PUBLISH_AND_UPSTREAM.md).
Local validation is recorded in [VALIDATION.md](docs/VALIDATION.md).

Historical bug reproduction: `python -m scripts.reproduce_52788 --output results/bug.json`
in isolated PySpark 4.0.0 and 4.0.1 environments. CI verifies the known failure
on 4.0.0 and correct XML on 4.0.1; this is not a newly discovered bug.

Latest status: [completed work and next priorities](docs/PROGRESS.md), including
120 expanded cross-version test executions and the verified historical defect.

## Measured selection loop

With PySpark and Java installed, run from the repository root:

```bash
python -m scripts.run_closed_loop --output-dir results/new-loop --budget 2 --strategy budget
```

Use a new output directory each time. This runs two full historical suites in fresh
processes, builds median duration and completed pass/fail counts, freezes selection,
then runs an independent full reference and the selected subset in fresh processes.
The output directory contains raw runs/logs, features, plan and evaluation JSON.
No target outcomes enter the selector. Timestamped histories must precede the
cutoff, have matching Spark/Python/platform and identical candidate inventories.
Errors reject a run; skips are excluded from history counts, and candidates with
no completed observation are rejected. Missing/new tests need an explicit future
cold-start policy, rather than being silently omitted.

Evaluation reports full-reference failures missed by selection, actual selected
failures, discrepancies between runs, undefined recall when no reference test
fails, observed test duration, whole-suite wall time and wall-budget overrun.
The budget constrains estimated test cost; JVM startup and fixture overhead may
cause wall time to exceed it. This runner does not kill tests at the budget limit.
Run-level timestamps identify ordering, not proof of identical hardware/config.
Keep the same source/configuration while executing a loop. This first loop uses
one Spark version per invocation; historical-defect fixtures are still separate.
