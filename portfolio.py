# ===== FILE: portfolio.py =====

from dataclasses import dataclass
from config.assumptions import RRIF_MIN_WITHDRAWAL_RATES

@dataclass
class RRSPAccount:
    balance: float
    def withdraw(self, amount: float) -> float:
        amt = min(amount, self.balance)
        self.balance -= amt
        return amt
    def grow(self, returns) -> None:
        self.balance *= (1 + returns.total_return)

@dataclass
class TFSAAccount:
    balance: float
    def withdraw(self, amount: float) -> float:
        amt = min(amount, self.balance)
        self.balance -= amt
        return amt
    def grow(self, returns) -> None:
        self.balance *= (1 + returns.total_return)

@dataclass
class NonRegisteredAccount:
    mv: float
    acb: float
    def withdraw(self, amount: float):
        amt = min(amount, self.mv)
        gain_ratio = 0.0
        if self.mv > 0:
            gain_ratio = max(0.0, (self.mv - self.acb) / self.mv)
        realized_gain = amt * gain_ratio
        self.mv -= amt
        self.acb -= amt * (1 - gain_ratio)
        return amt, realized_gain
    def grow(self, returns) -> None:
        self.mv *= (1 + returns.total_return)
    def yields(self, returns):
        interest = self.mv * returns.interest_yield
        elig_div = self.mv * returns.elig_dividend_yield
        nonelig_div = self.mv * returns.nonelig_dividend_yield
        return interest, elig_div, nonelig_div
    def add_to_acb(self, amount: float):
        self.mv += amount
        self.acb += amount

def rrif_minimum_withdrawal(age: int, balance: float) -> float:
    rate = RRIF_MIN_WITHDRAWAL_RATES.get(age, RRIF_MIN_WITHDRAWAL_RATES[max(RRIF_MIN_WITHDRAWAL_RATES)])
    return balance * rate
