import os
import re
import json
import pdfplumber


def parse_receipt(pdf_path: str) -> dict:
    """
    Opens a multi-page PDF, collects all text lines in `all_lines`,
    and parses them into a single receipt dictionary of the form:
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

    # We interpret all collected lines as one single receipt.
    return parse_lines(all_lines)


def parse_lines(lines: list) -> dict:
    """
    Takes all lines from a receipt and extracts:
      - date/time
      - a list of items (with name, quantity, unit_price, total_price)
      - summe (the final total of the receipt)
    """
    result = {
        "date": None,
        "time": None,
        "items": [],
        "summe": None
    }

    collecting_items = False

    # Regex for SUMME (total sum)
    sum_pattern = re.compile(r"SUMME\s*€\s*([\d,]+)")
    # Regex for date + time (e.g. 18.02.25 17:49)
    date_time_pattern = re.compile(r"(\d{2}\.\d{2}\.\d{2})\s+(\d{2}:\d{2})")

    for idx, line in enumerate(lines):
        # 1) Check date/time
        dt_match = date_time_pattern.search(line)
        if dt_match:
            result["date"] = dt_match.group(1)  # e.g. "18.02.25"
            result["time"] = dt_match.group(2)  # e.g. "17:49"

        # 2) If "SUMME" appears => stop collecting items
        if "SUMME" in line:
            collecting_items = False
            m_sum = sum_pattern.search(line)
            if m_sum:
                result["summe"] = float(m_sum.group(1).replace(",", "."))
            continue

        # 3) If the line starts with "EUR" => start collecting items
        if line.startswith("EUR"):
            collecting_items = True
            continue

        # 4) If we are collecting items, process each line
        if collecting_items:
            # a) If it's a "Posten:" line or similar, skip it
            if "Posten:" in line or line.lower().startswith("posten"):
                continue
            if "Coupon:" in line:
                continue

            # b) Check if it's a kilo line (e.g. "0,480 kg x 2,99 /kg")
            #    => we enrich the last item with weight info
            if is_kilo_line(line):
                parse_kilo_line(line, result["items"])
                continue

            # c) Otherwise, treat it as a normal article line
            item = parse_item_line(line)
            # If parse_item_line indicates it's not a valid item,
            # optionally skip it.
            if not item:
                continue

            # Add the item to our list
            result["items"].append(item)

    return result


def is_kilo_line(line: str) -> bool:
    """
    Checks if the line is something like "0,480 kg x 2,99 /kg".
    Returns True/False.
    """
    # Simple regex: ([\d,]+) kg x ([\d,]+) /kg
    # Example: "0,480 kg x 2,99 /kg"
    pattern = re.compile(r"^[\d,]+\s*kg\s*x\s*[\d,]+\s*/kg", re.IGNORECASE)
    return bool(pattern.search(line))


def parse_kilo_line(line: str, items: list):
    """
    Reads lines like "0,480 kg x 2,99 /kg", calculates total_price = 0.480 * 2.99,
    and enriches the *last* item in the list (items[-1]) with these values:
      - quantity = 0.480 (i.e., the weight in kg)
      - unit_price = 2.99 (price per kg)
      - total_price = the rounded result
      - name remains unchanged.
    If 'items' is empty, we do nothing.
    """
    if not items:
        return  # No previous items

    pattern = re.compile(r"^([\d,]+)\s*kg\s*x\s*([\d,]+)\s*/kg", re.IGNORECASE)
    m = pattern.search(line)
    if m:
        weight_str = m.group(1)  # e.g. "0,480"
        kg_price_str = m.group(2)  # e.g. "2,99"
        weight_val = float(weight_str.replace(",", "."))
        kg_price_val = float(kg_price_str.replace(",", "."))

        total = round(weight_val * kg_price_val, 2)

        # Enrich the last item
        last_item = items[-1]
        # If the last item already had quantity=1, we overwrite it here.
        last_item["quantity"] = weight_val
        last_item["unit_price"] = kg_price_val
        last_item["total_price"] = total
        # The name remains as it was, e.g. "PORREE lose".

        # We do NOT add a new item entry.


def parse_item_line(line: str) -> dict:
    """
    Parses a normal article line into:
      {
        "name": ...,
        "quantity": int,
        "unit_price": float,
        "total_price": float
      }
    Supports line formats like:
      - "GURKEN 0,49 x 4"
      - "GURKEN 0,49 EUR x 4"
      - "GURKEN 0,49 € x 4"

    Approach:
      1) Extract total_price at the end of the line (e.g. "1,95 B" -> 1.95).
      2) Check if there's a pattern "([\d,]+)(?:EUR|€)? x (\d+)" to find unit_price and quantity.
      3) If the pattern is broken, but we do have quantity and total_price => unit_price = total_price / quantity.
      4) If nothing matches => quantity=1, unit_price = total_price
    """
    # 1) Remove the final price from the line
    total_price_pattern = re.compile(r"([\d,]+)\s*(?:[A-Z]+|\*?[A-Z]+)?$")
    m_total = total_price_pattern.search(line)
    if not m_total:
        # No end price found => not a valid item line
        return {}

    total_str = m_total.group(1)
    total_val = float(total_str.replace(",", "."))
    # Cut that off the end of 'line'
    line_clean = line[:m_total.start()].strip()

    # 2) This pattern matches:
    #    "someName... (number) [EUR|€ optional] x (quantity) moreText..."
    #    e.g. "GURKEN 0,49 x 4", "GURKEN 0,49 EUR x 4", "GURKEN 0,49 € x 4"
    #    The group(2) will be our price_str, group(3) will be the quantity.
    pattern_price_qty = re.compile(
        r"(.*?)([\d,]+)\s*(?:EUR|€)?\s*x\s*(\d+)(.*)",
        re.IGNORECASE
    )
    mq = pattern_price_qty.search(line_clean)

    # Default result
    item = {
        "name": line_clean.strip(),
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
            # Fallback => keep item as-is
            pass
        else:
            item["quantity"] = quantity_val
            item["unit_price"] = unit_price_val
            # Rebuild name from everything outside the pattern
            item["name"] = cleanup_name(pre_text + " " + post_text)
            item["total_price"] = total_val

            # 3) If unit_price * quantity != total_val => recalc
            computed = round(unit_price_val * quantity_val, 2)
            if quantity_val == 0:
                # quantity cannot be zero, so skip or fallback
                # Option A: fallback to quantity=1
                quantity_val = 1
                item["quantity"] = 1
                item["unit_price"] = total_val  # if we assume total_val is correct
            else:
                # proceed with the mismatch check
                if abs(computed - round(total_val, 2)) > 0.01:
                    item["unit_price"] = round(total_val / quantity_val, 2)
    else:
        # 4) No "x" pattern found => quantity=1, unit_price= total_price
        item["name"] = cleanup_name(item["name"])

    return item


def cleanup_name(raw_name: str) -> str:
    """
    Removes unwanted characters and multiple spaces, etc.
    """
    # Optionally remove "€", "*" etc.
    name = raw_name.replace("€", "").replace("*", " ").strip()
    # Turn multiple spaces into a single space
    name = " ".join(name.split())

    # If needed, apply further heuristics here. For example:
    # "(\d)n,e(\d+)" -> "\1,\2" if you want to fix "1n,e49" -> "1,49".
    # e.g. re.sub(r"(\d)n,e(\d+)", r"\1,\2", name)

    return name


def main():
    # Create an output folders if it doesn't exist
    output_folder = os.path.join("output", "autogenerated")
    os.makedirs(output_folder, exist_ok=True)

    # We'll save 'parsed_receipts.json' inside the output folder
    json_output_path = os.path.join(output_folder, "parsed_receipts.json")

    folder = "receipts/pdfs/"  # Where the PDFs are stored
    all_data = []

    for filename in os.listdir(folder):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(folder, filename)
            parsed = parse_receipt(pdf_path)
            parsed["file"] = filename
            all_data.append(parsed)

    # Save the JSON data
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)

    print(f"Parsing complete. {len(all_data)} PDFs processed.")
    print(f"Results saved to: {json_output_path}")


if __name__ == "__main__":
    main()
