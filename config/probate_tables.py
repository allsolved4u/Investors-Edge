# ===== FILE: config/probate_tables.py =====

from typing import Dict

# Approximate probate / estate administration fee models by province/territory.
# Each entry has:
#   "bands": list of (cap, rate) tuples in ascending order of cap
#   "fixed": flat fee added regardless of estate size
# Rates are expressed as decimals (e.g., 0.015 = 1.5%).
# Caps are absolute dollar amounts; use float("inf") for no upper bound.

PROBATE_MODELS: Dict[str, Dict] = {
    "ON": {"bands": [(50000, 0.0), (float("inf"), 0.015)], "fixed": 0.0},
    "BC": {"bands": [(25000, 0.0), (50000, 0.006), (float("inf"), 0.014)], "fixed": 0.0},
    "AB": {"bands": [(float("inf"), 0.0)], "fixed": 525.0},  # flat court fee
    "SK": {"bands": [(float("inf"), 0.007)], "fixed": 0.0},
    "MB": {"bands": [(float("inf"), 0.007)], "fixed": 0.0},
    "NB": {"bands": [(float("inf"), 0.005)], "fixed": 0.0},
    "NS": {"bands": [(50000, 0.0), (100000, 0.014), (250000, 0.0145), (float("inf"), 0.016)], "fixed": 0.0},
    "PE": {"bands": [(float("inf"), 0.004)], "fixed": 0.0},
    "NL": {"bands": [(float("inf"), 0.006)], "fixed": 0.0},
    "QC": {"bands": [(float("inf"), 0.0)], "fixed": 0.0},  # notary fees; probate often not applicable
    "YT": {"bands": [(float("inf"), 0.0)], "fixed": 0.0},
    "NT": {"bands": [(float("inf"), 0.0)], "fixed": 0.0},
    "NU": {"bands": [(float("inf"), 0.0)], "fixed": 0.0},
}

def compute_probate_fees(province: str, estate_gross: float) -> float:
    """
    Compute approximate probate/estate administration fees for a given province and estate value.
    estate_gross: total gross estate value (before debts, taxes, etc.)
    """
    model = PROBATE_MODELS.get(province, {"bands": [(float("inf"), 0.0)], "fixed": 0.0})
    remaining = estate_gross
    last_cap = 0.0
    fees = model["fixed"]
    for cap, rate in model["bands"]:
        span = min(remaining, cap - last_cap)
        if span > 0:
            fees += span * rate
            remaining -= span
            last_cap = cap
        if remaining <= 0:
            break
    return max(0.0, fees)
