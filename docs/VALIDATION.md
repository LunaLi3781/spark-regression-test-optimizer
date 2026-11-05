# Validation — 2026-11-04

## Local results

Environment: macOS arm64, Python 3.9.6, Homebrew OpenJDK 17.0.21.0.3,
PySpark 3.5.3 and py4j 0.10.9.7. Dependencies were installed in a local virtual
environment; neither packages nor environment files are committed.

- Package wheel built and installed successfully with `pip install . pyspark==3.5.3`.
- Installed `spark-rto` command exercised from outside the source repository: passed.
- `python -m pip check`: no broken requirements.
- `python -m unittest discover -s tests -v`: **15 tests passed**.
- `python -m scripts.collect_spark --output results/spark-3.5.3-run01.json`:
  **8 real Spark SQL smoke tests passed**, zero failures/errors; whole-suite
  measured wall time approximately 5.06 seconds (one run, not a benchmark).
- [Measured per-test results](validation/spark-3.5.3-macos.json).
- Synthetic demo: 56 comparison rows; all respect their estimated budgets.
  See `demo-results.json`. Synthetic failures are not Spark regressions.

For this Homebrew Java setup, the Spark command used:

```bash
JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home \
SPARK_LOCAL_IP=127.0.0.1 \
.venv/bin/python -m scripts.collect_spark --output results/spark-3.5.3-run01.json
```

The first restricted run could not bind a local JVM communication port and ran
zero tests; the successful rerun had the required local-process permissions.
Spark emitted expected native-Hadoop fallback and unpartitioned-window warnings
for this tiny local smoke suite. Logs were retained locally.

This verifies one Spark version and environment, not upgrade compatibility or
selection effectiveness. No measured optimization benefit is claimed. GitHub CI
status should be checked at the repository's Actions page.
