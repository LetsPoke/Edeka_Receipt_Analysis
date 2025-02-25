from load_data import load_receipts_data
from item_visualization import plot_item_price_over_time, plot_multi_items_price_over_time


def main():
    df = load_receipts_data()  # your existing function

    item_level(df)


def item_level(df):

    items = [
        "Gurken",
        "Ruegen.Mueh.Mett",
        "Oatly Hafer Aufst.",
        "G&G Halbf.Margari.",
        "Harry Vital U.Fit"
    ]

    # plot_multi_items_price_over_time(df, items, output_name="multi_items_price.png")

    all_items = df["item_name"].unique()
    # plot_multi_items_price_over_time(df, all_items, output_name="unique_items_price.png")

    # all items with more than x entries
    top_items = df["item_name"].value_counts()
    top_items = top_items[top_items >= 18].index
    plot_multi_items_price_over_time(df, top_items, output_name="all_items_price_18.png")

    plot_item_price_over_time(df, "Gurken")
    plot_item_price_over_time(df, "Ruegen.Mueh.Mett")
    plot_item_price_over_time(df, "Oatly Hafer Aufst.")


if __name__ == "__main__":
    main()
