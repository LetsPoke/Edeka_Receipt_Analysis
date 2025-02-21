def spending_per_receipt(df):
    spend_per_bon = df.groupby(["date", "time", "file"])["total_price"].sum().reset_index()
    spend_per_bon.columns = ["date", "time", "file", "spend_this_bon"]
    return spend_per_bon
