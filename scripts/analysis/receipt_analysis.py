def spending_per_receipt(df):
    spend_per_bon = df.groupby(["date", "time", "file"])["total_price"].sum().reset_index()
    spend_per_bon.columns = ["date", "time", "file", "spend_this_bon"]
    return spend_per_bon


def calculate_daily_spending(df):
    daily_spend = df.groupby("date")["total_price"].sum().reset_index()
    daily_spend.columns = ["date", "spent_per_day"]
    return daily_spend


def calculate_daily_items(df):
    daily_item_count = df.groupby("date")["quantity"].sum().reset_index()
    daily_item_count.columns = ["date", "total_items"]
    return daily_item_count
