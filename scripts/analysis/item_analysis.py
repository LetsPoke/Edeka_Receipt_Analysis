def single_item_over_time(df, item_name):
    item_data = df[df["item_name"] == item_name]
    return item_data
