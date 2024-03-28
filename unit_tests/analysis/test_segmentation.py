import pandas as pd

from src.analysis.segmentation import k_means_centroids, rfm_scores, summarize_segments
from unit_tests.conftest import build_dataframe


def test_rfm_scores_pass_when_returns_recency_frequency_and_monetary_statistics():
    df = build_dataframe(3)
    df["Customer ID"] = [100, 100, 200]
    df["Invoice Date"] = pd.to_datetime(["2021-01-01", "2021-01-02", "2021-01-03"])
    df["Invoice ID"] = [1, 7, 12]
    df["Total Cost"] = [11, 25, 30]

    expected_stats = pd.DataFrame(
        [
            {"Customer ID": 100, "Recency": 1, "Frequency": 2, "Monetary": 36},
            {"Customer ID": 200, "Recency": 0, "Frequency": 1, "Monetary": 30},
        ]
    )

    scores = rfm_scores(df)

    assert scores.columns.to_list() == ["Customer ID", "Recency", "Frequency", "Monetary"]
    assert scores.equals(expected_stats)


def test_label_k_means_centroids_pass_when_returns_labeled_data_with_important_features():
    rfm_scores = pd.DataFrame(
        columns=["Customer ID", "Recency", "Frequency", "Monetary"],
        data=[
            [12346.0, 164, 10, 327.86],
            [12347.0, 2, 2, 1196.72],
            [12349.0, 42, 2, 1698.64],
        ],
    )

    df, importances = k_means_centroids(rfm_scores, n_clusters=2)

    # labels with segments, starting from 1
    assert df["Segment ID"].to_list() == [2, 1, 1]
    # returns most important features for each segment
    assert list(importances.keys()) == [1, 2]
    assert isinstance(importances[1], list)
    assert isinstance(importances[2], list)


def test_summarize_segments_passes_when_returns_mean_values_by_segment():
    labeled_rfm = pd.DataFrame(
        columns=["Customer ID", "Recency", "Frequency", "Monetary", "Segment ID"],
        data=[
            [12346.0, 164, 10, 327.86, 1],
            [12347.0, 2, 2, 1196.72, 2],
            [12349.0, 42, 2, 1698.64, 2],
        ],
    )

    expected_df = pd.DataFrame(
        columns=["Segment ID", "Average Recency", "Average Frequency", "Average Monetary", "Customer Count"],
        data=[
            [1, 164, 10, 327.86, 1],
            [2, 22, 2, 1447.68, 2],
        ],
    )

    assert summarize_segments(labeled_rfm).equals(expected_df)
