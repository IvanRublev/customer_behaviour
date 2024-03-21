from sklearn.preprocessing import StandardScaler
from deps.kmeans_feature_importance.kmeans_feature_imp import KMeansInterp


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

    df["segment"] = kms.labels_

    return df, kms.feature_importances_
