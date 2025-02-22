import pytest
from scripts.parsers.text_cleaner import cleanup_name


@pytest.mark.parametrize("raw_name, expected", [
    # Normal case
    ("Banana", "Banana"),

    # Special characters conversion
    ("Möhre", "Moehre"),
    ("Süßigkeit", "Suessigkeit"),
    ("Mäuse", "Maeuse"),

    # Uppercase to Title Case
    ("BANANA", "Banana"),
    ("APFEL", "Apfel"),

    # Extra spaces
    ("  Banane  ", "Banane"),
    ("  Apfel  Rot ", "Apfel Rot"),

    # Combination of issues
    ("  SÜßIGKEITEN  ", "Suessigkeiten"),
    ("   EHL MÖHREN ", "Ehl Moehren"),
])
def test_cleanup_name(raw_name, expected):
    result = cleanup_name(raw_name)
    assert result == expected, f"Failed on input: {raw_name}"
