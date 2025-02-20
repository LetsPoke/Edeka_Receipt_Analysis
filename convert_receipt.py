import json
import csv

def convert_json_to_csv(json_file, csv_file):
    """
    Konvertiert die Kassenbon-Daten aus einer JSON-Datei in eine CSV-Datei.
    Wir erstellen eine Zeile pro Artikel.
    """
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # CSV-Spalten
    fieldnames = ["file", "date", "time", "item_name", "price", "bon_sum"]

    with open(csv_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for bon in data:
            file_name = bon.get("file", "")
            bon_date = bon.get("date", "")
            bon_time = bon.get("time", "")
            bon_summe = bon.get("summe", 0.0)
            items = bon.get("items", [])

            # Pro Artikel eine Zeile in der CSV
            for item in items:
                row = {
                    "file": file_name,
                    "date": bon_date,
                    "time": bon_time,
                    "item_name": item["name"],
                    "price": item["price"],
                    "bon_sum": bon_summe
                }
                writer.writerow(row)

    print(f"Konvertierung nach CSV abgeschlossen. Datei: {csv_file}")

def main():
    input_json = "parsed_kassenbons.json"
    output_csv = "parsed_kassenbons.csv"
    convert_json_to_csv(input_json, output_csv)

if __name__ == "__main__":
    main()
