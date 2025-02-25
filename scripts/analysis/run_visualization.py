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

    plot_multi_items_price_over_time(df, items, output_name="all_items_price.png")

    plot_item_price_over_time(df, "Gurken")
    plot_item_price_over_time(df, "Ruegen.Mueh.Mett")
    plot_item_price_over_time(df, "Oatly Hafer Aufst.")
    plot_item_price_over_time(df, "Zucchini")
    plot_item_price_over_time(df, "G&G Halbf.Margari.")
    plot_item_price_over_time(df, "Harry Sonnt.Broet.")
    plot_item_price_over_time(df, "Harry Vital U.Fit")
    plot_item_price_over_time(df, "Bio E.Cashewkerne")


if __name__ == "__main__":
    main()
