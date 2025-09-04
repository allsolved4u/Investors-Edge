# ===== FILE: risk_model.py =====

from dataclasses import dataclass
from typing import List
import numpy as np
from config.risk import RiskParams

@dataclass
class YearMarket:
    equity_return: float
    fixed_return: float
    inflation: float

def generate_market_path(years: int, seed: int, rp: RiskParams) -> List[YearMarket]:
    rng = np.random.default_rng(seed)
    mu = np.array([rp.eq_mu, rp.fi_mu, rp.inf_mu])
    sigma = np.array([rp.eq_sigma, rp.fi_sigma, rp.inf_sigma])
    corr = np.array([
        [1.0,           rp.rho_eq_fi, rp.rho_eq_inf],
        [rp.rho_eq_fi,  1.0,          rp.rho_fi_inf],
        [rp.rho_eq_inf, rp.rho_fi_inf, 1.0]
    ])
    cov = np.outer(sigma, sigma) * corr
    L = np.linalg.cholesky(cov)

    z = rng.standard_normal(size=(years, 3))
    draws = z @ L.T + mu

    out = []
    for t in range(years):
        eq, fi, inf = draws[t]
        out.append(YearMarket(equity_return=eq, fixed_return=fi, inflation=max(-0.05, inf)))
    return out
