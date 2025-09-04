# ===== FILE: config/assumptions.py =====

from dataclasses import dataclass
from typing import Dict

@dataclass
class ReturnAssumptions:
    equity_return: float = 0.065
    fixed_income_return: float = 0.025
    inflation: float = 0.02
    interest_yield: float = 0.01
    elig_dividend_yield: float = 0.02
    nonelig_dividend_yield: float = 0.00
    reinvest_dividends: bool = False

@dataclass
class GovBenefitAssumptions:
    cpp_amount_at_65: float = 14000.0
    oas_amount_at_65: float = 9000.0

RRIF_MIN_WITHDRAWAL_RATES: Dict[int, float] = {
    55: 0.029, 56: 0.029, 57: 0.029, 58: 0.029, 59: 0.029,
    60: 0.031, 61: 0.033, 62: 0.035, 63: 0.038, 64: 0.041,
    65: 0.044, 66: 0.048, 67: 0.052, 68: 0.057, 69: 0.062,
    70: 0.068, 71: 0.0738, 72: 0.0754, 73: 0.0771, 74: 0.0788,
    75: 0.0806, 76: 0.0824, 77: 0.0843, 78: 0.0863, 79: 0.0883,
    80: 0.0904, 81: 0.0927, 82: 0.0951, 83: 0.0976, 84: 0.1003,
    85: 0.1031, 86: 0.1061, 87: 0.1093, 88: 0.1127, 89: 0.1163,
    90: 0.1202, 91: 0.1244, 92: 0.1289, 93: 0.1338, 94: 0.1393,
    95: 0.1512,
}

DEFAULT_RETURNS = ReturnAssumptions()
DEFAULT_GOV = GovBenefitAssumptions()
