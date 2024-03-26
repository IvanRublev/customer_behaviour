import pandas as pd


# fixtures for database


def build_dataframe(rows_count: int = 100):
    """Returns a dataframe with N rows"""
    df = pd.read_csv("dataset/online_retail_II_100.csv")

    df["Invoice ID"] = df["Invoice"]
    df = df.drop("Invoice", axis=1)

    df["TotalCost"] = df["Quantity"] * df["Price"]

    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

    while len(df) < rows_count:
        df = pd.concat([df, df])

    # If the dataframe is larger than the desired size, trim it down
    df = df.iloc[:rows_count]

    return df
