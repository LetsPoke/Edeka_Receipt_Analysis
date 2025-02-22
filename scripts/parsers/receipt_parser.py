import pdfplumber
import os
import re
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


def parse_lines(lines: list, pdf_path: str) -> dict:
    """ Extracts date/time, items, and sum from receipt lines """
    result = {
        "date": None,
        "time": None,
        "items": [],
        "summe": None,
        "file": os.path.basename(pdf_path)
    }

    collecting_items = False
    sum_pattern = re.compile(r"SUMME\s*€\s*([\d,]+)")
    date_time_pattern = re.compile(r"(\d{2}\.\d{2}\.\d{2})\s+(\d{2}:\d{2})")

    # Define lines to skip
    skip_lines = ["Posten", "Coupon", "Positionsrabatt", "Summe", "Nummer:"]

    for line in lines:
        # 1) Skip unwanted lines
        if any(skip in line for skip in skip_lines):
            continue

        # 2) Look for date/time
        dt_match = date_time_pattern.search(line)
        if dt_match:
            result["date"], result["time"] = dt_match.groups()

        # 3) If we see "SUMME", stop collecting items
        if "SUMME" in line:
            collecting_items = False
            match = sum_pattern.search(line)
            if match:
                result["summe"] = float(match.group(1).replace(",", "."))
            continue

        # 4) If line starts with "EUR", start item collection
        if line.startswith("EUR"):
            collecting_items = True
            continue

        # 5) If we are collecting items, parse them
        if collecting_items:
            if is_kilo_line(line):
                parse_kilo_line(line, result["items"])
            else:
                item = parse_item_line(line)
                if item:
                    result["items"].append(item)

    return result
