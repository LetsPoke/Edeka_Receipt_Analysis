import os
import json
import pytest
from scripts.utils.file_handler import save_json


@pytest.fixture
def temp_output_folder(tmpdir):
    """ Creates a temporary output directory for testing. """
    return str(tmpdir.mkdir("output"))


def test_save_json(temp_output_folder):
    """ Test saving a JSON file and verifying its contents. """
    data = [{"name": "Banana", "quantity": 2, "unit_price": 1.99, "total_price": 3.98}]
    filename = "test_receipts.json"
    file_path = os.path.join(temp_output_folder, filename)

    # Call the function
    save_json(data, file_path)

    # Check if the file was created
    assert os.path.exists(file_path), f"File was not created: {file_path}"

    # Read the file and validate its contents
    with open(file_path, "r", encoding="utf-8") as f:
        loaded_data = json.load(f)

    assert loaded_data == data, f"Data mismatch. Expected {data}, got {loaded_data}"


def test_save_json_empty(temp_output_folder):
    """ Test saving an empty JSON file. """
    data = []
    filename = "empty.json"
    file_path = os.path.join(temp_output_folder, filename)

    save_json(data, file_path)

    assert os.path.exists(file_path), "Empty JSON file was not created."

    with open(file_path, "r", encoding="utf-8") as f:
        loaded_data = json.load(f)

    assert loaded_data == [], "Empty JSON file did not contain an empty list."
