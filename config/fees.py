# ===== FILE: config/fees.py =====

from dataclasses import dataclass

@dataclass
class FeePolicy:
    mer_equity: float = 0.20 / 100.0
    mer_fixed: float  = 0.10 / 100.0
    advisory_fee: float = 0.60 / 100.0
    wht_foreign_div_rrsp: float = 0.00
    wht_foreign_div_tfsa: float = 0.15
    wht_foreign_div_nonreg: float = 0.00

@dataclass
class AssetPolicy:
    target_equity_weight: float = 0.60
    foreign_equity_share: float = 0.50
    prioritize_fixed_in_registered: bool = True
