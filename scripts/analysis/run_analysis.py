import os

from load_data import load_receipts_data
from basic_statistics import display_basic_statistics
from daily_spending import calculate_daily_spending, calculate_daily_items
from receipt_analysis import spending_per_receipt
from item_analysis import analyze_item_purchases
from output_results import save_to_csv


def main():
    df = load_receipts_data()

    display_basic_statistics(df)

    # Daily Spending & Items
    daily_spend = calculate_daily_spending(df)
    daily_items = calculate_daily_items(df)

    print("=== Spending per Day ===")
    print(daily_spend, "\n")

    print("=== Number of Items Purchased per Day ===")
    print(daily_items, "\n")

    # Spending per Receipt
    spend_per_bon = spending_per_receipt(df)
    print("=== Spending per Receipt ===")
    print(spend_per_bon, "\n")

    # Item Analysis
    item_stats, most_bought, most_expensive = analyze_item_purchases(df)

    print("=== Top 10 Most Purchased Items ===")
    print(most_bought, "\n")

    print("=== Top 10 Most Expensive Items ===")
    print(most_expensive, "\n")

    # Save outputs
    save_to_csv(item_stats, "item_stats.csv")
    save_to_csv(daily_spend, "daily_spending.csv")
    save_to_csv(daily_items, "daily_items.csv")
    save_to_csv(spend_per_bon, "spending_per_receipt.csv")


if __name__ == "__main__":
    main()
