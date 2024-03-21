from sklearn.preprocessing import StandardScaler
from deps.kmeans_feature_importance.kmeans_feature_imp import KMeansInterp


def rfm_scores(df):
    """Calculates a Recency, Frequency, and Monetary statistics (RFM) by Customer ID.

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
    rfm.rename(columns={"InvoiceDate": "Recency", "Invoice ID": "Frequency", "TotalCost": "Monetary"}, inplace=True)
    rfm["Recency"] = rfm["Recency"].astype(int)

    return rfm


def k_means_centroids(df, n_clusters):
    df = df.copy()
    X = StandardScaler().fit_transform(df)

    kms = KMeansInterp(
        n_clusters=n_clusters,
        random_state=42,
        ordered_feature_names=df.columns.tolist(),
        n_init="auto",
        max_iter=1000,
        feature_importance_method="wcss_min",
    ).fit(X)

    # make segments start from 1
    df["Segment ID"] = kms.labels_ + 1
    feature_importances = {k + 1: v for k, v in kms.feature_importances_.items()}

    return df, feature_importances


def summarize_segments(labeled_rfm):
    return (
        labeled_rfm.groupby("Segment ID")
        .agg({"Recency": "mean", "Frequency": "mean", "Monetary": "mean", "Customer ID": "count"})
        .reset_index()
        .rename(
            columns={
                "Recency": "Average Recency",
                "Frequency": "Average Frequency",
                "Monetary": "Average Monetary",
                "Customer ID": "Customer Count",
            }
        )
    )
