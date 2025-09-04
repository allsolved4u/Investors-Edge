# ===== FILE: scripts/charts.py =====

import os
import argparse
import matplotlib.pyplot as plt

from models import Household, PersonProfile, AccountBalances, IncomeBreakdown
from simulator import simulate
from reporting import plot_balances, plot_cashflow, to_rows
from reporting_mtr import marginal_tax_curve


def build_demo_household():
    return Household(
        person1=PersonProfile(
            name="You", age=60, province="AB", retirement_age=65,
            balances=AccountBalances(rrsp=800000, tfsa=150000, non_reg_mv=250000, non_reg_acb=200000),
            employment_income=120000, savings_rate=0.15
        ),
        person2=None,
        annual_expenses=80000
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", type=int, default=35)
    ap.add_argument("--start-year", type=int, default=2024)
    ap.add_argument("--outdir", default="artifacts")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    hh = build_demo_household()
    results = simulate(hh, years=args.years, start_year=args.start_year)
    path = results if isinstance(results, list) else results[0]

    # Balances chart
    fig_bal = plot_balances(path, title="Account balances")
    fig_bal.savefig(os.path.join(args.outdir, "balances.png"), dpi=150)

    # Cash flow chart
    fig_cf = plot_cashflow(path, title="Net cash flow")
    fig_cf.savefig(os.path.join(args.outdir, "cashflow.png"), dpi=150)

    # Marginal tax rate curve
    base_inc = IncomeBreakdown(rrif=40000, cpp=14000, oas=9000, interest=2000, eligible_dividends=3000)
    curve = marginal_tax_curve(province="AB", age=68, year=args.start_year, base_inc=base_inc,
                               bumps=[1000, 2000, 5000, 10000])

    xs = [c["bump"] for c in curve]
    ys = [c["marginal_rate"] * 100 for c in curve]
    plt.figure()
    plt.plot(xs, ys, marker="o")
    plt.title("Marginal tax rate curve")
    plt.xlabel("Income bump ($)")
    plt.ylabel("MTR (%)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(args.outdir, "mtr_curve.png"), dpi=150)


if __name__ == "__main__":
    main()
