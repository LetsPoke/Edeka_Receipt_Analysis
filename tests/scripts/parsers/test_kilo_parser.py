import pytest
from scripts.parsers.kilo_parser import is_kilo_line, parse_kilo_line


@pytest.mark.parametrize("line, expected", [
    ("0,480 kg x 2,99 /kg", True),  # ✅ Valid kilo-based price format
    ("1,200 kg x 3,49 /kg", True),  # ✅ Different weight and price
    ("500 g x 1,99 /kg", False),  # ❌ Not a valid kg format (grams instead)
    ("Banana 1,99 x 2", False),  # ❌ Normal item, not kilo-based
    ("Apple 3,50 €", False),  # ❌ No weight info
])
def test_is_kilo_line(line, expected):
    assert is_kilo_line(line) == expected, f"Failed on input: {line}"


def test_parse_kilo_line():
    items = [{"name": "Tomato", "quantity": 1, "unit_price": 0, "total_price": 0}]

    # Simulating a weighted item
    parse_kilo_line("0,480 kg x 2,99 /kg", items)

    assert items[-1]["quantity"] == 0.48
    assert items[-1]["unit_price"] == 2.99
    assert items[-1]["total_price"] == pytest.approx(1.43, rel=1e-2)  # 0.48 * 2.99
