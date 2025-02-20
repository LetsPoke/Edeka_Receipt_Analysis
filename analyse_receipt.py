import os
import pandas as pd

def main():
    csv_file = os.path.join("output", "parsed_receipts.csv")
    df = pd.read_csv(csv_file)

    # 1) Adjust data types if necessary.
    #    Make sure 'date' and 'time' are strings (or transform them later to datetime).
    df["date"] = df["date"].astype(str)
    df["time"] = df["time"].astype(str)

    # Optional: Convert 'date' to a proper datetime if it's in dd.mm.yy format:
    # df["date"] = pd.to_datetime(df["date"], format="%d.%m.%y", errors="coerce")
    #
    # Then you can, for example, filter by year/month:
    # df["year"] = df["date"].dt.year
    # df["month"] = df["date"].dt.month

    # 2) Sum of total spending per day based on each item's total_price
    daily_spend = df.groupby("date")["total_price"].sum().reset_index()
    daily_spend.columns = ["date", "spent_per_day"]
    print("=== Spending per Day (sum of total_price) ===")
    print(daily_spend)
    print()

    # 3) Number of items purchased per day
    #    Note: "items" can mean:
    #       a) each row (df.groupby("date")["item_name"].count())
    #       b) sum of 'quantity' if some items have quantity > 1
    daily_item_count = df.groupby("date")["quantity"].sum().reset_index()
    daily_item_count.columns = ["date", "total_items"]
    print("=== Number of Items Purchased per Day (sum of quantities) ===")
    print(daily_item_count)
    print()

    # 4) Spending per receipt (date,time) combination
    #    Each row is an item, so we can:
    #    a) sum total_price by (date,time,file) => "actual" receipts
    #    b) or take the average of bon_sum if bon_sum is the same for each item
    spend_per_bon = df.groupby(["date", "time", "file"])["total_price"].sum().reset_index()
    spend_per_bon.columns = ["date", "time", "file", "spend_this_bon"]
    print("=== Spending per Receipt ===")
    print(spend_per_bon)
    print()

    # 5) Most frequently purchased / Most expensive items
    #    => How often purchased (sum of quantity), how much total was spent (sum of total_price)
    #    => Top 10
    item_stats = df.groupby("item_name").agg(
        total_quantity=("quantity", "sum"),
        total_spend=("total_price", "sum")
    ).reset_index()

    # Sort by most purchased items
    item_stats_most_bought = item_stats.sort_values(by="total_quantity", ascending=False).head(10)
    # Sort by total spending
    item_stats_highest_spend = item_stats.sort_values(by="total_spend", ascending=False).head(10)

    print("=== Top 10 Most Purchased Items (by Quantity) ===")
    print(item_stats_most_bought)
    print()

    print("=== Top 10 Most Expensive Items (by total spending) ===")
    print(item_stats_highest_spend)
    print()

    # 6) Average unit price per item => total_spend / total_quantity (if not zero)
    item_stats["avg_unit_price"] = item_stats["total_spend"] / item_stats["total_quantity"]
    print("=== Average Unit Price per Item (top 10 by total spending) ===")
    avg_price_top = item_stats.sort_values(by="total_spend", ascending=False).head(10)
    print(avg_price_top[["item_name", "total_quantity", "total_spend", "avg_unit_price"]])
    print()

    # Create 'output' folder if it does not exist
    output_folder = "output"
    os.makedirs(output_folder, exist_ok=True)

    # We'll write item_stats.csv to the 'output' folder
    item_stats_csv = os.path.join(output_folder, "item_stats.csv")
    item_stats.to_csv(item_stats_csv, index=False)

if __name__ == "__main__":
    main()
