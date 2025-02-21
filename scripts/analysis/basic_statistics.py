def display_basic_statistics(df):
    print("=== First Few Rows ===")
    print(df.head(), "\n")

    print("=== Column Names and Data Types ===")
    print(df.dtypes, "\n")

    print("=== Number of Rows and Columns ===")
    print(df.shape, "\n")

    print("=== Basic Statistics ===")
    print(df.describe(), "\n")

    print("=== Unique Items ===")
    print(df["item_name"].unique(), "\n")
