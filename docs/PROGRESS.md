# Progress and next steps — 2026-11-04

## Completed

- Public MIT-licensed independent repository with provenance and contribution guidance.
- Five deterministic/reproducible selection baselines, validated JSON CLI and synthetic evaluation.
- Package installation verified; 15 core tests pass on Python 3.9, 3.11 and 3.12 in CI.
- Expanded original SQL smoke coverage from 8 to 20 tests.
- Spark 3.5.3 and 4.0.0: three independent runs per version; **120/120 test executions passed**.
- Public historical defect SPARK-52788: verified specific BinaryType-to-XML failure on
  4.0.0 and correct output on 4.0.1, with a passing string control on both versions.
- Raw JSON evidence committed in `validation/expanded/`.

Validated source commit: 318aca5.
CI: https://github.com/LunaLi3781/spark-regression-test-optimizer/actions/runs/41977589794

## Evidence boundaries

The historical bug workflow succeeds when the observed failure/fix matches its
explicit version expectation. A green job on 4.0.0 does not mean the defect is absent.
The bug was already reported and fixed upstream; this project supplies independent
reproduction, not discovery or repair credit. It is not established as a regression
from 3.5.3, where built-in XML capability differs.

Smoke tests are small and not representative of all Spark workloads. Hosted-runner
latency is not a controlled performance comparison. The optimizer has not yet been
validated against real held-out failures. An upstream draft PR has since been submitted; see the 2026-11-09 update below.

## Priority order

1. Build validated history aggregation: stable IDs, median prior duration, pass/fail
   counts, explicit error/skip exclusion, environment/version metadata and time cutoffs.
2. Connect selected IDs to actual test execution and record observed time, overhead,
   misses and budget overruns. Keep full-suite reference runs.
3. Build a public corpus of 5–10 independent historical defects with affected/fixed
   versions and traceable sources. Keep defect-specific tests separate from general
   smoke tests. Never fabricate past failure counts from target outcomes.
4. Compare all baselines on chronological held-out runs and multiple budgets/seeds;
   report failing-test recall and unique-defect recall separately. Publish negative results.
5. Use a newly confirmed upstream-relevant gap for a small Apache Spark contribution;
   search existing issues/PRs first. Do not resubmit the already fixed SPARK-52788.

This is a functioning engineering prototype plus an initial real-defect fixture,
not yet evidence of algorithm superiority, adoption, a paper or upstream acceptance.

## Closed-loop update

History aggregation, exact selected-test execution and independent full-reference
evaluation are now implemented and verified in CI. Core coverage is now 23 tests.
See [measured results](CLOSED_LOOP_RESULTS.md). Priorities 1–2 above are complete
for the smoke-suite MVP; cross-version defect-corpus integration remains open.

## Lifecycle and defect integration update (2026-11-05)

31 unit tests now pass. The recurring SPARK-52788 defect is integrated into
selection with phase timing and alternating paired runs. See [results](PHASE_RESULTS.md).
The small measured savings do not establish general optimizer superiority.

## Shared-history update (2026-11-06)

All five strategies now share frozen historical features and equal test-cost
budgets. 35 unit tests pass; 28 actual target executions completed.
[Results](SHARED_COMPARISON_RESULTS.md) show budget-dependent tradeoffs, not
unconditional superiority of the budget heuristic. Next priority is independent
defect diversity and meaningful pre-target change information.

## Upstream contribution update (2026-11-09)

Submitted [Apache Spark PR #60225](https://github.com/apache/spark/pull/60225)
to fix literal column-name handling in `assertDataFrameEqual(ignoreColumnOrder=True)`.
The defect can hide unequal values when a dotted top-level name overlaps a struct
field path. This is separate from the previously fixed SPARK-52788 fixture.

Two regression methods cover special names and the false-positive case.
[Contributor-owned source CI](https://github.com/LunaLi3781/spark-regression-test-optimizer/actions/runs/42515177490)
built the exact patch commit `4075e4b7a914cf67e5f35ee039c37df9c12cfaec` with Hive
and passed the native `pyspark.sql.tests.test_utils` suite (Python 3.11 / Java 21).
Lint and formatting checks also passed. Connect parity has not been run.

The PR remains a draft awaiting a JIRA issue. The official Build check reports
workflow-run detection failure; the separate passing run is not an official CI pass.
No maintainer review or upstream acceptance has been recorded as of this update.
This contribution demonstrates a reproducible correctness fix, not optimizer
superiority or external adoption.

## Formal upstream submission (2026-11-10)

Created [SPARK-61436](https://issues.apache.org/jira/browse/SPARK-61436)
(Bug, PySpark, affected version 5.0.0, priority Major) and linked it to
[PR #60225](https://github.com/apache/spark/pull/60225). The PR is now open
and ready for review, no longer a draft. The passing contributor-owned source
validation still applies to the unchanged patch commit.

Official Build remains ACTION_REQUIRED: the upstream checker cannot detect
a fork workflow run, and the fork workflow API currently lists no workflows.
The repository owner needs to initialize the fork's Actions workflows before
that CI path can be completed. No upstream acceptance or review is claimed.
