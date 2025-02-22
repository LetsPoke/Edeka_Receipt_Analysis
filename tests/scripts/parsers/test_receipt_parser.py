from scripts.parsers.receipt_parser import parse_lines

sample_lines = [
    "10.02.24 14:35",
    "EUR",  # start collecting items
    "1,99 € x 2"
    "Banana 3,98 B",
    "SUMME € 3,98"  # stop collecting items
]


def test_parse_lines_date():
    result = parse_lines(sample_lines, "sample.pdf")

    assert result["date"] == "10.02.24"


def test_parse_lines_time():
    result = parse_lines(sample_lines, "sample.pdf")

    assert result["time"] == "14:35"


def test_parse_lines_items():
    result = parse_lines(sample_lines, "sample.pdf")

    assert result["items"] == [
        {
            "name": "Banana",
            "quantity": 2,
            "unit_price": 1.99,
            "total_price": 3.98
        }
    ]


def test_parse_lines_sum():
    result = parse_lines(sample_lines, "sample.pdf")

    assert result["summe"] == 3.98


def test_parse_lines_file():
    result = parse_lines(sample_lines, "sample.pdf")

    assert result["file"] == "sample.pdf"


def test_parse_lines_no_date():
    result = parse_lines(["EUR"], "sample.pdf")

    assert result["date"] == None


def test_parse_lines_no_time():
    result = parse_lines(["EUR"], "sample.pdf")

    assert result["time"] == None


def test_parse_lines_no_items():
    result = parse_lines(["EUR"], "sample.pdf")

    assert result["items"] == []


def test_parse_lines_no_sum():
    result = parse_lines(["EUR"], "sample.pdf")

    assert result["summe"] == None


def test_parse_lines_no_file():
    result = parse_lines(["EUR"], "sample.pdf")

    assert result["file"] == "sample.pdf"
