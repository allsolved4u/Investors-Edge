# ===== FILE: survivor.py =====

from typing import Optional
from models import PersonProfile
from portfolio import RRSPAccount, TFSAAccount

def apply_spousal_rollovers(
    decedent: PersonProfile,
    survivor: PersonProfile,
    dec_rrsp: RRSPAccount,
    dec_tfsa: TFSAAccount,
    surv_rrsp: RRSPAccount,
    surv_tfsa: TFSAAccount,
    rrsp_rollover: bool = True,
    tfsa_successor: bool = True
):
    if rrsp_rollover and dec_rrsp.balance > 0:
        surv_rrsp.balance += dec_rrsp.balance
        dec_rrsp.balance = 0.0
    if tfsa_successor and dec_tfsa.balance > 0:
        surv_tfsa.balance += dec_tfsa.balance
        dec_tfsa.balance = 0.0

def cpp_survivor_benefit_approx(survivor_age: int, survivor_cpp: float, deceased_cpp: float, cap_fraction: float = 0.60) -> float:
    add = min(deceased_cpp * cap_fraction, max(0.0, deceased_cpp))
    combined = survivor_cpp + add
    cap = survivor_cpp * (1.0 + cap_fraction)
    return min(combined, cap) - survivor_cpp

def reduce_expenses_for_survivor(household_expenses: float, ratio: float) -> float:
    return household_expenses * ratio
