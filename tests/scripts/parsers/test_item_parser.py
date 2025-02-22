import pytest
from scripts.parsers.item_parser import parse_item_line


@pytest.mark.parametrize("sample_line, expected", [
    # Standard case with "€" symbol
    ("Banana 1,99 € x 2 3,98 B",
     {"name": "Banana", "quantity": 2, "unit_price": 1.99, "total_price": 3.98}),

    # Without "€" symbol
    ("Banana 1,99 x 2 3,98 B",
     {"name": "Banana", "quantity": 2, "unit_price": 1.99, "total_price": 3.98}),

    # With "EUR" instead of "€"
    ("Banana 1,99 EUR x 2 3,98 B",
     {"name": "Banana", "quantity": 2, "unit_price": 1.99, "total_price": 3.98}),

    # Single item without quantity line
    ("Banana 1,99 B",
     {"name": "Banana", "quantity": 1, "unit_price": 1.99, "total_price": 1.99}),

    # Edge case: Large quantity
    ("Banana 1,99 € x 10 19,90 B",
     {"name": "Banana", "quantity": 10, "unit_price": 1.99, "total_price": 19.90}),

    # Edge case: Weird spacing
    (" Banana  1,99   €  x   2    3,98  B ",
     {"name": "Banana", "quantity": 2, "unit_price": 1.99, "total_price": 3.98}),

])
def test_parse_item_line(sample_line, expected):
    result = parse_item_line(sample_line)
    assert result == expected, f"Failed on input: {sample_line}"
