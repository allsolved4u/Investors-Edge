# ===== FILE: accumulation.py =====

from typing import Tuple
from models import PersonProfile
from config.contribution_limits import rrsp_dollar_limit, tfsa_annual_room

def compute_pension_adjustment(person: PersonProfile, earnings: float) -> float:
    if person.pa_override is not None:
        return max(0.0, person.pa_override)
    if person.pension_plan == "DB":
        accrual = person.db_accrual_rate * earnings
        return max(0.0, 9.0 * accrual - 600.0)
    if person.pension_plan == "DC":
        return max(0.0, (person.dc_employee_rate + person.dc_employer_rate) * earnings)
    return 0.0

def rrsp_new_room(year: int, earnings: float, pa: float) -> float:
    limit = rrsp_dollar_limit(year)
    earned_cap = 0.18 * earnings
    return max(0.0, min(earned_cap, limit) - pa)

def tfsa_new_room(year: int, age: int) -> float:
    return tfsa_annual_room(year) if age >= 18 else 0.0

def plan_savings_target(person: PersonProfile, year_index: int) -> float:
    salary = person.employment_income * ((1 + person.wage_growth) ** year_index)
    return person.savings_rate * salary

def allocate_contributions(
    person: PersonProfile,
    year: int,
    year_index: int,
    contribution_policy: Tuple[str, ...] = ("rrsp", "tfsa", "nonreg")
):
    is_working = person.age + year_index < person.retirement_age
    earnings = person.employment_income * ((1 + person.wage_growth) ** year_index) if is_working else 0.0
    pa = compute_pension_adjustment(person, earnings)
    rrsp_room_available = person.rrsp_room_carryforward + rrsp_new_room(year, earnings, pa)
    tfsa_room_available = person.tfsa_room_carryforward + tfsa_new_room(year, person.age + year_index) + person.tfsa_recontribution_next_year
    target = plan_savings_target(person, year_index) if is_working else 0.0
    rrsp_contrib = tfsa_contrib = nonreg_con
    
    # ===== FILE: accumulation.py (continued) =====

    rrsp_contrib = tfsa_contrib = nonreg_contrib = 0.0
    remaining = target

    def put_rrsp(amount):
        nonlocal rrsp_contrib, remaining, rrsp_room_available
        add = min(amount, rrsp_room_available)
        rrsp_contrib += add
        rrsp_room_available -= add
        remaining -= add

    def put_tfsa(amount):
        nonlocal tfsa_contrib, remaining, tfsa_room_available
        add = min(amount, tfsa_room_available)
        tfsa_contrib += add
        tfsa_room_available -= add
        remaining -= add

    def put_nonreg(amount):
        nonlocal nonreg_contrib, remaining
        add = max(0.0, amount)
        nonreg_contrib += add
        remaining -= add

    for bucket in contribution_policy:
        if remaining <= 1e-9:
            break
        if bucket == "rrsp":
            put_rrsp(remaining)
        elif bucket == "tfsa":
            put_tfsa(remaining)
        elif bucket == "nonreg":
            put_nonreg(remaining)

    person.rrsp_room_carryforward = rrsp_room_available
    person.tfsa_room_carryforward = tfsa_room_available
    person.tfsa_recontribution_next_year = 0.0

    return {
        "rrsp_contrib": rrsp_contrib,
        "tfsa_contrib": tfsa_contrib,
        "nonreg_contrib": nonreg_contrib,
        "earnings_used": earnings,
        "pa": pa,
        "rrsp_room_end": person.rrsp_room_carryforward,
        "tfsa_room_end": person.tfsa_room_carryforward
    }
