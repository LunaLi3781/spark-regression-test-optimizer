"""Freeze all strategy plans from one historical feature set, without outcomes."""
import hashlib
import json
import random
from dataclasses import asdict
from .selection import select, STRATEGIES

def build_plans(features, budgets=(1.0, 2.0), seeds=(0, 1, 2)):
    features = sorted(features, key=lambda t: t.id)
    if not features or not budgets or not seeds:
        raise ValueError('nonempty features, budgets and seeds required')
    if len(set(budgets)) != len(budgets) or len(set(seeds)) != len(seeds):
        raise ValueError('duplicate budgets or seeds')
    digest = hashlib.sha256(json.dumps([asdict(t) for t in features], sort_keys=True).encode()).hexdigest()
    plans = []
    for index, budget in enumerate(budgets):
        for strategy in STRATEGIES:
            for seed in seeds if strategy == 'random' else (0,):
                chosen = select(features, budget, strategy, seed)
                plans.append(dict(id=f'b{index}-{strategy}-{seed}', strategy=strategy, seed=seed,
                    budget_s=budget, budget_mode='test', feature_sha256=digest,
                    candidate_ids=[t.id for t in features], selected_ids=[t.id for t in chosen],
                    estimated_test_s=sum(t.duration_s for t in chosen)))
    return plans

def schedule(plans, round_index):
    ordered = list(plans)
    random.Random(20261106).shuffle(ordered)
    return ordered if round_index % 2 == 0 else list(reversed(ordered))
