import re


def is_kilo_line(line: str) -> bool:
    """
    Checks if line contains weight-based pricing
    e.g. "0,480 kg x 2,99 /kg"
    """
    pattern = re.compile(r"^[\d,]+\s*kg\s*x\s*[\d,]+\s*/kg", re.IGNORECASE)
    return bool(pattern.search(line))


def parse_kilo_line(line: str, items: list):
    """ Parses weight-based items """
    if not items:
        return

    pattern = re.compile(r"^([\d,]+)\s*kg\s*x\s*([\d,]+)\s*/kg", re.IGNORECASE)
    match = pattern.search(line)

    if match:
        weight = float(match.group(1).replace(",", "."))
        kg_price = float(match.group(2).replace(",", "."))
        total = round(weight * kg_price, 2)

        last_item = items[-1]
        last_item["quantity"] = weight
        last_item["unit_price"] = kg_price
        last_item["total_price"] = total
