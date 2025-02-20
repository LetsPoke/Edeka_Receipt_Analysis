import os
import re
import json
import pdfplumber

def parse_lines(lines):
    """
    Parst eine Liste von Zeilen, in der EIN Kassenbon
    (evtl. über mehrere PDF-Seiten verteilt) enthalten ist.
    Ignoriert MwSt und Payback-Infos.
    """
    result = {
        "date": None,
        "time": None,
        "items": [],
        "summe": None
    }

    # Regex, um Artikelzeilen zu erkennen, z.B.:
    # "2€ x 0,89E.Vega.Kochcreme 1,78 A"  -> Name = (2€ x 0,89E.Vega.Kochcreme), Price = (1,78 A)
    # "kg x0,962 1,99"                   -> Name = (kg x0,962), Price = (1,99)
    # Ende der Zeile: Preis + optional Buchstaben
    item_pattern = re.compile(r"(.+?)\s+([\d,]+(?:\s*[A-Z]+)?)$")

    # Regex für Datum + Uhrzeit, z.B. "20.12.24 12:07"
    date_time_pattern = re.compile(r"(\d{2}\.\d{2}\.\d{2})\s+(\d{2}:\d{2})")

    collecting_items = False

    for line in lines:
        line = line.strip()

        # 1. Starte Artikelliste nach dem Wort "EUR"
        if line.startswith("EUR"):
            collecting_items = True
            continue

        # 2. Bei "SUMME" aufhören und Summe parsen
        if "SUMME" in line:
            collecting_items = False
            match_sum = re.search(r"SUMME\s*€\s*([\d,]+)", line)
            if match_sum:
                result["summe"] = float(match_sum.group(1).replace(",", "."))
            continue

        # 3. Artikel erfassen, wenn collecting_items aktiv
        if collecting_items:
            match_item = item_pattern.search(line)
            if match_item:
                name = match_item.group(1).strip()
                price_str = match_item.group(2).strip()
                # Nur den numerischen Teil in float umwandeln
                m_price = re.search(r"([\d,]+)", price_str)
                if m_price:
                    price_val = float(m_price.group(1).replace(",", "."))
                else:
                    price_val = 0.0

                result["items"].append({
                    "name": name,
                    "price": price_val
                })

        # 4. Datum / Uhrzeit erkennen
        dt_match = date_time_pattern.search(line)
        if dt_match:
            result["date"] = dt_match.group(1)  # z.B. 20.12.24
            result["time"] = dt_match.group(2)  # z.B. 12:07

    return result

def parse_kassenbon(pdf_path: str):
    """
    Öffnet ein PDF und fasst ALLE Seiten zusammen, um
    einen einzigen Kassenbon-Datensatz zu erhalten.
    (Falls wirklich mehrere Bons in einem PDF wären,
     müsste man mehr Logik einbauen, um sie zu trennen.)
    """
    all_lines = []

    with pdfplumber.open(pdf_path) as pdf:
        # Alle Seiten durchlaufen, Text in Zeilen listen
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                page_lines = page_text.split("\n")
                all_lines.extend(page_lines)

    # Nun parse_lines() auf die Gesamtheit aller Zeilen anwenden
    result = parse_lines(all_lines)
    return result

def main():
    folder = "Kassenbons"  # Ordner, in dem deine PDFs liegen
    output_json = "parsed_kassenbons.json"
    all_data = []

    for filename in os.listdir(folder):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(folder, filename)
            parsed = parse_kassenbon(pdf_path)
            parsed["file"] = filename
            all_data.append(parsed)

    # Speichere alle Einträge in einer JSON-Datei
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)

    print(f"Parsing abgeschlossen. {len(all_data)} PDF-Dateien verarbeitet.")
    print(f"Ergebnis-Datei: {output_json}")

if __name__ == "__main__":
    main()
