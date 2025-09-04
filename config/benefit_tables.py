# ===== FILE: config/benefit_tables.py =====

from dataclasses import dataclass
from typing import Dict, Tuple

GIS_TYPES = ("single", "couple_both_oas", "couple_one_oas", "allowance_recipient")

@dataclass
class GISParams:
    max_annual: float
    reduction_rate: float
    exempt_amount: float = 0.0

@dataclass
class AllowanceParams:
    max_annual: float
    reduction_rate: float

@dataclass
class GSTParams:
    base_single: float
    base_couple: float
    per_child: float
    phaseout_rate: float
    threshold: float

GIS_TABLE_BY_YEAR: Dict[int, Dict[str, GISParams]] = {
    2024: {
        "single": GISParams(max_annual=11000, reduction_rate=0.50),
        "couple_both_oas": GISParams(max_annual=7000, reduction_rate=0.50),
        "couple_one_oas": GISParams(max_annual=11000, reduction_rate=0.25),
        "allowance_recipient": GISParams(max_annual=11000, reduction_rate=0.25),
    }
}

ALLOWANCE_BY_YEAR: Dict[int, AllowanceParams] = {
    2024: AllowanceParams(max_annual=11000, reduction_rate=0.25)
}

GST_TABLE_BY_YEAR: Dict[int, GSTParams] = {
    2024: GSTParams(
        base_single=496, base_couple=650, per_child=171,
        phaseout_rate=0.05, threshold=42000
    )
}

PROV_SENIOR_SUPP_BY_YEAR: Dict[int, Dict[str, Tuple[float, float, float]]] = {}
