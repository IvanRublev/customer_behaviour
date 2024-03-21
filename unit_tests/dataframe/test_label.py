import pandas as pd

from src.dataframe.label import k_means_centroids
from unit_tests.conftest import build_dataframe


def test_label_k_means_centroids_pass_when_returns_labels():
    rfm_scores = pd.DataFrame(
        columns=["Customer ID", "recency", "frequency", "monetary"],
        data=[
            [12346.0, 164, 10, 327.86],
            [12347.0, 2, 2, 1196.72],
            [12349.0, 42, 2, 1698.64],
        ],
    )
    rfm_scores.set_index("Customer ID", inplace=True)

    df, importances = k_means_centroids(rfm_scores, n_clusters=2)

    # labels with segments
    assert df["segment"].to_list() == [1, 0, 0]
    # returns most important features for each segment
    assert list(importances.keys()) == [0, 1]
    assert isinstance(importances[0], list)
    assert isinstance(importances[1], list)
