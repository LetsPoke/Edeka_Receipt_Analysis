def calculate_daily_spending(df):
    daily_spend = df.groupby("date")["total_price"].sum().reset_index()
    daily_spend.columns = ["date", "spent_per_day"]
    return daily_spend


def calculate_daily_items(df):
    daily_item_count = df.groupby("date")["quantity"].sum().reset_index()
    daily_item_count.columns = ["date", "total_items"]
    return daily_item_count
