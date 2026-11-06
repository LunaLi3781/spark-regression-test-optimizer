"""Historical overhead reserve; estimates are never a hard deadline."""
from statistics import median
import math

def reserve_budget(history, budget, mode):
    if not math.isfinite(budget) or budget < 0 or mode not in ('test', 'wall'):
        raise ValueError('invalid budget or mode')
    overhead = median(max(0, r['process_wall_s'] - sum(t['duration_s'] for t in r['tests'])) for r in history)
    reserve = overhead if mode == 'wall' else 0
    return max(0, budget-reserve), overhead
