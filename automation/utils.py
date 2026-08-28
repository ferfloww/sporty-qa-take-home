import re


def parse_number(text: str) -> float:
    """Pulls a number out of a string. '€1,234.50' -> 1234.5, '2.45' -> 2.45"""
    match = re.search(r"-?[\d,]+\.?\d*", text.replace(",", ""))
    if not match:
        raise ValueError(f"No number found in {text!r}")
    return float(match.group())
