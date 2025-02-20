import os
import json
import csv

def convert_json_to_csv(json_file, csv_file):
    """
    Converts receipt data from a JSON file into a CSV file,
    creating one row per item.
    """

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # CSV column names (adjust if necessary)
    fieldnames = [
        "file",
        "date",
        "time",
        "item_name",
        "quantity",
        "unit_price",
        "total_price",
        "bon_sum"
    ]

    with open(csv_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for bon in data:
            file_name = bon.get("file", "")
            bon_date = bon.get("date", "")
            bon_time = bon.get("time", "")
            bon_sum = bon.get("summe", 0.0)  # 'summe' is the field in JSON
            items = bon.get("items", [])

            for item in items:
                row = {
                    "file": file_name,
                    "date": bon_date,
                    "time": bon_time,
                    "item_name": item.get("name", ""),
                    "quantity": item.get("quantity", 1),
                    "unit_price": item.get("unit_price", 0.0),
                    "total_price": item.get("total_price", 0.0),
                    "bon_sum": bon_sum
                }
                writer.writerow(row)

    print(f"Conversion to CSV completed. File: {csv_file}")


def main():
    # We assume the JSON is in the 'output' folder
    input_json = os.path.join("output", "parsed_receipts.json")

    # Create 'output' folder if it does not exist
    output_folder = "output"
    os.makedirs(output_folder, exist_ok=True)

    # We'll write parsed_receipts.csv to the 'output' folder
    output_csv = os.path.join(output_folder, "parsed_receipts.csv")

    convert_json_to_csv(input_json, output_csv)

if __name__ == "__main__":
    main()
