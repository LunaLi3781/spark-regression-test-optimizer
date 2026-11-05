"""Collect one run; retain full log to diagnose fixture/setup failures."""
import argparse
import json
import platform
import time
import unittest
from pathlib import Path

class RecordingResult(unittest.TextTestResult):
    def startTest(self, test):
        super().startTest(test)
        self.started = time.perf_counter()
        self.status = "pass"
    def addFailure(self, test, err):
        self.status = "fail"
        super().addFailure(test, err)
    def addError(self, test, err):
        self.status = "error"
        super().addError(test, err)
    def addSkip(self, test, reason):
        self.status = "skip"
        super().addSkip(test, reason)
    def stopTest(self, test):
        self.records.append(dict(id=test.id(), duration_s=time.perf_counter()-self.started, outcome=self.status))
        super().stopTest(test)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    import pyspark
    started = time.perf_counter()
    suite = unittest.defaultTestLoader.discover("integration", pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=2, resultclass=RecordingResult).run(suite)
    report = dict(data_kind="measured", spark_version=pyspark.__version__, python=platform.python_version(),
                  platform=platform.platform(), total_wall_s=time.perf_counter()-started,
                  successful=result.wasSuccessful(), errors=len(result.errors), failures=len(result.failures), tests=result.records)
    target = Path(args.output); target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2) + "\n")
    raise SystemExit(0 if result.wasSuccessful() and result.testsRun else 1)

if __name__ == "__main__": main()
