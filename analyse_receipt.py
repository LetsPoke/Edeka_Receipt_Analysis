import pandas as pd

def main():
    csv_file = "parsed_kassenbons.csv"
    df = pd.read_csv(csv_file)

    # 1) Datentypen anpassen (falls nötig)
    #    date als String, time evtl. auch
    df["date"] = df["date"].astype(str)
    df["time"] = df["time"].astype(str)

    # Optional: Wenn du das Datum in DateTime-Format konvertieren willst:
    # Achtung, deine date ist vermutlich dd.mm.yy, da brauchst du den entsprechenden format-String:
    #
    # df["date"] = pd.to_datetime(df["date"], format="%d.%m.%y", errors="coerce")
    #
    # Dann kannst du z.B. nach Jahr/Monat filtern:
    # df["year"] = df["date"].dt.year
    # df["month"] = df["date"].dt.month

    # 2) Summierte Ausgaben pro Tag (über die Artikel-Summen)
    #    => Summe von total_price pro date
    daily_spend = df.groupby("date")["total_price"].sum().reset_index()
    daily_spend.columns = ["date", "spent_per_day"]
    print("=== Ausgaben pro Tag (sum of total_price) ===")
    print(daily_spend)
    print()

    # 3) Anzahl der gekauften Artikel pro Tag
    #    => Achtung: "Artikel" kann man interpretieren als
    #       a) jede Zeile (df.groupby("date")["item_name"].count())
    #       b) summe aller 'quantity' (wenn quantity > 1 relevant)
    daily_item_count = df.groupby("date")["quantity"].sum().reset_index()
    daily_item_count.columns = ["date", "total_items"]
    print("=== Gekaufte Artikel (Menge) pro Tag ===")
    print(daily_item_count)
    print()

    # 4) Ausgaben pro Kassenbon (date,time)-Kombination
    #    Jede Zeile ist ein Artikel. Also können wir:
    #    a) sum of total_price pro (date,time,file) => "echte" Bons
    #    b) oder wir nehmen den Mittelwert von bon_sum, wenn bon_sum
    #       bei jedem Artikel gleich ist.
    spend_per_bon = df.groupby(["date", "time", "file"])["total_price"].sum().reset_index()
    spend_per_bon.columns = ["date", "time", "file", "spend_this_bon"]
    print("=== Ausgaben pro Kassenbon ===")
    print(spend_per_bon)
    print()

    # 5) Häufigste / Teuerste Artikel
    #    => Wie oft gekauft (Summe quantity), wie viel Geld dafür ausgegeben (Summe total_price)
    #    => Top 10
    item_stats = df.groupby("item_name").agg(
        total_quantity=("quantity", "sum"),
        total_spend=("total_price", "sum")
    ).reset_index()

    # Sort nach den meistgekauften Artikeln
    item_stats_most_bought = item_stats.sort_values(by="total_quantity", ascending=False).head(10)
    # Sort nach dem Geld, das ausgegeben wurde
    item_stats_highest_spend = item_stats.sort_values(by="total_spend", ascending=False).head(10)

    print("=== Top 10 meistgekaufte Artikel (nach Quantity) ===")
    print(item_stats_most_bought)
    print()

    print("=== Top 10 teuerste Artikel (nach total Spend) ===")
    print(item_stats_highest_spend)
    print()

    # 6) Durchschnittlicher Stückpreis pro Artikel
    #    => total_spend / total_quantity, falls total_quantity != 0
    item_stats["avg_unit_price"] = item_stats["total_spend"] / item_stats["total_quantity"]
    print("=== Durchschnittlicher Stückpreis pro Artikel (top 10 nach Spend) ===")
    avg_price_top = item_stats.sort_values(by="total_spend", ascending=False).head(10)
    print(avg_price_top[["item_name", "total_quantity", "total_spend", "avg_unit_price"]])
    print()

    # Optional: Du könntest hier z.B. ein CSV oder Excel exportieren:
    # item_stats.to_csv("item_stats.csv", index=False)

    # 7) Weitere Ideen:
    #   - Zeitliche Auswertung pro Monat (wenn date als datetime geparsed),
    #     z.B. df["month_year"] = df["date"].dt.to_period("M")
    #   - Kategorisierung: Wenn du händisch Artikelnamen zu Kategorien zuordnest (z.B. "Getränke", "Obst/Gemüse"),
    #     kannst du pro Kategorie summieren.
    #   - Visualisierungen: Mit matplotlib oder seaborn Diagramme erstellen.

if __name__ == "__main__":
    main()
