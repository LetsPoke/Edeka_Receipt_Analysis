import os
import re
import json
import pdfplumber

def parse_item_line(line):
    """
    Zerlegt eine Artikellinie in:
      name, quantity, unit_price, total_price.

    Beispiele:
      "3€ x 0,65Paderb.Pils 0,50l 1,95 B"
       -> name="Paderb.Pils 0,50l", quantity=3, unit_price=0.65, total_price=1.95

      "Pfand 0,15*B" -> wenn kein 'x' gefunden wird => quantity=1, unit_price=0.15, total_price=0.15

      "3€ x 0,25Pfand 0,75*B"
       -> name="Pfand", quantity=3, unit_price=0.25, total_price=0.75
    """
    result = {
        "name": line.strip(),
        "quantity": 1,
        "unit_price": 0.0,
        "total_price": 0.0
    }

    # 1) ENDPRICE (z.B. "1,95") extrahieren
    #    Am Ende der Zeile steht etwas wie "1,95 B" oder "0,75*B" oder nur "1,95"
    final_price_pattern = re.compile(r"([\d,]+)\s*[A-Z]*(?:\*?[A-Z]+)?$")
    # Erläuterung:
    # ([\d,]+) = z.B. 1,95
    # \s*[A-Z]* = optional Leerzeichen + Buchstaben (A, B, AW..)
    # (?:\*?[A-Z]+)? = optional Stern + weitere Buchstaben
    # Wir wollen so "1,95 B", "1,95AW", "0,75*B" etc. erwischen.

    m_end = final_price_pattern.search(line)
    if m_end:
        total_str = m_end.group(1)  # z.B. "1,95" oder "0,75"
        total_val = float(total_str.replace(",", "."))
        result["total_price"] = total_val
        # Schneiden wir das raus aus 'line', damit wir beim nächsten Schritt
        # nicht mehr den Endpreis doppelt parsen
        cut_pos = m_end.start()
        line = line[:cut_pos].strip()

    # 2) SUCHE NACH MUSTER FÜR "(quantity) x (price)" oder "(price) x (quantity)"
    #    Variante A: "(\d+)€?\s*x\s*([\d,]+)"
    pattern_a = re.compile(r"(.*?)(\d+)\s*€?\s*x\s*([\d,]+)(.*)")
    #    Variante B: "([\d,]+)\s*€?\s*x\s*(\d+)"
    pattern_b = re.compile(r"(.*?)([\d,]+)\s*€?\s*x\s*(\d+)(.*)")

    found_multiplication = False
    tmp_line = line

    # Erst Variante A: => quantity= \2, unit_price= \3
    ma = pattern_a.search(tmp_line)
    if ma:
        found_multiplication = True
        pre_text, q_str, up_str, post_text = ma.groups()
        # quantity
        quantity_val = int(q_str)  # Annahme: Ganzzahlig
        # unit_price
        up_val = float(up_str.replace(",", "."))

        # Falls total_price=0.0, berechnen wir es eben
        if result["total_price"] == 0.0:
            result["total_price"] = round(quantity_val * up_val, 2)

        # Name ist pre_text + post_text
        the_name = (pre_text + " " + post_text).strip()
        the_name = cleanup_name(the_name)

        result["quantity"] = quantity_val
        result["unit_price"] = up_val
        result["name"] = the_name

    else:
        # Dann Variante B: => unit_price= \2, quantity= \3
        mb = pattern_b.search(tmp_line)
        if mb:
            found_multiplication = True
            pre_text, up_str, q_str, post_text = mb.groups()
            quantity_val = int(q_str)
            up_val = float(up_str.replace(",", "."))

            if result["total_price"] == 0.0:
                result["total_price"] = round(quantity_val * up_val, 2)

            the_name = (pre_text + " " + post_text).strip()
            the_name = cleanup_name(the_name)

            result["quantity"] = quantity_val
            result["unit_price"] = up_val
            result["name"] = the_name

    # 3) WENN WEDER A NOCH B -> quantity=1, unit_price= total_price
    if not found_multiplication:
        # Dann könnte es so was sein wie "Pfand 0,15*B", "Fanta Zero 1l 1,59 B" usw.
        # -> quantity=1, unit_price= total_price
        result["quantity"] = 1
        result["unit_price"] = result["total_price"]
        # Den restlichen Text nehmen wir als Name
        result["name"] = cleanup_name(line)

    return result

def cleanup_name(raw_name):
    """
    Entfernt doppelte Leerzeichen, €-Zeichen, Sternchen usw.
    """
    name = raw_name.replace("€", "").replace("*", " ").strip()
    # Eventuelle Mehrfach-Spaces:
    name = " ".join(name.split())
    return name


def parse_lines(lines):
    """
    Parst die gesamten Zeilen eines (ggf. mehrseitigen) Bons
    und gibt date, time und items zurück (sowie summe).
    """
    result = {
        "date": None,
        "time": None,
        "items": [],
        "summe": None
    }

    # Wenn wir item-spezifische Felder brauchen (quantity, unit_price, total_price)
    # ersetzen wir unser altes "price" durch "unit_price" und "quantity"/"total_price".

    # „collecting_items“ wird True, nachdem wir "EUR" gefunden haben
    collecting_items = False

    # Regex für Summen-Zeilen, z.B. "SUMME € 10,84"
    sum_pattern = re.compile(r"SUMME\s*€\s*([\d,]+)")
    # Regex für Datum/Uhrzeit, z.B. "18.02.25 17:49"
    date_time_pattern = re.compile(r"(\d{2}\.\d{2}\.\d{2})\s+(\d{2}:\d{2})")

    for line in lines:
        line = line.strip()

        # 1) "EUR" -> ab hier Artikel sammeln
        if line.startswith("EUR"):
            collecting_items = True
            continue

        # 2) "SUMME" -> Artikelsammlung beenden
        if "SUMME" in line:
            collecting_items = False
            m_sum = sum_pattern.search(line)
            if m_sum:
                result["summe"] = float(m_sum.group(1).replace(",", "."))
            continue

        # 3) Artikel verarbeiten
        if collecting_items:
            item_dict = parse_item_line(line)
            # Wir ignorieren Artikelzeilen, die 0 als total_price haben?
            # (Manche Zeilen könnten Pfand etc. sein)
            # Oder wir nehmen alles, was wir finden.
            result["items"].append(item_dict)

        # 4) Datum / Uhrzeit
        dt_match = date_time_pattern.search(line)
        if dt_match:
            result["date"] = dt_match.group(1)
            result["time"] = dt_match.group(2)

    return result


def parse_kassenbon(pdf_path: str):
    """
    Liest ALLE Seiten eines PDFs und interpretiert sie
    als EINEN Kassenbon (falls der Bon über 2 Seiten geht).
    """
    all_lines = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_lines.extend(text.split("\n"))

    return parse_lines(all_lines)

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
