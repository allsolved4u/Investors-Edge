# ===== FILE: spending.py =====

from dataclasses import dataclass
from typing import Literal

Strategy = Literal["fixed", "guardrails", "vpw"]

@dataclass
class GuardrailsPolicy:
    init_withdrawal_rate: float = 0.045
    lower_guardrail: float = 0.035
    upper_guardrail: float = 0.055
    adjust_pct: float = 0.10
    inflation_cap: float = 0.05

@dataclass
class VPWTable:
    by_age: dict = None
    def __post_init__(self):
        if self.by_age is None:
            self.by_age = {age: max(0.03, 0.035 + 0.0015 * (age - 60)) for age in range(50, 101)}

def spending_fixed(last_spend: float, inflation: float, cap: float = 0.10) -> float:
    return last_spend * (1 + min(inflation, cap))

def spending_guardrails(total_assets: float, last_spend: float, inflation: float, start_assets: float, pol: GuardrailsPolicy) -> float:
    proposed = last_spend * (1 + min(inflation, pol.inflation_cap))
    wr = proposed / max(1e-9, total_assets)
    if wr < pol.lower_guardrail:
        return proposed * (1 + pol.adjust_pct)
    if wr > pol.upper_guardrail:
        return proposed * (1 - pol.adjust_pct)
    return proposed

def spending_vpw(total_assets: float, age: int, inflation: float, vpw: VPWTable, last_spend: float = 0.0) -> float:
    rate = vpw.by_age.get(age, vpw.by_age[max(vpw.by_age)])
    return total_assets * rate
