# ===== FILE: models.py =====

from dataclasses import dataclass, field
from typing import Optional, Dict, List

@dataclass
class AccountBalances:
    rrsp: float = 0.0
    tfsa: float = 0.0
    non_reg_mv: float = 0.0
    non_reg_acb: float = 0.0

@dataclass
class IncomeBreakdown:
    employment: float = 0.0
    interest: float = 0.0
    other_taxable: float = 0.0
    rrif: float = 0.0
    cpp: float = 0.0
    oas: float = 0.0
    pension_db: float = 0.0
    annuity_registered: float = 0.0
    eligible_dividends: float = 0.0
    non_eligible_dividends: float = 0.0
    capital_gains_realized: float = 0.0
    deductions: float = 0.0
    annuity_nonreg_taxable_interest: float = 0.0
    annuity_nonreg_cash: float = 0.0

@dataclass
class TaxResult:
    taxable_income: float
    federal_tax: float
    provincial_tax: float
    provincial_surtax: float
    health_premium: float
    oas_recovery_tax: float
    total_payable: float
    net_income: float
    details: Dict[str, float] = field(default_factory=dict)

@dataclass
class YearResult:
    year_index: int
    age1: int
    age2: Optional[int]
    split_fraction: float
    taxes_total: float
    net_cash_flow: float
    balances_p1: AccountBalances
    balances_p2: Optional[AccountBalances]
    notes: Dict[str, float] = field(default_factory=dict)

@dataclass
class PersonProfile:
    name: str
    age: int
    province: str
    retirement_age: int
    cpp_start_age: int = 65
    oas_start_age: int = 65
    cpp_amount_at_65: float = 14000.0
    oas_amount_at_65: float = 9000.0
    balances: AccountBalances = field(default_factory=AccountBalances)
    employment_income: float = 0.0
    wage_growth: float = 0.03
    savings_rate: float = 0.15
    pension_plan: str = "none"
    db_accrual_rate: float = 0.02
    dc_employee_rate: float = 0.05
    dc_employer_rate: float = 0.05
    pa_override: Optional[float] = None
    rrsp_room_carryforward: float = 0.0
    tfsa_room_carryforward: float = 0.0
    tfsa_recontribution_next_year: float = 0.0
    mortality: Optional[object] = None
    survivor_policy: Optional[object] = None
    annuities: List[object] = field(default_factory=list)
    cpp_sharing_enabled: bool = False
    cpp_share_fraction: float = 0.5
    cpp_prb_enabled: bool = False
    cpp_prb_accrual_rate: float = 0.01
    cpp_prb_carry: float = 0.0
    db_pension: Optional[object] = None

@dataclass
class Household:
    person1: PersonProfile
    person2: Optional[PersonProfile] = None
    annual_expenses: float = 60000.0
