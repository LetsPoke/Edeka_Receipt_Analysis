def analyze_item_purchases(df):
    item_stats = df.groupby("item_name").agg(
        total_quantity=("quantity", "sum"),
        total_spend=("total_price", "sum")
    ).reset_index()

    # Most purchased items
    item_stats_most_bought = item_stats.sort_values(by="total_quantity", ascending=False).head(10)

    # Most expensive items
    item_stats_highest_spend = item_stats.sort_values(by="total_spend", ascending=False).head(10)

    # Average unit price
    item_stats["avg_unit_price"] = item_stats["total_spend"] / item_stats["total_quantity"]

    return item_stats, item_stats_most_bought, item_stats_highest_spend
