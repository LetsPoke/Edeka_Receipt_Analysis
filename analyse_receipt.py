import pandas as pd

def main():
    csv_file = "parsed_kassenbons.csv"
    df = pd.read_csv(csv_file)

    # Beispiel: Gesamte Ausgabe pro Tag berechnen
    # (Achtung, da pro Artikel Zeile eine SUMME steht, wäre die Summe mehrfach
    #  pro Bon enthalten. Daher lieber die UNIQUE-(date,time)-Kombination nutzen
    #  oder echte Artikel-Summen aus der price-Spalte bilden.)
    #
    # Variante 1: Summe aller Einzelpreise pro Tag:
    df["date"] = df["date"].astype(str)  # sicherstellen, dass date ein String ist
    ausgaben_pro_tag = df.groupby("date")["price"].sum().reset_index()

    print("=== Ausgaben pro Tag (Summe der Artikelpreise) ===")
    print(ausgaben_pro_tag)

    # Beispiel: Anzahl der gekauften Artikel pro Tag
    artikel_anzahl_pro_tag = df.groupby("date")["item_name"].count().reset_index()
    artikel_anzahl_pro_tag.columns = ["date", "count_items"]

    print("\n=== Anzahl der gekauften Artikel pro Tag ===")
    print(artikel_anzahl_pro_tag)

    # Du kannst hier beliebig weitere Analysen oder Visualisierungen hinzufügen.
    # z.B. Summe pro "Bon" statt pro Tag (dafür braucht man die (date, time)-Kombination):
    #   df.groupby(["date", "time"])["price"].sum()

if __name__ == "__main__":
    main()
