from sklearn.preprocessing import StandardScaler
from deps.kmeans_feature_importance.kmeans_feature_imp import KMeansInterp


def k_means_centroids(df, n_clusters):
    data = df.copy()

    X_ = data[["recency", "frequency", "monetary"]]
    X = StandardScaler().fit_transform(X_)
    kms = KMeansInterp(
        n_clusters=n_clusters,
        random_state=42,
        ordered_feature_names=X_.columns.tolist(),
        n_init="auto",
        max_iter=1000,
        feature_importance_method="wcss_min",  # or 'unsup2sup'
    ).fit(X)

    return kms.labels_, kms.feature_importances_
