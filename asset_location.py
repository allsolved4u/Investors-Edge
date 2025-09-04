# ===== FILE: asset_location.py =====

from dataclasses import dataclass
from typing import Tuple
from config.fees import FeePolicy, AssetPolicy

@dataclass
class AccountReturns:
    rrsp_total: float
    tfsa_total: float
    nonreg_total: float
    advisory_cash_cost: float

def _net_asset_returns(eq_gross: float, fi_gross: float, mer_eq: float, mer_fi: float) -> Tuple[float, float]:
    return eq_gross - mer_eq, fi_gross - mer_fi

def _apply_foreign_wht_on_div_yield(eq_total_return: float, div_yield: float, wht: float) -> float:
    return eq_total_return - div_yield * wht

def compute_effective_account_returns(
    rrsp_balance: float,
    tfsa_balance: float,
    nonreg_balance: float,
    equity_return: float,
    fixed_return: float,
    dividend_yield_equity: float,
    fee: FeePolicy,
    ap: AssetPolicy
) -> AccountReturns:
    total = rrsp_balance + tfsa_balance + nonreg_balance
    if total <= 0:
        return AccountReturns(0.0, 0.0, 0.0, 0.0)

    target_equity_mv = ap.target_equity_weight * total
    target_fixed_mv = (1 - ap.target_equity_weight) * total

    fixed_rrsp = min(target_fixed_mv, rrsp_balance)
    rem_fixed = target_fixed_mv - fixed_rrsp
    fixed_tfsa = min(max(0.0, rem_fixed), tfsa_balance)
    rem_fixed = target_fixed_mv - fixed_rrsp - fixed_tfsa
    fixed_nonreg = max(0.0, rem_fixed)

    eq_rrsp = max(0.0, rrsp_balance - fixed_rrsp)
    eq_tfsa = max(0.0, tfsa_balance - fixed_tfsa)
    eq_nonreg = max(0.0, nonreg_balance - fixed_nonreg)

    eq_net, fi_net = _net_asset_returns(equity_return, fixed_return, fee.mer_equity, fee.mer_fixed)

    foreign_share = ap.foreign_equity_share
    rrsp_eq_ret = _apply_foreign_wht_on_div_yield(eq_net, dividend_yield_equity * foreign_share, fee.wht_foreign_div_rrsp)
    tfsa_eq_ret = _apply_foreign_wht_on_div_yield(eq_net, dividend_yield_equity * foreign_share, fee.wht_foreign_div_tfsa)
    nonreg_eq_ret = _apply_foreign_wht_on_div_yield(eq_net, dividend_yield_equity * foreign_share, fee.wht_foreign_div_nonreg)

    rrsp_total_ret = (eq_rrsp * rrsp_eq_ret + fixed_rrsp * fi_net) / rrsp_balance if rrsp_balance > 0 else 0.0
    tfsa_total_ret = (eq_tfsa * tfsa_eq_ret + fixed_tfsa * fi_net) / tfsa_balance if tfsa_balance > 0 else 0.0
    nonreg_total_ret = (eq_nonreg * nonreg_eq_ret + fixed_nonreg * fi_net) / nonreg_balance if nonreg_balance > 0 else 0.0

    advisory_cash = fee.advisory_fee * total

    return AccountReturns(
        rrsp_total=rrsp_total_ret,
        tfsa_total=tfsa_total_ret,
        nonreg_total=nonreg_total_ret,
        advisory_cash_cost=advisory_cash
    )
