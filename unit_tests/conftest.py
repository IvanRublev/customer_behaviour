import pandas as pd

from src.customer_behaviour import do_prepare_dataframe

# fixtures for database


def build_dataframe(rows_count: int = 100):
    """Returns a dataframe with N rows"""
    df, _ = do_prepare_dataframe("dataset/online_retail_II_100.csv")

    while len(df) < rows_count:
        df = pd.concat([df, df])

    # If the dataframe is larger than the desired size, trim it down
    df = df.iloc[:rows_count]

    return df
