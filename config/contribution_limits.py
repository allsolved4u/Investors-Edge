# ===== FILE: config/contribution_limits.py =====

from typing import Dict, Optional

RRSP_DOLLAR_LIMIT_BY_YEAR: Dict[int, float] = {
    2022: 29910,
    2023: 31150,
    2024: 31560,
    2025: 32490,
}

TFSA_ROOM_BY_YEAR: Dict[int, float] = {
    2009: 5000, 2010: 5000, 2011: 5000, 2012: 5000,
    2013: 5500, 2014: 5500, 2015: 10000,
    2016: 5500, 2017: 5500, 2018: 5500,
    2019: 6000, 2020: 6000, 2021: 6000, 2022: 6000,
    2023: 6500, 2024: 7000, 2025: 7000
}

def rrsp_dollar_limit(year: int) -> float:
    y = year
    while y >= min(RRSP_DOLLAR_LIMIT_BY_YEAR):
        if y in RRSP_DOLLAR_LIMIT_BY_YEAR:
            return RRSP_DOLLAR_LIMIT_BY_YEAR[y]
        y -= 1
    return RRSP_DOLLAR_LIMIT_BY_YEAR[max(RRSP_DOLLAR_LIMIT_BY_YEAR)]

def tfsa_annual_room(year: int) -> float:
    y = year
    while y >= min(TFSA_ROOM_BY_YEAR):
        if y in TFSA_ROOM_BY_YEAR:
            return TFSA_ROOM_BY_YEAR[y]
        y -= 1
    return 0.0

def ensure_years(start: int, end: int, rrsp_growth: Optional[float] = None):
    if rrsp_growth:
        for y in range(start + 1, end + 1):
            if y not in RRSP_DOLLAR_LIMIT_BY_YEAR:
                RRSP_DOLLAR_LIMIT_BY_YEAR[y] = RRSP_DOLLAR_LIMIT_BY_YEAR[y - 1] * rrsp_growth
