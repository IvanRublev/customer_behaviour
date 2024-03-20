import pandas as pd


def cast_column_types(df):
    """Casts the column types of the given DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to be processed.

    Returns:
        pd.DataFrame: The processed DataFrame with updated column types.
    """
    df["StockCode"] = pd.Categorical(df["StockCode"])
    df["Description"] = df["Description"].astype("string")
    df["Quantity"] = df["Quantity"].astype("Int64")
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["Price"] = df["Price"].astype("Float64")
    df["Customer ID"] = df["Customer ID"].astype("Float64")
    df["Country"] = pd.Categorical(df["Country"])
    df["TotalCost"] = df["Quantity"] * df["Price"]

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
    df["Country"] = df["Country"].map(code_by_country)
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
    df["Country"] = df["Country"].map(country_by_code)

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
