import os
import re
import json
import pdfplumber


def parse_receipt(pdf_path: str) -> dict:
    """
    Opens a multi-page PDF, collects all text lines,
    and parses them into a single receipt dictionary:
      {
        "date": "...",
        "time": "...",
        "items": [...],
        "summe": float,
        "file": pdf_path
      }
    """
    all_lines = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                for line in text.split("\n"):
                    line = line.strip()
                    all_lines.append(line)

    return parse_lines(all_lines)


def parse_lines(lines: list) -> dict:
    """
    Extracts from all lines:
      - date/time
      - list of items (name, quantity, unit_price, total_price)
      - summe (final total)
    """
    result = {
        "date": None,
        "time": None,
        "items": [],
        "summe": None
    }

    collecting_items = False

    sum_pattern = re.compile(r"SUMME\s*€\s*([\d,]+)")
    date_time_pattern = re.compile(r"(\d{2}\.\d{2}\.\d{2})\s+(\d{2}:\d{2})")

    for idx, line in enumerate(lines):
        # 1) Look for date/time
        dt_match = date_time_pattern.search(line)
        if dt_match:
            result["date"] = dt_match.group(1)
            result["time"] = dt_match.group(2)

        # 2) If we see "SUMME", stop collecting items
        if "SUMME" in line:
            collecting_items = False
            m_sum = sum_pattern.search(line)
            if m_sum:
                result["summe"] = float(m_sum.group(1).replace(",", "."))
            continue

        # 3) If line starts with "EUR", start item collection
        if line.startswith("EUR"):
            collecting_items = True
            continue

        # 4) If we are collecting items, handle each line
        if collecting_items:
            # Skip certain lines
            lines_to_skip = ["Posten", "Coupon", "Positionsrabatt", "Summe", "Nummer:"]
            if any(skip in line for skip in lines_to_skip):
                continue

            # Check if it's a "kilo line" like "0,480 kg x 2,99 /kg"
            if is_kilo_line(line):
                parse_kilo_line(line, result["items"])
                continue

            # Otherwise, parse it as a normal item
            item = parse_item_line(line)
            if not item:
                # parse_item_line returned {} => skip
                continue

            result["items"].append(item)

    return result


def is_kilo_line(line: str) -> bool:
    """
    e.g. "0,480 kg x 2,99 /kg"
    """
    pattern = re.compile(r"^[\d,]+\s*kg\s*x\s*[\d,]+\s*/kg", re.IGNORECASE)
    return bool(pattern.search(line))


def parse_kilo_line(line: str, items: list):
    """
    e.g. "0,480 kg x 2,99 /kg"
    Convert last item from quantity=1 => quantity=0.48, unit_price=2.99, etc.
    """
    if not items:
        return

    pattern = re.compile(r"^([\d,]+)\s*kg\s*x\s*([\d,]+)\s*/kg", re.IGNORECASE)
    m = pattern.search(line)
    if m:
        weight_str = m.group(1)
        kg_price_str = m.group(2)
        weight_val = float(weight_str.replace(",", "."))
        kg_price_val = float(kg_price_str.replace(",", "."))

        total = round(weight_val * kg_price_val, 2)

        last_item = items[-1]
        last_item["quantity"] = weight_val
        last_item["unit_price"] = kg_price_val
        last_item["total_price"] = total


def parse_item_line(line: str) -> dict:
    """
    Parses a line into {name, quantity, unit_price, total_price},
    handling old vs new receipt styles (ö -> oe, uppercase->mixed).
    Also skip lines like "4 x" if you want to avoid them as separate items.
    """
    # If the line is just "4 x" or "2 x" with no price, skip it
    # Todo: add quantity to the item name (schema changed 2023-02-22) we can handle new but not old schema
    if re.match(r"^\d+\s*x\s*$", line):
        return {}

    # 1) Extract the final price (e.g. "1,95 B" => "1,95")
    total_price_pattern = re.compile(r"([\d,]+)\s*(?:[A-Z]+|\*?[A-Z]+)?$")
    m_total = total_price_pattern.search(line)
    if not m_total:
        return {}

    total_str = m_total.group(1)
    total_val = float(total_str.replace(",", "."))
    line_clean = line[:m_total.start()].strip()

    # 2) Pattern for e.g. "GURKEN 0,49 € x 4"
    # => group(2)=0,49, group(3)=4
    # We allow optional "EUR" or "€"
    # Or older style might just be "GURKEN 0,49 x 4"
    pattern_price_qty = re.compile(
        r"(.*?)([\d,]+)\s*(?:EUR|€)?\s*x\s*(\d+)(.*)",
        re.IGNORECASE
    )
    mq = pattern_price_qty.search(line_clean)

    item = {
        "name": cleanup_name(line_clean),
        "quantity": 1,
        "unit_price": total_val,
        "total_price": total_val
    }

    if mq:
        pre_text, price_str, qty_str, post_text = mq.groups()
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

            # If there's a mismatch, recalc unit_price
            computed = round(unit_price_val * quantity_val, 2)
            if quantity_val == 0:
                item["quantity"] = 1
                item["unit_price"] = total_val
            else:
                if abs(computed - round(total_val, 2)) > 0.01:
                    item["unit_price"] = round(total_val / quantity_val, 2)
    else:
        # 4) No "x" pattern found => quantity=1, unit_price= total_price
        item["name"] = cleanup_name(item["name"])

    return item


def cleanup_name(raw_name: str) -> str:
    """
    1) Convert to a consistent case (e.g. lower).
    2) Replace 'ö'->'oe', 'ü'->'ue', 'ä'->'ae'.
    3) Convert to Title-case or keep lower.
    4) Remove extra spaces, skip lines like '4 x' if you want to do it here.
    """
    # Make everything lowercase
    name = raw_name.lower()

    # Replace 'oe' => 'ö' and 'ue' => 'ü'
    name = name.replace("ö", "oe").replace("ü", "ue").replace("ä", "ae")

    # Convert to Title-case, so "ehl möhren" => "Ehl Möhren"
    name = name.title()

    # Remove superfluous spaces
    name = " ".join(name.split())

    return name


def main():
    output_folder = os.path.join("output", "autogenerated")
    os.makedirs(output_folder, exist_ok=True)

    json_output_path = os.path.join(output_folder, "parsed_receipts.json")

    folder = "receipts/pdfs/"
    all_data = []

    for filename in os.listdir(folder):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(folder, filename)
            parsed = parse_receipt(pdf_path)
            parsed["file"] = filename
            all_data.append(parsed)

    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)

    print(f"Parsing complete. {len(all_data)} PDFs processed.")
    print(f"Results saved to: {json_output_path}")


if __name__ == "__main__":
    main()
