import pandas as pd

from src.dataframe.statistics import rfm_scores
from unit_tests.conftest import build_dataframe


def test_rfm_scores_pass_when_returns_recency_frequency_and_monetary_statistics():
    df = build_dataframe(3)
    df["Customer ID"] = [100, 100, 200]
    df["InvoiceDate"] = pd.to_datetime(["2021-01-01", "2021-01-02", "2021-01-03"])
    df["Invoice ID"] = [1, 7, 12]
    df["TotalCost"] = [11, 25, 30]

    expected_stats = pd.DataFrame(
        [
            {"Customer ID": 100, "recency": 1, "frequency": 2, "monetary": 36},
            {"Customer ID": 200, "recency": 0, "frequency": 1, "monetary": 30},
        ]
    )

    scores = rfm_scores(df)

    assert scores.columns.to_list() == ["Customer ID", "recency", "frequency", "monetary"]
    assert scores.equals(expected_stats)
