# ===== FILE: asset_allocation.py =====

from dataclasses import dataclass

@dataclass
class GlidePath:
    start_equity_w: float = 0.80
    end_equity_w: float = 0.40
    end_equity_w_late: float = 0.40
    anchor_age: int = 45
    retire_age: int = 65

    def equity_weight(self, age: int) -> float:
        if age <= self.anchor_age:
            return self.start_equity_w
        if age >= self.retire_age:
            return self.end_equity_w_late
        span = max(1, self.retire_age - self.anchor_age)
        t = (age - self.anchor_age) / span
        return self.start_equity_w + t * (self.end_equity_w - self.start_equity_w)

def blended_return(equity_w: float, equity_return: float, fixed_return: float) -> float:
    return equity_w * equity_return + (1 - equity_w) * fixed_return

def blended_returns_for_person(age: int, glide: GlidePath, equity_return: float, fixed_return: float) -> float:
    eq_w = glide.equity_weight(age)
    return blended_return(eq_w, equity_return, fixed_return)
