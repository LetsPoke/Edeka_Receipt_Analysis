import json
import csv

def convert_json_to_csv(json_file, csv_file):
    """
    Konvertiert die Kassenbon-Daten aus parsed_kassenbons.json in eine CSV-Datei.
    Für jeden Artikel (= items-Eintrag) erzeugen wir eine Zeile.
    """

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Angepasste CSV-Spalten
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
            bon_summe = bon.get("summe", 0.0)
            items = bon.get("items", [])

            # Pro Artikel eine Zeile schreiben
            for item in items:
                row = {
                    "file": file_name,
                    "date": bon_date,
                    "time": bon_time,
                    "item_name": item.get("name", ""),
                    "quantity": item.get("quantity", 1),
                    "unit_price": item.get("unit_price", 0.0),
                    "total_price": item.get("total_price", 0.0),
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
