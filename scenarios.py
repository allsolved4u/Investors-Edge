# ===== FILE: scenarios.py =====

from dataclasses import dataclass
from typing import Callable, Dict, Any, List
from copy import deepcopy

from models import Household
from simulator import simulate

@dataclass
class Scenario:
    name: str
    tweak: Callable[[Household], Household]
    sim_years: int = 35
    params: Dict[str, Any] = None  # extra kwargs for simulate()

def tweak_retire_age(age: int) -> Callable[[Household], Household]:
    def _t(hh: Household) -> Household:
        hh2 = deepcopy(hh)
        hh2.person1.retirement_age = age
        if hh2.person2:
            hh2.person2.retirement_age = age
        return hh2
    return _t

def tweak_cpp_oas(cpp_age: int, oas_age: int) -> Callable[[Household], Household]:
    def _t(hh: Household) -> Household:
        hh2 = deepcopy(hh)
        hh2.person1.cpp_start_age = cpp_age
        hh2.person1.oas_start_age = oas_age
        if hh2.person2:
            hh2.person2.cpp_start_age = cpp_age
            hh2.person2.oas_start_age = oas_age
        return hh2
    return _t

def run_scenarios(base: Household, scenarios: List[Scenario], start_year=2024):
    out = {}
    for sc in scenarios:
        hh2 = sc.tweak(base)
        kwargs = dict(sc.params or {})
        kwargs.setdefault("start_year", start_year)
        out[sc.name] = simulate(hh2, years=sc.sim_years, **kwargs)
    return out
