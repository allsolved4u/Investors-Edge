# ===== FILE: mc.py =====

from typing import Callable, Dict, Any
import numpy as np

def run_mc(sim_fn: Callable, runs: int, *args, **kwargs) -> Dict[str, Any]:
    estates = []
    deplete_flags = []
    for i in range(runs):
        kw = dict(kwargs)
        if "seed" in kw:
            kw["seed"] = kw["seed"] + i * 17
        else:
            kw["seed"] = 42 + i * 17
        results = sim_fn(*args, **kw)
        if isinstance(results, tuple):
            path, estate = results
        else:
            path, estate = results, None

        last = path[-1]
        total_bal = last.balances_p1.rrsp + last.balances_p1.tfsa + last.balances_p1.non_reg_mv
        if last.balances_p2:
            total_bal += last.balances_p2.rrsp + last.balances_p2.tfsa + last.balances_p2.non_reg_mv

        deplete_flags.append(total_bal <= 0.0)
        estates.append(estate.estate_net if getattr(estate, "estate_net", None) is not None else total_bal)

    return {
        "prob_depletion": float(np.mean(deplete_flags)) if runs > 0 else 0.0,
        "estate_p50": float(np.median(estates)) if estates else 0.0,
        "estate_p10": float(np.percentile(estates, 10)) if len(estates) >= 10 else (estates[0] if estates else 0.0),
        "estate_p90": float(np.percentile(estates, 90)) if len(estates) >= 10 else (estates[-1] if estates else 0.0),
    }
