"""Shared-history actual-execution comparison; no fitted model or target tuning."""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time
from spark_rto.comparison import build_plans, schedule
from spark_rto.history import aggregate, evaluate

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', required=True)
    args = parser.parse_args()
    root = Path(args.output_dir)
    root.mkdir(parents=True, exist_ok=False)
    def save(name, value):
        path = root/name
        path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')
        return path
    def run(name, selection=None):
        path = root/(name+'.json')
        command = [sys.executable, '-m', 'scripts.collect_spark', '--include-defect', '--output', str(path)]
        if selection is not None:
            command += ['--selection', str(selection)]
        started = time.perf_counter()
        with (root/(name+'.log')).open('w') as log:
            process = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
        elapsed = time.perf_counter()-started
        if process.returncode not in (0,1) or not path.exists():
            raise RuntimeError('collector crashed: '+name)
        report = json.loads(path.read_text())
        report['process_wall_s'] = elapsed
        save(name+'.json', report)
        if report['errors'] or any(t['outcome'] not in ('pass','fail') for t in report['tests']):
            raise RuntimeError('invalid experiment run: '+name)
        return report
    history = [run('history-0'), run('history-1')]
    cutoff = datetime.now(timezone.utc).isoformat()
    features = aggregate(history, cutoff)
    save('features.json', [asdict(t) for t in features])
    plans = build_plans(features)
    manifest = dict(cutoff=cutoff, history_run_ids=[r['run_id'] for r in history], plans=plans,
        schedules=[[p['id'] for p in schedule(plans,i)] for i in range(2)],
        change_signal='absent: all scores zero; change baseline degenerates to ID ordering')
    save('manifest.json', manifest)  # frozen before any target execution
    selections = {p['id']:save(p['id']+'-selection.json',p['selected_ids']) for p in plans}
    results = []
    for round_index in range(2):
        reference = run(f'reference-{round_index}') if round_index == 0 else None
        actual = {}
        for plan in schedule(plans,round_index):
            actual[plan['id']] = run(f'r{round_index}-'+plan['id'], selections[plan['id']])
        if reference is None:
            reference = run(f'reference-{round_index}')
        for plan in plans:
            measured = actual[plan['id']]
            row = evaluate(measured,reference,plan)
            row.update(plan_id=plan['id'], round=round_index, strategy=plan['strategy'],seed=plan['seed'],
                selected_count=len(plan['selected_ids']), feature_sha256=plan['feature_sha256'],
                process_wall_s=measured['process_wall_s'], reference_process_wall_s=reference['process_wall_s'],
                process_time_saved_s=reference['process_wall_s']-measured['process_wall_s'])
            results.append(row)
        save('comparison.json',dict(rows=results, completed_rounds=round_index+1))
    print(json.dumps(dict(completed_rounds=2, executions=len(results))))

if __name__ == '__main__': main()
