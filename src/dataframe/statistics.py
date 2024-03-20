def rfm_scores(df):
    """Calculates a Recency, Frequency, and Monetary statistics (RFM) by Customer Id.

    Parameters:
        df (pandas.DataFrame): The input dataframe containing customer data.

    Calculated scores:
        - Recency: The number of days since the last purchase.
        - Frequency: The number of unique purchases.
        - Monetary: The total amount spent.

    Returns:
        pandas.DataFrame: The RFM statistics table.
    """

    snapshot_date = df["InvoiceDate"].max()

    rfm = (
        df.groupby("Customer ID")
        .agg(
            {
                "InvoiceDate": lambda dates: (snapshot_date - dates.max()).days,
                "Invoice ID": lambda invoice_ids: invoice_ids.nunique(),
                "TotalCost": lambda total_cost: total_cost.sum(),
            }
        )
        .reset_index()
    )
    rfm.set_index("Customer ID", inplace=True)
    rfm.rename(columns={"InvoiceDate": "recency", "Invoice ID": "frequency", "TotalCost": "monetary"}, inplace=True)
    rfm["recency"] = rfm["recency"].astype("Int64")

    return rfm
