from load_data import load_receipts_data
from basic_statistics import display_basic_statistics
from receipt_analysis import spending_per_receipt, calculate_daily_spending, calculate_daily_items
from overall_analysis import analyze_overall_purchases
from output_results import save_to_csv


def main():
    df = load_receipts_data()  # returns a pandas DataFrame

    # display_basic_statistics(df)

    receipt_level(df)

    top_level(df)


def receipt_level(df):

    # Daily Spending & Items
    daily_spend = calculate_daily_spending(df)
    daily_items = calculate_daily_items(df)
    spend_per_bon = spending_per_receipt(df)

    print("=== Spending per Day ===")
    print(daily_spend.head(), "\n")

    print("=== Average Daily Spending ===")
    print(daily_spend["spent_per_day"].mean(), "\n")

    print("=== Number of Items Purchased per Day ===")
    print(daily_items.head(), "\n")

    print("=== Average Number of Items Purchased per Day ===")
    print(daily_items["total_items"].mean(), "\n")

    print("=== Spending per Receipt ===")
    print(spend_per_bon.head(), "\n")

    print("=== Average Spending per Receipt ===")
    print(spend_per_bon["spend_this_bon"].mean(), "\n")

    # Save outputs
    save_to_csv(daily_spend, "daily_spending.csv")
    save_to_csv(daily_items, "daily_items.csv")
    save_to_csv(spend_per_bon, "spending_per_receipt.csv")

    return daily_items, daily_spend, spend_per_bon


def top_level(df):

    # Overall Analysis
    item_stats, most_bought, most_expensive = analyze_overall_purchases(df)

    print("=== Top 10 Most Purchased Items ===")
    print(most_bought, "\n")

    print("=== Top 10 Most Expensive Items ===")
    print(most_expensive, "\n")

    # Save outputs
    save_to_csv(item_stats, "item_stats.csv")

    return item_stats, most_bought, most_expensive


if __name__ == "__main__":
    main()
