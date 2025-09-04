# ===== FILE: taxes.py =====

from typing import Tuple
from models import IncomeBreakdown, TaxResult
from config.tax_tables import FEDERAL_RULES_BY_YEAR, PROVINCIAL_RULES_BY_YEAR

def _apply_brackets(amount: float, brackets) -> float:
    tax = 0.0
    remaining = amount
    last_cap = 0.0
    for b in brackets:
        span = min(remaining, b.up_to - last_cap)
        if span > 0:
            tax += span * b.rate
            remaining -= span
            last_cap = b.up_to
        if remaining <= 0:
            break
    return max(0.0, tax)

def _non_refundable_credit(value: float, rate: float) -> float:
    return max(0.0, value * rate)

def _dividend_gross_up_and_credits(inc: IncomeBreakdown, fed, prov):
    elig_grossed = inc.eligible_dividends * (1.0 + fed.dividends.eligible_gross_up)
    nonelig_grossed = inc.non_eligible_dividends * (1.0 + fed.dividends.non_eligible_gross_up)
    taxable_div = elig_grossed + nonelig_grossed
    fed_credit = elig_grossed * fed.credits.eligible_dividend_credit_rate \
               + nonelig_grossed * fed.credits.non_eligible_dividend_credit_rate
    prov_credit = elig_grossed * prov.credits.eligible_dividend_credit_rate \
                + nonelig_grossed * prov.credits.non_eligible_dividend_credit_rate
    return taxable_div, fed_credit, prov_credit

def _taxable_capital_gains(realized_total: float, fed) -> float:
    thr = fed.capital_gains.alt_threshold_individual
    if thr and realized_total > thr:
        base = thr
        above = realized_total - thr
        return base * fed.capital_gains.base_inclusion_rate + above * fed.capital_gains.alt_inclusion_rate
    return realized_total * fed.capital_gains.base_inclusion_rate

def _oas_recovery(net_income_before_credits: float, oas_received: float, fed) -> float:
    if oas_received <= 0:
        return 0.0
    excess = max(0.0, net_income_before_credits - fed.oas_recovery_threshold)
    return min(oas_received, excess * fed.oas_recovery_rate)

def _provincial_surtax_and_premiums(prov_tax_after_credits: float, taxable_income: float, prov):
    surtax = 0.0
    for s in prov.surtaxes:
        if prov_tax_after_credits > s.threshold_on_tax:
            surtax += (prov_tax_after_credits - s.threshold_on_tax) * s.rate
    premium = 0.0
    for band in prov.health_premium_bands:
        if band.income_from <= taxable_income < band.income_to:
            premium = band.premium
            break
    return surtax, premium

def compute_personal_tax(inc: IncomeBreakdown, province: str, age: int, year: int) -> TaxResult:
    fed = FEDERAL_RULES_BY_YEAR[year]
    prov_map = PROVINCIAL_RULES_BY_YEAR.get(year) or PROVINCIAL_RULES_BY_YEAR[max(PROVINCIAL_RULES_BY_YEAR)]
    prov = prov_map[province]

    taxable_div, fed_div_credit, prov_div_credit = _dividend_gross_up_and_credits(inc, fed, prov)
    taxable_gains = _taxable_capital_gains(inc.capital_gains_realized, fed)

    net_income = (
        inc.employment + inc.interest + inc.other_taxable +
        inc.rrif + inc.pension_db + inc.annuity_registered + inc.cpp + inc.oas +
        taxable_div + taxable_gains +
        inc.annuity_nonreg_taxable_interest
    ) - inc.deductions

    taxable_income = net_income

    fed_basic_tax = _apply_brackets(taxable_income, fed.brackets)
    fed_credits = _non_refundable_credit(fed.credits.basic_personal_amount, fed.credits.credit_rate)

    if age >= 65 and fed.credits.age_amount_base > 0:
        reduction = max(0.0, (net_income - fed.credits.age_amount_threshold) * fed.credits.age_amount_reduction_rate)
        age_amt = max(0.0, fed.credits.age_amount_base - reduction)
        fed_credits += _non_refundable_credit(age_amt, fed.credits.credit_rate)

    eligible_pension_credit = inc.pension_db + (inc.rrif + inc.annuity_registered if age >= 65 else 0.0)
    fed_credits += _non_refundable_credit(min(eligible_pension_credit, fed.credits.pension_amount_max), fed.credits.credit_rate)
    fed_credits += fed_div_credit

    qc_abatement = fed_basic_tax * prov.quebec_abatement_rate if prov.quebec_abatement_rate > 0 else 0.0
    fed_tax_after_credits = max(0.0, fed_basic_tax - fed_credits - qc_abatement)

    oas_rec = _oas_recovery(net_income, inc.oas, fed)

    prov_basic_tax = _apply_brackets(taxable_income, prov.brackets)
    prov_credits = _non_refundable_credit(prov.credits.basic_personal_amount, prov.credits.credit_rate)
    prov_credits += prov_div_credit
    prov_tax_after_credits = max(0.0, prov_basic_tax - prov_credits)
    prov_surtax, health_premium = _provincial_surtax_and_premiums(prov_tax_after_credits, taxable_income, prov)

    federal_tax = fed_tax_after_credits + oas_rec
    provincial_tax = prov_tax_after_credits
    total_payable = federal_tax + provincial_tax + prov_surtax + health_premium

    cash_income = (
        inc.employment + inc.interest + inc.other_taxable +
        inc.rrif + inc.pension_db + inc.annuity_registered + inc.cpp + inc.oas +
        (inc.eligible_dividends + inc.non_eligible_dividends) +
        inc.capital_gains_realized + inc.annuity_nonreg_cash
    )
    net_cash = cash_income - total_payable

    return TaxResult(
        taxable_income=taxable_income,
        federal_tax=federal_tax,
        provincial_tax=provincial_tax,
        provincial_surtax=prov_surtax,
        health_premium=health_premium,
        oas_recovery_tax=oas_rec,
        total_payable=total_payable,
        net_income=net_cash
    )
