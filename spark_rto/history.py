"""Strict chronological feature construction from measured complete-suite runs."""
from datetime import datetime
from statistics import median
from .selection import TestCase

def timestamp(value):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('timestamps must include timezone')
    return parsed

def aggregate(reports, cutoff):
    cutoff = timestamp(cutoff)
    groups, environment, ids, run_ids = {}, None, None, set()
    if not reports:
        raise ValueError('history is empty')
    for report in reports:
        if report['run_id'] in run_ids:
            raise ValueError('duplicate run_id')
        run_ids.add(report['run_id'])
        if not timestamp(report['started_at']) <= timestamp(report['finished_at']) < cutoff:
            raise ValueError('history must finish strictly before cutoff')
        if report.get('selected_ids') is not None or report['errors'] or report.get('data_kind') != 'measured':
            raise ValueError('require full measured runs without infrastructure errors')
        env = tuple(report[k] for k in ('spark_version', 'python', 'platform'))
        if environment is not None and env != environment:
            raise ValueError('mixed history environments')
        environment = env
        current = set()
        for row in report['tests']:
            if row['id'] in current:
                raise ValueError('duplicate test ID')
            current.add(row['id'])
            if row['outcome'] not in ('pass', 'fail', 'skip', 'error'):
                raise ValueError('unknown outcome')
            if row['outcome'] in ('skip', 'error'):
                continue
            TestCase(row['id'], row['duration_s'])
            groups.setdefault(row['id'], []).append(row)
        if ids is not None and current != ids:
            raise ValueError('history test inventory changed')
        ids = current
    if set(groups) != ids or not ids:
        raise ValueError('each candidate needs a completed historical observation')
    return [TestCase(key, median(r['duration_s'] for r in rows), len(rows),
                     sum(r['outcome'] == 'fail' for r in rows))
            for key, rows in sorted(groups.items())]


def evaluate(selected_report, reference, plan):
    """Evaluate against an independent full run, keeping discrepancies explicit."""
    if reference['run_id'] == selected_report['run_id']:
        raise ValueError('reference must be independent')
    for key in ('spark_version', 'python', 'platform'):
        if reference[key] != selected_report[key]:
            raise ValueError('target environments differ')
    if reference.get('selected_ids') is not None or reference['errors'] or selected_report['errors']:
        raise ValueError('incomplete or errored evaluation')
    def outcomes(report):
        rows = report['tests']
        result = {r['id']: r['outcome'] for r in rows}
        if len(result) != len(rows) or any(v not in ('pass', 'fail') for v in result.values()):
            raise ValueError('evaluation requires unique completed tests')
        return result
    full, actual = outcomes(reference), outcomes(selected_report)
    if set(full) != set(plan['candidate_ids']) or set(actual) != set(plan['selected_ids']):
        raise ValueError('evaluation inventory mismatch')
    failed = {k for k,v in full.items() if v == 'fail'}
    found = failed & set(actual)
    return dict(reference_failures=sorted(failed), selected_reference_failures=sorted(found),
        missed_reference_failures=sorted(failed-set(actual)),
        observed_selected_failures=sorted(k for k,v in actual.items() if v == 'fail'),
        outcome_disagreements=sorted(k for k,v in actual.items() if full[k] != v),
        failing_test_recall=len(found)/len(failed) if failed else None,
        observed_test_s=sum(r['duration_s'] for r in selected_report['tests']),
        observed_wall_s=selected_report['total_wall_s'],
        wall_budget_overrun_s=max(0,selected_report['total_wall_s']-plan['budget_s']),
        budget_s=plan['budget_s'], estimated_test_s=plan['estimated_test_s'])
