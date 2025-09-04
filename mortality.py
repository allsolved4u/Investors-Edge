# ===== FILE: mortality.py =====

import math
import random
from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class GompertzParams:
    a: float
    b: float

DEFAULT_GOMPERTZ = {
    "M": GompertzParams(a=5e-5, b=0.095),
    "F": GompertzParams(a=3e-5, b=0.090),
}

def gompertz_survival(age: int, t: float, gp: GompertzParams) -> float:
    return math.exp(-(gp.a / gp.b) * (math.exp(gp.b * (age + t)) - math.exp(gp.b * age)))

def sample_death_age(current_age: int, sex: str, rng: random.Random, gp: Optional[GompertzParams] = None) -> int:
    gp = gp or DEFAULT_GOMPERTZ.get(sex, DEFAULT_GOMPERTZ["M"])
    lo, hi = 0.0, 60.0
    u = rng.random()
    for _ in range(40):
        mid = (lo + hi) / 2.0
        s = gompertz_survival(current_age, mid, gp)
        if s > u:
            lo = mid
        else:
            hi = mid
    return current_age + math.ceil(hi)

def sample_household_deaths(age1: int, sex1: str, age2: Optional[int], sex2: Optional[str], seed: int = 42) -> Tuple[int, Optional[int]]:
    rng = random.Random(seed)
    d1 = sample_death_age(age1, sex1, rng)
    d2 = sample_death_age(age2, sex2, rng) if (age2 is not None and sex2 is not None) else None
    return d1, d2
