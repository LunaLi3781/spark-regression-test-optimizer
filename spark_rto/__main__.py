import argparse
import json
from pathlib import Path
from .selection import TestCase, select, STRATEGIES


def load(path):
    raw = json.loads(Path(path).read_text())
    if not isinstance(raw, list):
        raise ValueError("input must be a JSON array")
    return [TestCase(**row) for row in raw]


def main():
    parser = argparse.ArgumentParser(description="Select tests within an estimated serial-time budget")
    parser.add_argument("input", help="JSON array of historical test features")
    parser.add_argument("--budget", type=float, required=True)
    parser.add_argument("--strategy", choices=STRATEGIES, default="budget")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--outcomes", help="Optional HELD-OUT JSON mapping test IDs to pass/fail")
    args = parser.parse_args()
    try:
        tests = load(args.input)
        chosen = select(tests, args.budget, args.strategy, args.seed)
        report = dict(strategy=args.strategy, seed=args.seed, budget_s=args.budget,
                      selected=[t.id for t in chosen], estimated_duration_s=sum(t.duration_s for t in chosen))
        if args.outcomes:
            outcomes = json.loads(Path(args.outcomes).read_text())
            if not isinstance(outcomes, dict) or set(outcomes) != {t.id for t in tests} or any(v not in ("pass", "fail") for v in outcomes.values()):
                raise ValueError("outcomes must cover exactly the candidate IDs with pass/fail")
            total = sum(v == "fail" for v in outcomes.values())
            found = sum(outcomes[t.id] == "fail" for t in chosen)
            report.update(failing_tests_found=found, failing_tests_total=total,
                          failing_test_recall=found / total if total else None)
        print(json.dumps(report, indent=2, allow_nan=False))
    except (ValueError, TypeError, OSError) as error:
        parser.error(str(error))

if __name__ == "__main__":
    main()
