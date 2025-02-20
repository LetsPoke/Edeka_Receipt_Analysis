import os
import re
import json
import pdfplumber

def parse_kassenbon(pdf_path: str) -> dict:
    """
    Öffnet ein mehrseitiges PDF, sammelt alle Zeilen in all_lines
    und parsed diese zu einem einzigen Kassenbon-Dict:
      {
        "date": "...",
        "time": "...",
        "items": [...],
        "summe": float,
        "file": pdf_path
      }
    """
    all_lines = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                for line in text.split("\n"):
                    line = line.strip()
                    all_lines.append(line)

    # Danach interpretieren wir das als EINEN Bon.
    return parse_lines(all_lines)


def parse_lines(lines: list) -> dict:
    """
    Nimmt alle Zeilen eines Kassenbons und extrahiert:
      - Datum / Uhrzeit
      - Liste von Items (mit name, quantity, unit_price, total_price)
      - summe (Endsumme des Bons)
    """
    result = {
        "date": None,
        "time": None,
        "items": [],
        "summe": None
    }

    collecting_items = False

    # Regex für SUMME
    sum_pattern = re.compile(r"SUMME\s*€\s*([\d,]+)")
    # Regex für Datum+Uhrzeit
    date_time_pattern = re.compile(r"(\d{2}\.\d{2}\.\d{2})\s+(\d{2}:\d{2})")

    for idx, line in enumerate(lines):
        # 1) Datum/Uhrzeit checken
        dt_match = date_time_pattern.search(line)
        if dt_match:
            result["date"] = dt_match.group(1)  # z.B. "18.02.25"
            result["time"] = dt_match.group(2)  # z.B. "17:49"

        # 2) SUMME => Items enden
        if "SUMME" in line:
            collecting_items = False
            m_sum = sum_pattern.search(line)
            if m_sum:
                result["summe"] = float(m_sum.group(1).replace(",", "."))
            continue

        # 3) EUR => ab hier starten wir das Sammeln von Artikelzeilen
        if line.startswith("EUR"):
            collecting_items = True
            continue

        # 4) Falls wir gerade Artikel sammeln, verarbeiten wir die Zeilen
        if collecting_items:
            # a) Falls es eine "Posten:" Zeile oder ähnliches ist, skippen wir
            if "Posten:" in line or line.lower().startswith("posten"):
                continue
            if "Coupon:" in line:
                continue

            # b) Erkennen wir eine Zeile mit Kilo-Angaben?
            #    z.B. "0,480 kg x 2,99 /kg" => wir reichern den letzten Artikel an
            if is_kilo_line(line):
                parse_kilo_line(line, result["items"])
                continue

            # c) Sonst versuchen wir, die Zeile als normalen Artikel zu parsen
            item = parse_item_line(line)
            # Wenn parse_item_line sagt, es war wahrscheinlich kein Artikel,
            # kann man optional skippen.
            if not item:
                continue

            # item zurück in die Liste
            result["items"].append(item)

    return result


def is_kilo_line(line: str) -> bool:
    """
    Prüft, ob es sich um eine Zeile handelt wie "0,480 kg x 2,99 /kg".
    Gibt True/False zurück.
    """
    # Ein simples Regex: ([\d,]+) kg x ([\d,]+) /kg
    # Bsp: "0,480 kg x 2,99 /kg"
    pattern = re.compile(r"^[\d,]+\s*kg\s*x\s*[\d,]+\s*/kg", re.IGNORECASE)
    return bool(pattern.search(line))


def parse_kilo_line(line: str, items: list):
    """
    Liest Zeilen wie "0,480 kg x 2,99 /kg", berechnet total_price = 0,480*2,99,
    und reichert den *letzten* Artikel (items[-1]) damit an.
    - quantity = 0.480 (sprich, KG)
    - unit_price = 2.99 (€/kg)
    - total_price = gerundetes Ergebnis
    - name bleibt unverändert.
    Hinweis: Falls items leer ist, machen wir nichts.
    """
    if not items:
        return  # Keine vorherigen Artikel vorhanden

    pattern = re.compile(r"^([\d,]+)\s*kg\s*x\s*([\d,]+)\s*/kg", re.IGNORECASE)
    m = pattern.search(line)
    if m:
        weight_str = m.group(1)  # z.B. "0,480"
        kg_price_str = m.group(2)  # z.B. "2,99"
        weight_val = float(weight_str.replace(",", "."))
        kg_price_val = float(kg_price_str.replace(",", "."))

        total = round(weight_val * kg_price_val, 2)

        # Letzten Artikel anreichern:
        last_item = items[-1]
        # Falls der letzte Artikel schon was drin hat (z.B. quantity=1),
        # überschreiben wir das. Alternativ könntest du es addieren o.ä.
        last_item["quantity"] = weight_val
        last_item["unit_price"] = kg_price_val
        last_item["total_price"] = total
        # Der name bleibt so, wie er im letzten Artikel war
        # (z.B. "PORREE lose").

        # Fertig. Wir legen KEINEN neuen Artikel an.


