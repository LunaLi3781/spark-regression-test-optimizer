"""Run from repository root: python3 -m scripts.evaluate_demo."""
import json
from spark_rto.__main__ import load
from spark_rto import select, STRATEGIES

def main():
    tests = load("examples/history.json")
    with open("examples/outcomes.json") as f:
        outcomes = json.load(f)
    rows = []
    for budget in (5, 10, 20, 28):
        for strategy in STRATEGIES:
            for seed in (range(10) if strategy == "random" else [0]):
                chosen = select(tests, budget, strategy, seed)
                found = sum(outcomes[t.id] == "fail" for t in chosen)
                rows.append(dict(budget_s=budget, strategy=strategy, seed=seed,
                    estimated_duration_s=sum(t.duration_s for t in chosen),
                    selected=[t.id for t in chosen], failing_test_recall=found / 3))
    print(json.dumps(dict(data_kind="synthetic", rows=rows), indent=2))

if __name__ == "__main__":
    main()
