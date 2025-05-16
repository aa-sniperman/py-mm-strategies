def format_units(value: int, decimals: int) -> float:
    return float(value / (10 ** decimals))