def parse_item_line(line: str) -> dict:
    """
    Parst eine normale Artikelzeile in:
      {
        "name": ...,
        "quantity": int,
        "unit_price": float,
        "total_price": float
      }

    Vorgehen:
      1) Extrahiere total_price am Zeilenende (z.B. "1,95 B" -> 1,95).
      2) Schaue, ob ein Muster "X,YZ € x N" existiert, um unit_price und quantity zu holen.
      3) Falls es kaputt ist, wir haben quantity, total_price => unit_price = total_price / quantity.
      4) Falls gar nichts geht => quantity=1, unit_price=total_price
    """
    # 1) Gesamten Endpreis entfernen
    total_price_pattern = re.compile(r"([\d,]+)\s*(?:[A-Z]+|\*?[A-Z]+)?$")
    # ([\d,]+) -> "1,95"
    # \s*(?:[A-Z]+|\*?[A-Z]+)? -> optional Buchstaben etc. "B" oder "*B" oder "AW"
    m_total = total_price_pattern.search(line)
    if not m_total:
        # Kein Endpreis gefunden => Kein valider Artikel
        return {}

    total_str = m_total.group(1)
    total_val = float(total_str.replace(",", "."))
    # Schneide das hinten ab:
    line_clean = line[:m_total.start()].strip()

    # 2) Suche unser Muster:  "(\d+,\d+) € x (\d+)"
    #    z.B. "0,65 € x 3"
    pattern_price_qty = re.compile(r"(.*?)([\d,]+)\s*€\s*x\s*(\d+)(.*)")
    mq = pattern_price_qty.search(line_clean)

    # Standard-Result
    item = {
        "name": line_clean.strip(),
        "quantity": 1,
        "unit_price": total_val,
        "total_price": total_val
    }

    if mq:
        pre_text, price_str, qty_str, post_text = mq.groups()
        try:
            unit_price_val = float(price_str.replace(",", "."))
            quantity_val = int(qty_str)
        except ValueError:
            # Fallback => wir behalten item so
            pass
        else:
            item["quantity"] = quantity_val
            item["unit_price"] = unit_price_val
            item["name"] = cleanup_name(pre_text + " " + post_text)
            item["total_price"] = total_val

            # 3) Falls unit_price * quantity != total_val => wir übernehmen total_val,
            #    und erlauben die Korrektur: unit_price = total_val / quantity
            #    So beheben wir Problem #1: Falls PDF-Text kaputt war.
            computed = round(unit_price_val * quantity_val, 2)
            if abs(computed - round(total_val, 2)) > 0.01:
                # Falls Diskrepanz => Stückpreis ausrechnen:
                item["unit_price"] = round(total_val / quantity_val, 2)

    else:
        # Fallback-Fall: Kein "€ x" gefunden
        # => quantity=1, unit_price= total_price
        # => Falls der Zeiletext kaputt ist (z.B. "E.Vega.Kochcrem1n,e49 ..."),
        #    wir haben total_val, also name= line_clean
        item["name"] = cleanup_name(item["name"])

    return item


def cleanup_name(raw_name: str) -> str:
    """
    Entfernt störende Sonderzeichen, mehrfache Leerzeichen etc.
    """
    # Optional: Ersetze "€", "*", etc.
    name = raw_name.replace("€", "").replace("*", " ").strip()
    # Mehrfach-Spaces -> einfacher Space
    name = " ".join(name.split())

    # Hier könntest du weitere Heuristiken einbauen, z.B.
    # "(\d)n,e(\d+)" -> "\1,\2" falls du die kaputten "1n,e49" -> "1,49" fixen willst.
    # => re.sub(r"(\d)n,e(\d+)", r"\1,\2", name)

    return name

def main():
    folder = "Kassenbons"
    output_json = "parsed_kassenbons.json"
    all_data = []

    for filename in os.listdir(folder):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(folder, filename)
            data = parse_kassenbon(pdf_path)
            data["file"] = filename
            all_data.append(data)

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)

    print(f"Parsing abgeschlossen. {len(all_data)} PDF-Dateien verarbeitet.")
    print(f"Ergebnisse in: {output_json}")

if __name__ == "__main__":
    main()
