from src.dataframe.statistics import rfm_statistics
from unit_tests.conftest import build_dataframe


# def test_rfm_statistics_pass_when_returns_recency_frequency_and_monetary_statistics():
#     df = build_dataframe(2)
#     df["CustomerID"] = [100, 100]

#     max_date = df["InvoiceDate"].max()
#     invoice_date1, invoice_date2 = df["InvoiceDate"]
#     transaction_id1, transaction_id2 = df["Transaction ID"]

#     expected_rfm_statistics = DataFrame(
#         [
#             {
#                 "CustomerID": 100,
#                 "recency": [invoice_date1 - max_date, invoice_date2 - max_date],
#                 "frequency": 1,
#                 "monetary": 1,
#             }
#         ]
#     )
