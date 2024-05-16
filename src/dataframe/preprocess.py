import pandas as pd

from src.settings import Settings


def do_prepare_dataframe(csv_path=Settings.dataset_csv_path):
    # Prepare the dataset
    df = pd.read_csv(csv_path)

    df = df.dropna()
    df = df.drop(df[df["Quantity"] <= 0].index)
    df = df.drop_duplicates()

    df.rename(
        {
            "Invoice": "Invoice ID",
            "StockCode": "Stock Code",
            "Description": "Stock Description",
            "InvoiceDate": "Invoice Date",
        },
        axis=1,
        inplace=True,
    )

    df["Total Cost"] = df["Quantity"] * df["Price"]

    # we encode the countries to a numerical value to prevent correlation analysis crash
    df, code_by_country = encode_countries(df)

    df = cast_column_types(df)

    # sort for time series analysis
    df = df.sort_values("Invoice Date")

    df = reject_outliers_by_iqr(df, "Total Cost")

    return df, code_by_country


def cast_column_types(df):
    """Casts the column types of the given DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to be processed.

    Returns:
        pd.DataFrame: The processed DataFrame with updated column types.
    """
    df["Invoice ID"] = pd.Categorical(df["Invoice ID"])
    df["Stock Code"] = pd.Categorical(df["Stock Code"])
    df["Stock Description"] = df["Stock Description"].astype("string")
    df["Quantity"] = df["Quantity"].astype("Int64")
    df["Invoice Date"] = pd.to_datetime(df["Invoice Date"])
    df["Price"] = df["Price"].astype("Float64")
    df["Customer ID"] = df["Customer ID"].astype("Float64")
    df["Country"] = pd.Categorical(df["Country"])

    return df


def encode_countries(df):
    """Encode the 'Country' column in the given DataFrame using numerical codes.

    Parameters:
        df (pandas.DataFrame): The DataFrame containing the 'Country' column to be encoded.

    Returns:
        tuple: A tuple containing the updated DataFrame with the 'Country' column encoded,
        and a dictionary mapping countries to their corresponding codes.
    """

    code_by_country = {country: code + 1 for code, country in enumerate(df["Country"].unique())}
    df.loc[:, "Country"] = df.loc[:, "Country"].map(code_by_country)
    df["Country"] = pd.Categorical(df["Country"])
    return df, code_by_country


def decode_countries(df, code_by_country):
    """Decode the 'Country' column in the given DataFrame from numerical codes to contry names.

    Parameters:
        df (pandas.DataFrame): The DataFrame containing the 'Country' column to be decoded.
        code_by_country (dict): A dictionary mapping countries to their corresponding codes.

    Returns:
        pandas.DataFrame: The DataFrame with the 'Country' column decoded in "Country name (code)" format.
    """

    country_by_code = {code: f"{country} ({code})" for country, code in code_by_country.items()}
    df.loc[:, "CountryStr"] = pd.Categorical(df.loc[:, "Country"].map(country_by_code))
    df.drop("Country", axis=1, inplace=True)
    df.rename(columns={"CountryStr": "Country"}, inplace=True)

    return df


def reject_outliers_by_iqr(df, column):
    """Reject outlier values by given dataframe's column using the Interquartile Range (IQR) method.

    Parameters:
        df (pandas.DataFrame): The DataFrame from which to filter outliers.
        column (str): The name of the column on which to filter outliers.

    Returns:
        pandas.DataFrame: The DataFrame with the outliers removed.
    """

    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
