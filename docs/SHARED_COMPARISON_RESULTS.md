# Shared-history strategy comparison — 2026-11-06

Source commit: 10d78ed.
CI: https://github.com/LunaLi3781/spark-regression-test-optimizer/actions/runs/42282503061

## Protocol and audit

Spark 4.0.0, Python 3.11, Java 17; 20 smoke tests plus SPARK-52788.
All strategies share two earlier full-suite runs and the same feature SHA-256.
Fourteen plans and two schedules were frozen before target runs. Budgets constrain
estimated test execution only; actual process time includes JVM startup/warm-up.
Random seeds 0/1/2 are all reported. Two rounds reverse a seeded shuffled order;
a shared full reference runs before the first round and after the second.
All 28 target executions completed with no outcome disagreements against their
reference. Unit suite: 35 tests passed. Raw JSON: validation/shared-comparison/.

## Results

Found/possible counts repeated observations of the SAME single known defect,
not independent bugs. Selected count is out of 21. Time is entire process wall time.

| Test budget s | Strategy | Seed | Selected | Found/possible | Median wall s | Wall range s |
|---:|---|---:|---:|---:|---:|---:|
| 1 | budget | 0 | 11 | 2/2 | 6.88 | 6.67–7.10 |
| 1 | change | 0 | 9 | 0/2 | 6.58 | 6.56–6.61 |
| 1 | cheapest | 0 | 12 | 0/2 | 6.90 | 6.59–7.21 |
| 1 | failure | 0 | 8 | 2/2 | 6.64 | 6.56–6.71 |
| 1 | random | 0 | 6 | 0/2 | 7.91 | 7.90–7.91 |
| 1 | random | 1 | 8 | 2/2 | 7.11 | 7.09–7.14 |
| 1 | random | 2 | 8 | 2/2 | 7.94 | 7.90–7.98 |
| 2 | budget | 0 | 17 | 2/2 | 8.08 | 8.03–8.12 |
| 2 | change | 0 | 9 | 0/2 | 8.05 | 7.98–8.13 |
| 2 | cheapest | 0 | 17 | 2/2 | 7.66 | 7.56–7.76 |
| 2 | failure | 0 | 8 | 2/2 | 8.18 | 8.16–8.19 |
| 2 | random | 0 | 16 | 2/2 | 9.09 | 9.07–9.10 |
| 2 | random | 1 | 14 | 2/2 | 8.49 | 8.34–8.65 |
| 2 | random | 2 | 15 | 2/2 | 8.96 | 8.88–9.03 |

## Observations

At the 1-second budget, failure-priority and budget-aware selection both retained
the defect; cheapest-first missed it, despite selecting more tests. At 2 seconds,
cheapest-first also retained it and had a lower measured median than budget-aware
selection. Thus these observations do not support unconditional superiority of
the budget heuristic. ID ordering missed the defect at both budgets. Random
selection missed it for seed 0 at 1 second and retained it for the other seeds.
These are descriptive observations on this fixture, not general success rates.

## Interpretation boundaries

- Historical data already contains the defect. This measures recurring-failure
  selection, not prediction of a newly introduced upgrade regression.
- All change scores are zero; `change` is ID ordering here, not a meaningful
  evaluation of coverage/change-aware selection.
- Each row has only two timing repetitions. Random seeds are not cherry-picked,
  but three seeds are not enough for a strong distributional claim.
- Shared full references are not adjacent paired controls for every plan. Timing
  drift, one runner, small fixtures and one defect limit generalization.
- Training and complete reference costs must be included when estimating net
  CI savings. No production savings, statistical significance or algorithm novelty
  is established by this diagnostic experiment.

Next: expand independent public defects, collect meaningful pre-target change
signals, and separate known recurring failures from unseen target failures before
asking external engineers to reproduce any effectiveness claim.
