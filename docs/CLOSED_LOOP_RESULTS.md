# Measured closed-loop validation

Source commit: 49849c5.
CI: https://github.com/LunaLi3781/spark-regression-test-optimizer/actions/runs/41978137384

23 core tests pass across Python 3.9/3.11/3.12. Both Spark matrix jobs and
both historical-defect expectation checks pass. Each closed loop builds two
prior full runs, freezes features and selection, then executes an independent
full reference and selected subset. Raw JSON files are in validation/closed-loop/.

Budget: 2 seconds of estimated test cost, not a hard wall limit.

| Version | Selected | Estimated test s | Actual test s | Wall s | Wall overrun s |
|---|---:|---:|---:|---:|---:|
| spark-smoke-3.5.3 | 14/20 | 1.90 | 5.90 | 8.99 | 6.99 |
| spark-smoke-4.0.0 | 14/20 | 1.86 | 4.31 | 9.29 | 7.29 |

All selected and reference tests passed; recall is undefined. These results
validate the pipeline, not algorithm superiority. Startup, fixtures and test
order affect costs. Reference failures selected, actual selected failures and
cross-run disagreements are reported separately to expose flaky observations.

Remaining priorities: characterize startup/order costs, integrate version-specific
historical-defect tests into an independent evaluation corpus, expand to 5–10
public defects, then compare all strategies on held-out data. Current smoke
closed loops run one version per invocation; they do not automatically migrate
environments or evaluate the standalone defect fixture.
