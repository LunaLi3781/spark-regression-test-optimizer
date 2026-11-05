"""Budget-constrained greedy baselines; no Spark or proprietary dependencies."""
from dataclasses import dataclass
from decimal import Decimal
import math
import random

STRATEGIES = ("random", "failure", "cheapest", "change", "budget")

@dataclass(frozen=True)
class TestCase:
    id: str
    duration_s: float
    runs: int = 0
    failures: int = 0
    change_score: float = 0.0

    def __post_init__(self):
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("id must be a nonempty string")
        for name, value in (("duration_s", self.duration_s), ("change_score", self.change_score)):
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError(name + " must be finite and numeric")
        if self.duration_s <= 0 or not 0 <= self.change_score <= 1:
            raise ValueError("duration must be positive; change_score must be in [0, 1]")
        if type(self.runs) is not int or type(self.failures) is not int:
            raise ValueError("runs/failures must be integers")
        if not 0 <= self.failures <= self.runs:
            raise ValueError("require 0 <= failures <= runs")

    @property
    def risk(self):
        # Laplace smoothing: a cold-start test has risk 0.5, not zero.
        return (self.failures + 1) / (self.runs + 2)


def select(tests, budget_s, strategy="budget", seed=0):
    if isinstance(budget_s, bool) or not isinstance(budget_s, (int, float)) or not math.isfinite(budget_s) or budget_s < 0:
        raise ValueError("budget must be finite and nonnegative")
    if strategy not in STRATEGIES:
        raise ValueError("unknown strategy: " + str(strategy))
    ordered = sorted(tests, key=lambda t: t.id)
    if len({t.id for t in ordered}) != len(ordered):
        raise ValueError("duplicate test id")
    if strategy == "random":
        random.Random(seed).shuffle(ordered)
    else:
        keys = {
            "failure": lambda t: (-t.risk, t.id),
            "cheapest": lambda t: (t.duration_s, t.id),
            "change": lambda t: (-t.change_score, t.id),
            "budget": lambda t: (-(t.risk * (1 + t.change_score) / t.duration_s), t.id),
        }
        ordered.sort(key=keys[strategy])
    remaining = Decimal(str(budget_s))
    chosen = []
    for test in ordered:
        cost = Decimal(str(test.duration_s))
        if cost <= remaining:
            chosen.append(test)
            remaining -= cost
    return chosen
