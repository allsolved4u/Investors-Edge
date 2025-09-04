# ===== FILE: taxes_couples.py =====

from typing import Optional, Tuple
from models import IncomeBreakdown, TaxResult
from taxes import compute_personal_tax

def _eligible_split_amount(age: int, inc: IncomeBreakdown) -> float:
    amt = inc.pension_db
    if age >= 65:
        amt += inc.rrif + inc.annuity_registered
    return amt

def compute_household_tax(
    p1_inc: IncomeBreakdown,
    p2_inc: Optional[IncomeBreakdown],
    province: str,
    age1: int,
    age2: Optional[int],
    year: int

# ===== FILE: taxes_couples.py (continued) =====

def compute_household_tax(
    p1_inc: IncomeBreakdown,
    p2_inc: Optional[IncomeBreakdown],
    province: str,
    age1: int,
    age2: Optional[int],
    year: int
) -> Tuple[TaxResult, Optional[TaxResult], float]:
    """
    Compute household tax with simple pension splitting optimisation.
    Returns: (t1_result, t2_result_or_None, best_split_fraction)
    """
    if not p2_inc:
        # Single
        t1 = compute_personal_tax(p1_inc, province, age1, year)
        return t1, None, 0.0

    best_total = float("inf")
    best_frac = 0.0
    best_pair = (None, None)

    # Try split fractions from 0% to 50% in 5% increments
    for i in range(0, 11):
        frac = i * 0.05
        # Determine eligible amounts
        elig1 = _eligible_split_amount(age1, p1_inc)
        shift_amt = min(frac * elig1, elig1 * 0.5)

        # Apply shift from p1 to p2
        p1_mod = IncomeBreakdown(**{**p1_inc.__dict__})
        p2_mod = IncomeBreakdown(**{**p2_inc.__dict__})

        # Shift proportionally from eligible sources
        if elig1 > 0:
            if p1_mod.pension_db > 0:
                shift_db = min(p1_mod.pension_db, shift_amt)
                p1_mod.pension_db -= shift_db
                p2_mod.pension_db += shift_db
                shift_amt -= shift_db
            if shift_amt > 0 and age1 >= 65:
                if p1_mod.rrif > 0:
                    shift_rrif = min(p1_mod.rrif, shift_amt)
                    p1_mod.rrif -= shift_rrif
                    p2_mod.rrif += shift_rrif
                    shift_amt -= shift_rrif
                if shift_amt > 0 and p1_mod.annuity_registered > 0:
                    shift_ann = min(p1_mod.annuity_registered, shift_amt)
                    p1_mod.annuity_registered -= shift_ann
                    p2_mod.annuity_registered += shift_ann
                    shift_amt -= shift_ann

        t1 = compute_personal_tax(p1_mod, province, age1, year)
        t2 = compute_personal_tax(p2_mod, province, age2, year)
        total = t1.total_payable + t2.total_payable
        if total < best_total:
            best_total = total
            best_frac = frac
            best_pair = (t1, t2)

    return best_pair[0], best_pair[1], best_frac
