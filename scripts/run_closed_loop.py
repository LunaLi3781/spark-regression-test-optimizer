"""Run prior history -> frozen selection -> full reference + selected execution."""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
from spark_rto.history import aggregate, evaluate
from spark_rto import select, STRATEGIES

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--budget', type=float, required=True)
    parser.add_argument('--strategy', choices=STRATEGIES, default='budget')
    parser.add_argument('--seed', type=int, default=0)
    args = parser.parse_args()
    root = Path(args.output_dir)
    root.mkdir(parents=True, exist_ok=False)
    def save(name, value):
        path = root/name
        path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')
        return path
    def run(name, selection=None):
        path = root/name
        command = [sys.executable, '-m', 'scripts.collect_spark', '--output', str(path)]
        if selection is not None:
            command += ['--selection', str(selection)]
        with (root/(name+'.log')).open('w') as log:
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
        if result.returncode not in (0,1) or not path.exists():
            raise RuntimeError('collector failed; inspect '+str(root))
        report = json.loads(path.read_text())
        if report['errors']:
            raise RuntimeError('infrastructure error; inspect '+str(path))
        return report
    history = [run('history-1.json'), run('history-2.json')]
    cutoff = datetime.now(timezone.utc).isoformat()
    features = aggregate(history, cutoff)
    save('features.json', [asdict(test) for test in features])
    chosen = select(features, args.budget, args.strategy, args.seed)
    plan = dict(cutoff=cutoff, history_run_ids=[r['run_id'] for r in history],
        candidate_ids=[t.id for t in features], selected_ids=[t.id for t in chosen],
        budget_s=args.budget, estimated_test_s=sum(t.duration_s for t in chosen),
        strategy=args.strategy, seed=args.seed)
    save('plan.json', plan)
    selection = save('selection.json', plan['selected_ids'])
    reference = run('reference.json')
    actual = run('selected.json', selection)
    result = evaluate(actual, reference, plan)
    save('evaluation.json', result)
    print(json.dumps(result, indent=2))

if __name__ == '__main__': main()
