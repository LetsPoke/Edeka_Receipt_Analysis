import pdfplumber
import os
import re

from .fix_quantity_lines import fix_quantity_lines
from .item_parser import parse_item_line
from .kilo_parser import is_kilo_line, parse_kilo_line


def parse_receipt(pdf_path: str) -> dict:
    """ Extracts structured data from a PDF receipt """
    all_lines = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                for line in text.split("\n"):
                    all_lines.append(line.strip())

    return parse_lines(all_lines, pdf_path)


def remove_unwanted_items(items: list) -> list:
    """
    Removes any item whose 'name' field contains certain unwanted keywords
    (e.g. 'coupon', 'nummer', 'summe'). Returns a new filtered list.
    """
    # Define the keywords to exclude (make them all lowercase).
    exclude_keywords = ["coupon", "nummer:", "summe", "pfand", "Leergut", "positionsrabatt 50% -",
                        "positionsrabatt 30% -", "23% jahresstartrab. art. -", "23% jahresstartrab. -",
                        "leergut entl.allg. -", "leergut einweg allg. -"]

    filtered = []
    for item in items:
        name_lower = item["name"].lower()
        # Check if *any* exclude keyword is in the item name
        if any(keyword in name_lower for keyword in exclude_keywords):
            # Skip this item (don't add to filtered list)
            continue
        filtered.append(item)

    return filtered


def parse_lines(lines: list, pdf_path: str) -> dict:
    """ Extracts date/time, items, and sum from receipt lines """
    result = {
        "date": None,
        "time": None,
        "items": [],
        "sum": None,
        "file": os.path.basename(pdf_path)
    }

    collecting_items = False
    date_time_pattern = re.compile(r"(\d{2}\.\d{2}\.\d{2})\s+(\d{2}:\d{2})")

    for line in lines:
        # 1) Look for date/time
        dt_match = date_time_pattern.search(line)
        if dt_match:
            result["date"], result["time"] = dt_match.groups()

        # 2) If line starts with "EUR", start item collection
        if line.startswith("EUR"):
            collecting_items = True
            continue

        # 3) If we see "Posten", stop collecting items
        if "Posten" in line:
            collecting_items = False
            continue

        # 4) If we are collecting items, parse them
        if collecting_items:
            if is_kilo_line(line):
                parse_kilo_line(line, result["items"])
            else:
                item = parse_item_line(line)
                if item:
                    result["items"].append(item)

    # 5) merge any lines like "2 x" with the next item
    # because schema change is too difficult to detect, this is easier
    fix_quantity_lines(result["items"])

    # 6) Remove unwanted items (e.g. coupons, totals, etc.)
    result["items"] = remove_unwanted_items(result["items"])

    # 7) Compute sum of total_price from all items
    # because of 3 schemas it is easier to compute instead of read sum
    # its also cleaned without unwanted items
    total_sum = sum(item["total_price"] for item in result["items"])
    result["sum"] = round(total_sum, 2)

    return result
