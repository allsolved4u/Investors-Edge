# ===== FILE: estate.py =====

from dataclasses import dataclass, field
from typing import Dict
from models import IncomeBreakdown
from taxes import compute_personal_tax
from config.probate_tables import compute_probate_fees

@dataclass
class EstateSummary:
    year_of_final_death: int
    probate_fees: float
    terminal_taxes: float
    other_costs: float
    estate_gross: float
    estate_net: float
    details: Dict[str, float] = field(default_factory=dict)

def compute_terminal_taxes_and_estate(
    province: str,
    year: int,
    rrsp_balance: float,
    tfsa_balance: float,
    nonreg_mv: float,
    nonreg_acb: float,
    other_cash: float = 0.0,
    funeral_admin_fixed: float = 10000.0,
    probate_enabled: bool = True
) -> EstateSummary:
    realized_gain = max(0.0, nonreg_mv - nonreg_acb)
    inc = IncomeBreakdown(
        employment=0.0, interest=0.0, other_taxable=0.0, rrif=rrsp_balance,
        cpp=0.0, oas=0.0, pension_db=0.0, annuity_registered=0.0,
        eligible_dividends=0.0, non_eligible_dividends=0.0,
        capital_gains_realized=realized_gain, deductions=0.0,
        annuity_nonreg_taxable_interest=0.0, annuity_nonreg_cash=0.0
    )
    tax_result = compute_personal_tax(inc, province=province, age=90, year=year)
    terminal_taxes = tax_result.total_payable

    estate_gross = rrsp_balance + tfsa_balance + nonreg_mv + other_cash
    probate_fees = compute_probate_fees(province, estate_gross) if probate_enabled else 0.0
    estate_net = max(0.0, estate_gross - terminal_taxes - probate_fees - funeral_admin_fixed)

    return EstateSummary(
        year_of_final_death=year,
        probate_fees=probate_fees,
        terminal_taxes=terminal_taxes,
        other_costs=funeral_admin_fixed,
        estate_gross=estate_gross,
        estate_net=estate_net,
        details={
            "nonreg_realized_gain": realized_gain,
            "rrsp_included": rrsp_balance
        }
    )
