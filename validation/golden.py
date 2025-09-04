# ===== FILE: validation/golden.py =====

import json, math, argparse
from typing import Dict, Any, List, Tuple

from models import IncomeBreakdown, PersonProfile, Household, AccountBalances
from taxes import compute_personal_tax
from simulator import simulate

ABS_TOL = 1.00
REL_TOL = 0.005  # 0.5%

def _close(a: float, b: float, abs_tol: float, rel_tol: float) -> bool:
    return math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)

def _compare_dicts(actual: Dict[str, float], expected: Dict[str, float],
                   abs_tol=ABS_TOL, rel_tol=REL_TOL) -> List[str]:
    diffs = []
    keys = set(actual) | set(expected)
    for k in sorted(keys):
        a = actual.get(k, 0.0)
        e = expected.get(k, 0.0)
        if not _close(a, e, abs_tol, rel_tol):
            diffs.append(f"{k}: actual={a:.2f}, expected={e:.2f}")
    return diffs

def case_simple_tax_ab() -> Dict[str, Any]:
    inc = IncomeBreakdown(
        employment=0.0, interest=3000.0, other_taxable=0.0,
        rrif=40000.0, cpp=14000.0, oas=9000.0,
        eligible_dividends=5000.0, non_eligible_dividends=2000.0,
        capital_gains_realized=10000.0, deductions=0.0
    )
    res = compute_personal_tax(inc, province="AB", age=68, year=2024)
    return {
        "taxable_income": res.taxable_income,
        "federal_tax": res.federal_tax,
        "provincial_tax": res.provincial_tax,
        "oas_recovery": res.oas_recovery_tax,
        "total_tax": res.total_payable,
        "net_income": res.net_income
    }

def case_couple_split_on() -> Dict[str, Any]:
    p1 = PersonProfile(name="P1", age=68, province="ON", retirement_age=65,
                       balances=AccountBalances(), cpp_amount_at_65=14000, oas_amount_at_65=9000)
    p2 = PersonProfile(name="P2", age=66, province="ON", retirement_age=65,
                       balances=AccountBalances(), cpp_amount_at_65=8000, oas_amount_at_65=9000)
    hh = Household(person1=p1, person2=p2, annual_expenses=60000)
    results = simulate(hh, years=1, start_year=2024)
    yr = results[0] if isinstance(results, list) else results[0]
    return {
        "taxes_total": yr.taxes_total,
        "split_fraction": yr.split_fraction
    }

def run_golden_suite(baseline_path: str, write=False,
                     abs_tol=ABS_TOL, rel_tol=REL_TOL) -> Tuple[bool, List[str]]:
    actual = {
        "simple_tax_ab": case_simple_tax_ab(),
        "couple_split_on": case_couple_split_on(),
    }
    if write:
        with open(baseline_path, "w") as f:
            json.dump(actual, f, indent=2)
        return True, ["Golden written"]

    with open(baseline_path, "r") as f:
        expected = json.load(f)

    diffs_all = []
    ok = True
    for name, act in actual.items():
        exp = expected.get(name, {})
        diffs = _compare_dicts(act, exp, abs_tol, rel_tol)
        if diffs:
            ok = False
            diffs_all.append(f"[{name}] " + "; ".join(diffs))
    return ok, diffs_all

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", default="baselines/golden_2024.json")
    ap.add_argument("--write", action="store_true", help="Write baseline JSON")
    args = ap.parse_args()
    ok, msgs = run_golden_suite(args.baseline, write=args.write)
    if args.write:
        print("\n".join(msgs))
    else:
        if not ok:
            raise SystemExit("Golden diff:\n" + "\n".join(msgs))
        print("Golden OK")
