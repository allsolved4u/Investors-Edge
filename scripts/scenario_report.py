# ===== FILE: scripts/scenario_report.py =====

import os
import json
import argparse
from copy import deepcopy

from models import Household, PersonProfile, AccountBalances
from scenarios import Scenario, run_scenarios, tweak_retire_age, tweak_cpp_oas
from reporting import summarize, to_rows
from mc import run_mc
from simulator import simulate


def build_base() -> Household:
    p1 = PersonProfile(
        name="You", age=60, province="AB", retirement_age=65,
        balances=AccountBalances(rrsp=900000, tfsa=120000, non_reg_mv=200000, non_reg_acb=160000),
        employment_income=140000, savings_rate=0.18
    )
    p2 = PersonProfile(
        name="Spouse", age=58, province="AB", retirement_age=65,
        balances=AccountBalances(rrsp=350000, tfsa=80000, non_reg_mv=50000, non_reg_acb=45000),
        employment_income=80000, savings_rate=0.12
    )
    return Household(person1=p1, person2=p2, annual_expenses=90000)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", type=int, default=35)
    ap.add_argument("--start-year", type=int, default=2024)
    ap.add_argument("--mc-runs", type=int, default=500)
    ap.add_argument("--outdir", default="artifacts")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    base = build_base()
    scenarios = [
        Scenario(name="Retire@65_CPP/OAS@65", tweak=tweak_retire_age(65), sim_years=args.years),
        Scenario(name="Retire@60_CPP/OAS@65", tweak=tweak_retire_age(60), sim_years=args.years),
        Scenario(name="Retire@65_CPP@70_OAS@70",
                 tweak=lambda h: tweak_cpp_oas(70, 70)(tweak_retire_age(65)(h)), sim_years=args.years),
    ]

    runs = run_scenarios(base, scenarios, start_year=args.start_year)

    comparison = {}
    for name, path in runs.items():
        results = path if isinstance(path, list) else path[0]
        summary = summarize(results)

        # True MC: vary seed and call simulate each run
        mc_stats = run_mc(sim_fn=lambda hh, **kw: simulate(hh, years=args.years, start_year=args.start_year),
                          runs=args.mc_runs, hh=build_base())

        comparison[name] = {
            "ending_assets": summary["ending_assets"],
            "avg_taxes": summary["avg_taxes"],
            "min_net_cash_flow": summary["min_net_cash_flow"],
            "max_net_cash_flow": summary["max_net_cash_flow"],
            "prob_depletion": mc_stats["prob_depletion"],
            "estate_p50": mc_stats["estate_p50"],
            "estate_p10": mc_stats["estate_p10"],
            "estate_p90": mc_stats["estate_p90"],
        }

        # Export per-year rows to CSV
        try:
            import csv
            rows = to_rows(results)
            with open(os.path.join(args.outdir, f"{name}_path.csv"), "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                w.writeheader()
                w.writerows(rows)
        except Exception:
            pass

    with open(os.path.join(args.outdir, "scenario_comparison.json"), "w") as f:
        json.dump(comparison, f, indent=2)

    print(json.dumps(comparison, indent=2))


if __name__ == "__main__":
    main()
