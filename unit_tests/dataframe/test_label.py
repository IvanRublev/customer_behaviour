import pandas as pd

from src.dataframe.label import k_means_centroids
from unit_tests.conftest import build_dataframe


def test_label_k_means_centroids_pass_when_returns_labels():
    rfm_scores = pd.DataFrame(
        [
            {"Customer ID": 100, "recency": 1, "frequency": 2, "monetary": 36},
            {"Customer ID": 200, "recency": 0, "frequency": 1, "monetary": 30},
        ]
    )
    rfm_scores.set_index("Customer ID", inplace=True)

    expected_centroids = pd.DataFrame(
        [
            {"centroid": 0, "feature": "monetary", "weight": 0.3},
            {"centroid": 1, "feature": "frequency", "monetary": 0.2},
        ]
    )

    assert k_means_centroids(rfm_scores, n_clusters=2).equals(expected_centroids)
