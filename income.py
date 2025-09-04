# ===== FILE: income.py =====

def cpp_amount_this_year(amount_at_65: float, start_age: int, current_age: int, cpi_factor: float) -> float:
    if current_age < start_age:
        return 0.0
    adj = 1.0
    if start_age != 65:
        adj = 1 + 0.072 * (start_age - 65) if start_age > 65 else 1 - 0.072 * (65 - start_age)
    return amount_at_65 * adj * cpi_factor

def oas_amount_this_year(amount_at_65: float, start_age: int, current_age: int, cpi_factor: float) -> float:
    if current_age < start_age:
        return 0.0
    adj = 1.0
    if start_age != 65:
        adj = 1 + 0.072 * (start_age - 65) if start_age > 65 else 1 - 0.072 * (65 - start_age)
    return amount_at_65 * adj * cpi_factor
