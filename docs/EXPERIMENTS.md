# Experiment protocol

1. Begin with the synthetic demo only to validate plumbing. It is not evidence
   of savings or algorithm superiority.
2. Collect repeated full-suite runs in controlled, isolated baseline/target Spark
   environments. Record commit, Spark/Python/JDK versions, OS, CPU/RAM, Spark
   configuration, seeds, inputs and warm-up policy. Retain raw logs and provenance.
3. Separate earlier training history, optional validation history and later held-out
   upgrade runs chronologically. Estimate costs from past runs only. Explain the
   cold-start prior and manually assigned change scores before observing labels.
4. Compare all five strategies at budgets such as 10%, 25%, 50%, 75% and 100% of
   estimated full-suite cost. Run random selection with at least 30 seeds for real
   studies; report variability, not the best random seed.
5. Measure failing-test recall, actual selected runtime and budget overruns, plus
   full-suite failures missed. Group tests by root cause before claiming unique-bug
   discovery. No-failure runs have undefined recall, not zero or perfect recall.
6. Always retain a scheduled full-suite reference run. Do not use this prototype
   to remove release-critical coverage. Cost estimates can drift across upgrades.
7. Examine flaky tests, shared-session ordering, JVM startup and repeated execution
   effects. Report failures caused by infrastructure separately from regressions.
8. Report negative results and confidence intervals across independent runs/issues.
   The synthetic dataset is too small for significance claims.

Next milestones: add a validated history aggregator, selected-test runner with
observed wall-clock accounting, 20–30 independent public SQL tests, one public
historical regression reproduction, then a chronological multi-version study.
Only after obtaining measured evidence consider a paper or an upstream proposal.
