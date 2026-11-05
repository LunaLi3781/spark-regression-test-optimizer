"""Collect one run; retain full log to diagnose fixture/setup failures."""
import argparse
from datetime import datetime, timezone
import uuid
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
    parser.add_argument("--selection", help="JSON list of exact discovered test IDs")
    args = parser.parse_args()
    import pyspark
    started_at = datetime.now(timezone.utc).isoformat()
    started = time.perf_counter()
    suite = unittest.defaultTestLoader.discover("integration", pattern="test_*.py")
    selected_ids = None
    if args.selection:
        selected_ids = json.loads(Path(args.selection).read_text())
        def flatten(items):
            for item in items:
                if isinstance(item, unittest.TestSuite):
                    yield from flatten(item)
                else:
                    yield item
        inventory = {test.id(): test for test in flatten(suite)}
        if not isinstance(selected_ids, list) or any(not isinstance(k, str) for k in selected_ids):
            raise ValueError('selection must be a list of IDs')
        if len(set(selected_ids)) != len(selected_ids) or set(selected_ids) - set(inventory):
            raise ValueError('duplicate or unknown selection IDs')
        suite = unittest.TestSuite(inventory[k] for k in selected_ids)
    result = unittest.TextTestRunner(verbosity=2, resultclass=RecordingResult).run(suite)
    report = dict(data_kind="measured", run_id=str(uuid.uuid4()), started_at=started_at,
                  finished_at=datetime.now(timezone.utc).isoformat(), selected_ids=selected_ids, spark_version=pyspark.__version__, python=platform.python_version(),
                  platform=platform.platform(), total_wall_s=time.perf_counter()-started,
                  successful=result.wasSuccessful(), errors=len(result.errors), failures=len(result.failures), tests=result.records)
    target = Path(args.output); target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2) + "\n")
    raise SystemExit(0 if result.wasSuccessful() and (result.testsRun or selected_ids == []) else 1)

if __name__ == "__main__": main()
