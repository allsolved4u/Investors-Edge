# ===== FILE: reporting.py =====

from typing import List, Dict, Any
import matplotlib.pyplot as plt

from models import YearResult

def to_rows(results: List[YearResult]) -> List[Dict[str, Any]]:
    rows = []
    for r in results:
        row = {
            "year_idx": r.year_index,
            "age1": r.age1,
            "age2": r.age2,
            "taxes_total": r.taxes_total,
            "net_cash_flow": r.net_cash_flow,
            "p1_rrsp": r.balances_p1.rrsp,
            "p1_tfsa": r.balances_p1.tfsa,
            "p1_nonreg": r.balances_p1.non_reg_mv,
        }
        if r.balances_p2:
            row.update({
                "p2_rrsp": r.balances_p2.rrsp,
                "p2_tfsa": r.balances_p2.tfsa,
                "p2_nonreg": r.balances_p2.non_reg_mv
            })
        rows.append(row)
    return rows

def summarize(results: List[YearResult]) -> Dict[str, float]:
    last = results[-1]
    total_bal = last.balances_p1.rrsp + last.balances_p1.tfsa + last.balances_p1.non_reg_mv
    if last.balances_p2:
        total_bal += last.balances_p2.rrsp + last.balances_p2.tfsa + last.balances_p2.non_reg_mv
    return {
        "ending_assets": total_bal,
        "avg_taxes": sum(r.taxes_total for r in results) / max(1, len(results)),
        "min_net_cash_flow": min(r.net_cash_flow for r in results),
        "max_net_cash_flow": max(r.net_cash_flow for r in results),
    }

def plot_balances(results: List[YearResult], title="Account balances"):
    years = [r.year_index for r in results]
    p1_rrsp = [r.balances_p1.rrsp for r in results]
    p1_tfsa = [r.balances_p1.tfsa for r in results]
    p1_nonreg = [r.balances_p1.non_reg_mv for r in results]

    plt.figure()
    plt.stackplot(years, p1_rrsp, p1_tfsa, p1_nonreg, labels=["RRSP", "TFSA", "Non-reg"])
    if results[0].balances_p2:
        p2_rrsp = [r.balances_p2.rrsp for r in results]
        p2_tfsa = [r.balances_p2.tfsa for r in results]
        p2_nonreg = [r.balances_p2.non_reg_mv for r in results]
        plt.stackplot(years, p2_rrsp, p2_tfsa, p2_nonreg, labels=["P2 RRSP", "P2 TFSA", "P2 Non-reg"], alpha=0.5)
    plt.title(title)
    plt.xlabel("Year")
    plt.ylabel("Balance ($)")
    plt.legend(loc="upper left")
    plt.tight_layout()
    return plt.gcf()

def plot_cashflow(results: List[YearResult], title="Net cash flow"):
    years = [r.year_index for r in results]
    ncf = [r.net_cash_flow for r in results]

    plt.figure()
    plt.plot(years, ncf, marker="o")
    plt.axhline(0, color="gray", linewidth=1)
    plt.title(title)
    plt.xlabel("Year")
    plt.ylabel("Net cash flow ($)")
    plt.tight_layout()
    return plt.gcf()
