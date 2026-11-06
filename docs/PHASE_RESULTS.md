# Lifecycle costs and recurring-defect selection — 2026-11-05

Validated source: 6426795. 31 unit tests pass on Python 3.9, 3.11 and 3.12.
CI: https://github.com/LunaLi3781/spark-regression-test-optimizer/actions/runs/42158113487
All jobs passed, including smoke suites and standalone defect controls.

## Protocol

21 tests: 20 smoke tests and one SPARK-52788 correctness test. Two prior full
runs per experiment generate features and median non-test process overhead.
Selection is frozen before two target pairs, alternating full/selected order.
Every nonempty suite runs the same small warm-up. Logs distinguish setup, warm-up,
test execution, cleanup, residual collector work and complete process wall time.
Test mode budgets estimated test cost. Wall mode first reserves historical overhead.
Both use the existing budget heuristic. Raw JSON: `validation/phases/`.

## Measurements

| Spark | Mode/budget | Selected | Pair | Estimated wall s | Actual wall s | Full wall s | Saved s | Failure recall |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 4.0.0 | test / 2s | 15/21 | 1 | 10.36 | 9.88 | 12.74 | 2.86 | 1.0 |
| 4.0.0 | test / 2s | 15/21 | 2 | 10.36 | 9.83 | 13.23 | 3.40 | 1.0 |
| 4.0.0 | wall / 12s | 20/21 | 1 | 11.73 | 11.90 | 12.28 | 0.38 | 1.0 |
| 4.0.0 | wall / 12s | 20/21 | 2 | 11.73 | 11.61 | 13.19 | 1.59 | 1.0 |
| 4.0.1 | test / 2s | 15/21 | 1 | 9.49 | 10.05 | 12.79 | 2.74 | None |
| 4.0.1 | test / 2s | 15/21 | 2 | 9.49 | 9.95 | 13.00 | 3.05 | None |
| 4.0.1 | wall / 12s | 20/21 | 1 | 11.60 | 12.02 | 13.27 | 1.25 | None |
| 4.0.1 | wall / 12s | 20/21 | 2 | 11.60 | 12.06 | 12.99 | 0.93 | None |

`None` means no failing reference tests, so recall is undefined. On 4.0.0, both
modes selected the known failing test in both pairs; selected outcomes matched
reference outcomes. Startup plus warm-up was approximately 7 seconds. Test-only
cost estimates cannot account for this fixed overhead. The 12-second wall mode
was close to measured process time but still exceeded the limit by approximately
0.02–0.06 seconds on 4.0.1. It is an estimate, not a deadline guarantee.

## Boundaries and next experiments

- This is selection of a recurring known defect: training already contains the
  4.0.0 failure. It does not demonstrate discovery of unseen regressions.
- One known defect, two pairs, tiny data and one hosted runner per version are
  insufficient for broad effectiveness or statistical significance claims.
- Training/full-reference experiment costs are not included in the reported
  per-selected-run savings; net CI savings depend on reuse of historical data.
- Both budget modes use different budgets and independently collected histories;
  this is not a fair comparison between algorithms or budget models.
- Warm-up changes the protocol. Earlier un-warmed reports are retained as historical
  evidence, not a controlled before/after performance comparison.
- The first CI attempt failed due to restoring an unset configuration with null.
  This harness defect was fixed and covered by a unit test before collecting these results.

Next: freeze one history set for all baselines and budgets, expand independent
public defect cases, report uncertainty across more pairs, and test unseen-failure
scenarios without tuning against target outcomes. Seek external reproduction only
with these scope boundaries visible.
