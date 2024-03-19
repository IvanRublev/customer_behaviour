import pandas as pd


def preprocess(df):
    """Cleans and enreaches the given DataFrame

    Operations:
        drops unused columns
        removes missing values
        removes negative or zero quantities
        adds total cost column
        converts data types
        sorts data by invoice date
    """

    df = df.drop("Invoice", axis=1)
    df = df.dropna()
    df = df.drop(df[df["Quantity"] <= 0].index)

    df = df.drop_duplicates()

    df["StockCode"] = pd.Categorical(df["StockCode"])
    df["Description"] = df["Description"].astype("string")
    df["Quantity"] = df["Quantity"].astype("Int64")
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["Price"] = df["Price"].astype("Float64")
    df["Customer ID"] = pd.Categorical(df["Customer ID"])
    df["Country"] = pd.Categorical(df["Country"])
    df["TotalCost"] = df["Quantity"] * df["Price"]

    df = df.sort_values("InvoiceDate")

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


def reject_outliers_by_iqr(df, column):
    """Filters out outliers from the given DataFrame using the Interquartile Range (IQR) method.

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
