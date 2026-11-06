"""Run prior history -> frozen selection -> full reference + selected execution."""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time
from spark_rto.cost import reserve_budget
from spark_rto.history import aggregate, evaluate
from spark_rto import select, STRATEGIES

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--budget', type=float, required=True)
    parser.add_argument('--strategy', choices=STRATEGIES, default='budget')
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--include-defect', action='store_true')
    parser.add_argument('--budget-mode', choices=['test', 'wall'], default='test')
    parser.add_argument('--pairs', type=int, default=1)
    args = parser.parse_args()
    if args.pairs < 1:
        parser.error('--pairs must be positive')
    root = Path(args.output_dir)
    root.mkdir(parents=True, exist_ok=False)
    def save(name, value):
        path = root/name
        path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')
        return path
    def run(name, selection=None):
        path = root/name
        command = [sys.executable, '-m', 'scripts.collect_spark', '--output', str(path)]
        if args.include_defect:
            command += ['--include-defect']
        if selection is not None:
            command += ['--selection', str(selection)]
        process_started = time.perf_counter()
        with (root/(name+'.log')).open('w') as log:
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
        process_wall_s = time.perf_counter()-process_started
        if result.returncode not in (0,1) or not path.exists():
            raise RuntimeError('collector failed; inspect '+str(root))
        report = json.loads(path.read_text())
        report['process_wall_s'] = process_wall_s
        save(name, report)
        if report['errors']:
            raise RuntimeError('infrastructure error; inspect '+str(path))
        return report
    history = [run('history-1.json'), run('history-2.json')]
    cutoff = datetime.now(timezone.utc).isoformat()
    features = aggregate(history, cutoff)
    save('features.json', [asdict(test) for test in features])
    available, reserve = reserve_budget(history, args.budget, args.budget_mode)
    chosen = select(features, available, args.strategy, args.seed)
    plan = dict(cutoff=cutoff, history_run_ids=[r['run_id'] for r in history],
        candidate_ids=[t.id for t in features], selected_ids=[t.id for t in chosen],
        budget_s=args.budget, estimated_test_s=sum(t.duration_s for t in chosen),
        strategy=args.strategy, seed=args.seed, budget_mode=args.budget_mode,
        overhead_reserve_s=reserve if args.budget_mode == 'wall' else 0,
        estimated_overhead_s=reserve, estimated_wall_s=reserve+sum(t.duration_s for t in chosen))
    save('plan.json', plan)
    selection = save('selection.json', plan['selected_ids'])
    evaluations = []
    for pair in range(args.pairs):
        if pair % 2 == 0:
            reference = run(f'reference-{pair}.json')
            actual = run(f'selected-{pair}.json', selection)
        else:
            actual = run(f'selected-{pair}.json', selection)
            reference = run(f'reference-{pair}.json')
        result = evaluate(actual, reference, plan)
        result.update(pair=pair, reference_process_wall_s=reference['process_wall_s'],
            selected_process_wall_s=actual['process_wall_s'],
            process_time_saved_s=reference['process_wall_s']-actual['process_wall_s'],
            process_budget_overrun_s=max(0,actual['process_wall_s']-args.budget),
            reference_timing=reference['timing'], selected_timing=actual['timing'])
        evaluations.append(result)
    save('evaluation.json', dict(pairs=evaluations))
    print(json.dumps(evaluations, indent=2))

if __name__ == '__main__': main()
