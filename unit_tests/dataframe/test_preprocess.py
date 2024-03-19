import pandas as pd
from pandas.api import types

from src.dataframe.preprocess import encode_countries, reject_outliers_by_iqr, preprocess
from unit_tests.conftest import build_dataframe


class TestPreprocess:
    def test_pass_when_returns_columns_for_analysis(self):
        df = build_dataframe()

        df = preprocess(df)

        assert list(df.columns) == [
            "StockCode",
            "Description",
            "Quantity",
            "InvoiceDate",
            "Price",
            "Customer ID",
            "Country",
            "TotalCost",
        ]

        # total cost is quantity * price
        assert (df["TotalCost"] == df["Quantity"] * df["Price"]).all()

    def test_pass_when_return_columns_with_appropriate_types(self):
        df = build_dataframe()

        df = preprocess(df)

        assert isinstance(df["StockCode"].dtype, pd.CategoricalDtype)
        assert isinstance(df["Description"].dtype, pd.StringDtype)
        assert isinstance(df["Quantity"].dtype, pd.Int64Dtype)
        assert types.is_datetime64_dtype(df["InvoiceDate"].dtype)
        assert isinstance(df["Price"].dtype, pd.Float64Dtype)
        assert isinstance(df["Customer ID"].dtype, pd.CategoricalDtype)  # manually casted
        assert isinstance(df["Country"].dtype, pd.CategoricalDtype)

    def test_pass_when_removes_missing_values(self):
        df = build_dataframe()

        # introduce missing values
        df.loc[0, "StockCode"] = None
        df.loc[11, "Country"] = None
        df.loc[37, "Price"] = None

        df = preprocess(df)

        assert df.isna().sum().sum() == 0

    def test_pass_when_removes_negative_or_zero_quantities(self):
        df = build_dataframe()

        # introduce negative quantities
        df.loc[0, "Quantity"] = -1
        df.loc[5, "Quantity"] = 0
        df.loc[11, "Quantity"] = -2
        df.loc[37, "Quantity"] = -3

        df = preprocess(df)

        assert (df["Quantity"] >= 0).all()

    def test_pass_when_removes_duplicate_rows(self):
        df = build_dataframe()

        # introduce duplicate rows
        df = pd.concat([df, df])

        df = preprocess(df)

        assert df.duplicated().sum() == 0

    def test_pass_when_sorts_data_by_invoice_date(self):
        df = build_dataframe()
        # shuffle rows
        df = df.sample(frac=1).reset_index(drop=True)

        df = preprocess(df)

        assert df["InvoiceDate"].is_monotonic_increasing
        assert df["InvoiceDate"].min() == df["InvoiceDate"].iloc[0]
        assert df["InvoiceDate"].max() == df["InvoiceDate"].iloc[-1]


class TestEncodeCountries:
    def test_pass_when_substitutes_countries_with_numbers(self):
        df = build_dataframe(10)
        df["Country"] = [
            "United Kingdom",
            "Germany",
            "France",
            "Spain",
            "Portugal",
            "Italy",
            "France",
            "Switzerland",
            "Austria",
            "Netherlands",
        ]

        df, code_by_country = encode_countries(df)

        assert isinstance(df["Country"].dtype, pd.CategoricalDtype)
        assert df["Country"].tolist() == [1, 2, 3, 4, 5, 6, 3, 7, 8, 9]
        assert code_by_country == {
            "United Kingdom": 1,
            "Germany": 2,
            "France": 3,
            "Spain": 4,
            "Portugal": 5,
            "Italy": 6,
            "Switzerland": 7,
            "Austria": 8,
            "Netherlands": 9,
        }


class TestRejectOutliersByIQR:
    def test_pass_when_removes_outliers_for_specified_column(self):
        df = build_dataframe(10)
        df["Quantity"] = [1, 2, 3, 4, 500, 6, 20, 8, 9, 10]

        df = reject_outliers_by_iqr(df, "Quantity")

        assert df["Quantity"].tolist() == [1, 2, 3, 4, 6, 8, 9, 10]
