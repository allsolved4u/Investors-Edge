# ===== FILE: config/risk.py =====

from dataclasses import dataclass

@dataclass
class RiskParams:
    eq_mu: float = 0.065
    eq_sigma: float = 0.18
    fi_mu: float = 0.025
    fi_sigma: float = 0.06
    inf_mu: float = 0.02
    inf_sigma: float = 0.01
    rho_eq_fi: float = -0.15
    rho_eq_inf: float = 0.10
    rho_fi_inf: float = -0.20
