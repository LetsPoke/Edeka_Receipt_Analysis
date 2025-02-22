import re
from .text_cleaner import cleanup_name


def parse_item_line(line: str) -> dict:
    """
    Parses a line into {name, quantity, unit_price, total_price},
    handling old vs. new receipt styles (ö -> oe, uppercase->mixed).
    Also skips lines like "4 x" if they contain no price.
    """
    # Skip lines that only contain "4 x", "2 x", etc. without a price
    # Todo: add quantity to the item name (schema changed 2023-02-22) we can handle new but not old schema
    if re.match(r"^\d+\s*x\s*$", line):
        return {}

    # 1) Extract the final price (e.g., "1,95 B" => "1,95")
    total_price_pattern = re.compile(r"([\d,]+)\s*(?:[A-Z]+|\*?[A-Z]+)?$")
    m_total = total_price_pattern.search(line)
    if not m_total:
        return {}

    total_str = m_total.group(1)
    total_val = float(total_str.replace(",", "."))  # Convert to float
    line_clean = line[:m_total.start()].strip()  # Remove the price part

    # 2) Detect "x" quantity patterns (e.g., "GURKEN 0,49 € x 4")
    pattern_price_qty = re.compile(
        r"(.*?)([\d,]+)\s*(?:EUR|€)?\s*x\s*(\d+)(.*)",
        re.IGNORECASE
    )
    match_qty = pattern_price_qty.search(line_clean)

    # Default item structure
    item = {
        "name": cleanup_name(line_clean),
        "quantity": 1,  # Default quantity is 1 if no "x" pattern is found
        "unit_price": total_val,
        "total_price": total_val
    }

    if match_qty:
        pre_text, price_str, qty_str, post_text = match_qty.groups()
        try:
            unit_price_val = float(price_str.replace(",", "."))
            quantity_val = int(qty_str)
        except ValueError:
            pass
        else:
            item["quantity"] = quantity_val
            item["unit_price"] = unit_price_val
            # Rebuild name from everything outside the pattern
            item["name"] = cleanup_name(pre_text + " " + post_text)
            item["total_price"] = total_val

            # If there's a mismatch, recalculate unit price
            computed = round(unit_price_val * quantity_val, 2)
            if quantity_val == 0:
                # If quantity is zero, assume it's an error and reset it to 1
                item["quantity"] = 1
                item["unit_price"] = total_val
            else:
                if abs(computed - round(total_val, 2)) > 0.01:
                    # Adjust unit price if necessary
                    item["unit_price"] = round(total_val / quantity_val, 2)
    else:
        # No "x" pattern found => quantity=1, unit_price = total_price
        item["name"] = cleanup_name(item["name"])

    return item
