def rfm_statistics(df):
    """Creates a Recency, Frequency, and Monetary (RFM) statistics table.

    Parameters:
        df (pandas.DataFrame): The input dataframe containing customer data.

    Returns:
        pandas.DataFrame: The RFM statistics table.
    """
    pass

    snap_date = df[date].max()
    rfmTable = (
        df.groupby(customer_id)
        .agg(
            {
                date: lambda x: (snap_date - x.max()).days,
                transaction_id: lambda x: x.nunique(),
                "Total": lambda x: x.sum(),
            }
        )
        .reset_index()
    )
    rfmTable[date] = rfmTable[date].astype(int)
    rfmTable.rename(columns={date: "recency", transaction_id: "frequency", "Total": "monetary"}, inplace=True)
    return rfmTable
