def rfm_scores(df):
    """Calculates a Recency, Frequency, and Monetary statistics (RFM) by Customer Id.

    Parameters:
        df (pandas.DataFrame): The input dataframe containing customer data.

    Calculated scores:
        - recency: The number of days since the last purchase.
        - frequency: The number of unique purchases.
        - monetary: The total amount spent.

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
    rfm.rename(columns={"InvoiceDate": "recency", "Invoice ID": "frequency", "TotalCost": "monetary"}, inplace=True)
    rfm["recency"] = rfm["recency"].astype(int)

    return rfm
