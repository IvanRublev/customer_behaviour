import pandas as pd
from pandas.api import types

from src.dataframe.preprocess import cast_column_types, decode_countries, encode_countries, reject_outliers_by_iqr
from unit_tests.conftest import build_dataframe


def test_cast_column_types_pass_when_return_columns_with_appropriate_types():
    df = build_dataframe()

    df = cast_column_types(df)

    assert isinstance(df["Invoice ID"].dtype, pd.CategoricalDtype)
    assert isinstance(df["StockCode"].dtype, pd.CategoricalDtype)
    assert isinstance(df["Description"].dtype, pd.StringDtype)
    assert isinstance(df["Quantity"].dtype, pd.Int64Dtype)
    assert types.is_datetime64_dtype(df["InvoiceDate"].dtype)
    assert isinstance(df["Price"].dtype, pd.Float64Dtype)
    assert isinstance(df["Customer ID"].dtype, pd.Float64Dtype)  # manually casted
    assert isinstance(df["Country"].dtype, pd.CategoricalDtype)


def test_encode_countries_pass_when_substitutes_countries_with_numbers():
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


def test_decode_countries_pass_when_country_codes_are_replaced_with_names():
    df = build_dataframe(10)
    df["Country"] = [1, 2, 3, 4, 5, 6, 3, 7, 8, 9]
    code_by_country = {
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

    df = decode_countries(df, code_by_country)

    assert df["Country"].tolist() == [
        "United Kingdom (1)",
        "Germany (2)",
        "France (3)",
        "Spain (4)",
        "Portugal (5)",
        "Italy (6)",
        "France (3)",
        "Switzerland (7)",
        "Austria (8)",
        "Netherlands (9)",
    ]


def test_reject_outliers_by_iqr_pass_when_removes_outliers():
    df = build_dataframe(10)
    df["Quantity"] = [1, 2, 3, 4, 500, 6, 20, 8, 9, 10]

    df = reject_outliers_by_iqr(df, "Quantity")

    assert df["Quantity"].tolist() == [1, 2, 3, 4, 6, 8, 9, 10]
