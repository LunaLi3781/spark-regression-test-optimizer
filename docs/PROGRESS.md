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
validated against real held-out failures. No upstream PR has been submitted.

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
