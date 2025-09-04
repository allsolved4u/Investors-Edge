# ===== FILE: reporting_mtr.py =====

from typing import List, Dict
from models import IncomeBreakdown
from taxes import compute_personal_tax

def marginal_tax_curve(
    province: str, age: int, year: int,
    base_inc: IncomeBreakdown,
    bumps: List[float]
) -> List[Dict[str, float]]:
    base = compute_personal_tax(base_inc, province, age, year)
    out = []
    for b in bumps:
        inc2 = IncomeBreakdown(**{**base_inc.__dict__})
        inc2.other_taxable += b
        t2 = compute_personal_tax(inc2, province, age, year)
        mtr = (t2.total_payable - base.total_payable) / b if b != 0 else 0.0
        out.append({"bump": b, "marginal_rate": mtr, "new_tax": t2.total_payable})
    return out
