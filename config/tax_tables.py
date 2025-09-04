# ===== FILE: config/tax_tables.py =====

from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Bracket:
    up_to: float
    rate: float

@dataclass
class CreditScheme:
    basic_personal_amount: float
    credit_rate: float
    age_amount_base: float
    age_amount_threshold: float
    age_amount_reduction_rate: float
    pension_amount_max: float
    eligible_dividend_credit_rate: float
    non_eligible_dividend_credit_rate: float

@dataclass
class DividendParams:
    eligible_gross_up: float
    non_eligible_gross_up: float

@dataclass
class CapitalGainsParams:
    base_inclusion_rate: float
    alt_inclusion_rate: float
    alt_threshold_individual: float  # 0 to disable

@dataclass
class SurtaxRule:
    threshold_on_tax: float
    rate: float

@dataclass
class HealthPremiumBand:
    income_from: float
    income_to: float
    premium: float

@dataclass
class ProvinceRules:
    code: str
    brackets: List[Bracket]
    credits: CreditScheme
    surtaxes: List[SurtaxRule]
    health_premium_bands: List[HealthPremiumBand]
    quebec_abatement_rate: float = 0.0
    quebec_abatement_mode: str = "on_basic_after_credits"
    apply_surtax_before_health_premium: bool = True

@dataclass
class FederalRules:
    brackets: List[Bracket]
    credits: CreditScheme
    dividends: DividendParams
    capital_gains: CapitalGainsParams
    oas_recovery_threshold: float
    oas_recovery_rate: float

# -------------------------
# Federal 2024 example
# -------------------------
FEDERAL_2024 = FederalRules(
    brackets=[
        Bracket(53359, 0.15),
        Bracket(106717, 0.205),
        Bracket(165430, 0.26),
        Bracket(235675, 0.29),
        Bracket(float("inf"), 0.33),
    ],
    credits=CreditScheme(
        basic_personal_amount=15000,
        credit_rate=0.15,
        age_amount_base=8000,
        age_amount_threshold=42430,
        age_amount_reduction_rate=0.15,
        pension_amount_max=2000,
        eligible_dividend_credit_rate=0.150198,
        non_eligible_dividend_credit_rate=0.090301,
    ),
    dividends=DividendParams(
        eligible_gross_up=0.38,
        non_eligible_gross_up=0.15,
    ),
    capital_gains=CapitalGainsParams(
        base_inclusion_rate=0.50,
        alt_inclusion_rate=0.6667,
        alt_threshold_individual=250000,
    ),
    oas_recovery_threshold=90997,
    oas_recovery_rate=0.15,
)

# -------------------------
# Example provincial rules (AB, ON, BC, QC shown; add others as needed)
# -------------------------
AB_2024 = ProvinceRules(
    code="AB",
    brackets=[
        Bracket(14869, 0.10),
        Bracket(104000, 0.12),
        Bracket(209952, 0.13),
        Bracket(314928, 0.14),
        Bracket(float("inf"), 0.15),
    ],
    credits=CreditScheme(
        basic_personal_amount=21000,
        credit_rate=0.10,
        age_amount_base=5000,
        age_amount_threshold=43600,
        age_amount_reduction_rate=0.15,
        pension_amount_max=1500,
        eligible_dividend_credit_rate=0.08,
        non_eligible_dividend_credit_rate=0.02,
    ),
    surtaxes=[],
    health_premium_bands=[]
)

ON_2024 = ProvinceRules(
    code="ON",
    brackets=[
        Bracket(49231, 0.0505),
        Bracket(98463, 0.0915),
        Bracket(150000, 0.1116),
        Bracket(220000, 0.1216),
        Bracket(float("inf"), 0.1316),
    ],
    credits=CreditScheme(
        basic_personal_amount=11871,
        credit_rate=0.0505,
        age_amount_base=5650,
        age_amount_threshold=42000,
        age_amount_reduction_rate=0.15,
        pension_amount_max=1500,
        eligible_dividend_credit_rate=0.10,
        non_eligible_dividend_credit_rate=0.02,
    ),
    surtaxes=[
        SurtaxRule(5100, 0.20),
        SurtaxRule(6600, 0.36),
    ],
    health_premium_bands=[
        HealthPremiumBand(0, 20000, 0),
        HealthPremiumBand(20000, 36000, 300),
        HealthPremiumBand(36000, 48000, 450),
        HealthPremiumBand(48000, 72000, 600),
        HealthPremiumBand(72000, 200000, 750),
        HealthPremiumBand(200000, float("inf"), 900),
    ],
    apply_surtax_before_health_premium=True
)

BC_2024 = ProvinceRules(
    code="BC",
    brackets=[
        Bracket(45654, 0.0506),
        Bracket(91310, 0.077),
        Bracket(104835, 0.105),
        Bracket(127299, 0.1229),
        Bracket(172602, 0.147),
        Bracket(240716, 0.168),
        Bracket(float("inf"), 0.205),
    ],
    credits=CreditScheme(
        basic_personal_amount=12184,
        credit_rate=0.0506,
        age_amount_base=5200,
        age_amount_threshold=39000,
        age_amount_reduction_rate=0.15,
        pension_amount_max=1500,
        eligible_dividend_credit_rate=0.07,
        non_eligible_dividend_credit_rate=0.016,
    ),
    surtaxes=[],
    health_premium_bands=[]
)

QC_2024 = ProvinceRules(
    code="QC",
    brackets=[
        Bracket(46295, 0.14),
        Bracket(92580, 0.19),
        Bracket(112655, 0.24),
        Bracket(float("inf"), 0.2575),
    ],
    credits=CreditScheme(
        basic_personal_amount=18000,
        credit_rate=0.14,
        age_amount_base=3400,
        age_amount_threshold=42000,
        age_amount_reduction_rate=0.15,
        pension_amount_max=2000,
        eligible_dividend_credit_rate=0.115,
        non_eligible_dividend_credit_rate=0.044,
    ),
    surtaxes=[],
    health_premium_bands=[],
    quebec_abatement_rate=0.165,
    quebec_abatement_mode="on_basic_after_credits"
)

# -------------------------
# Year-keyed registries
# -------------------------
FEDERAL_RULES_BY_YEAR: Dict[int, FederalRules] = {2024: FEDERAL_2024}

PROVINCIAL_RULES_BY_YEAR: Dict[int, Dict[str, ProvinceRules]] = {
    2024: {
        "AB": AB_2024,
        "ON": ON_2024,
        "BC": BC_2024,
        "QC": QC_2024,
        # Add other provinces/territories here...
    }
}
