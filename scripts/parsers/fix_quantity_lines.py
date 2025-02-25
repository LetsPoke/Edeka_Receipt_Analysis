import re


def fix_quantity_lines(items: list) -> list:
    """
    Post-processes the item list to merge lines like "2 x", "4 x", etc.
    Example:
      If items[i] is { "name": "2 x", "unit_price": 0.59, "total_price": 0.59 }
      and items[i+1] is { "name": "Pizza", "quantity": 1,
                          "unit_price": 1.18, "total_price": 1.18 }
      then we merge them into:
      { "name": "Pizza", "quantity": 2, "unit_price": 0.59,
        "total_price": 1.18 }
      and remove the '2 x' line.

    Returns the updated item list.
    """
    i = 0
    while i < len(items):
        line_name = items[i]["name"]
        match_q = re.match(r"^(\d+)\s*x$", line_name, re.IGNORECASE)
        if match_q:
            # e.g. "2 x" or "4 x" or "19 x"
            qty_val = int(match_q.group(1))

            # Check if there's a next item
            if i + 1 < len(items):
                next_item = items[i + 1]

                # We expect that next_item["total_price"] = qty_val * items[i]["unit_price"]
                expected_total = round(qty_val * items[i]["unit_price"], 2)
                actual_next_total = round(next_item["total_price"], 2)

                if abs(expected_total - actual_next_total) < 0.001:
                    # Merge
                    next_item["quantity"] = qty_val
                    next_item["unit_price"] = items[i]["unit_price"]
                    # total_price remains next_item["total_price"] (e.g. 1.18).
                    # Remove the "2 x"/"4 x"/... line from the list
                    items.pop(i)
                    # Don't increment 'i' because we want to stay on the same
                    # index for the next iteration (which is now the merged item).
                    continue
        i += 1
    return items
