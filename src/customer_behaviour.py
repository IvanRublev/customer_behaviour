import pandas as pd
import streamlit as st

from src.dataframe.preprocess import cast_column_types, encode_countries, reject_outliers_by_iqr
from src.logger import logger
from src.settings import Settings
from src.pages import customer_segmentation, data_exploration, home


@st.cache_data
def _prepare_dataframe():
    # Prepare the dataset
    df = pd.read_csv(Settings.dataset_csv_path)

    df["Invoice ID"] = df["Invoice"]
    df = df.drop("Invoice", axis=1)

    df["TotalCost"] = df["Quantity"] * df["Price"]

    df = df.dropna()
    df = df.drop(df[df["Quantity"] <= 0].index)

    df = df.drop_duplicates()

    # we encode the countries to a numerical value to prevent correlation analysis crash
    df, code_by_country = encode_countries(df)

    df = cast_column_types(df)

    # sort for time series analysis
    df = df.sort_values("InvoiceDate")

    df = reject_outliers_by_iqr(df, "TotalCost")

    return df.copy(), code_by_country


def customer_behaviour_app():
    logger.info("UI loop")

    # Configure UI
    icon = "🌎"
    st.set_page_config(page_title=Settings.app_description, page_icon=icon, layout="wide")
    st.sidebar.title(f"{icon} {Settings.app_name}")
    side = st.sidebar.selectbox("Please, choose a Report", ["Home", "Data Exploration", "Customer Segmentation"])

    for page in [customer_segmentation, data_exploration, home]:
        page.maybe_initialize_session_state(st)

    df, code_by_country = _prepare_dataframe()

    if side == "Home":
        home.render(st)

    elif side == "Data Exploration":
        data_exploration.render(st, df=df, code_by_country=code_by_country)

    elif side == "Customer Segmentation":
        customer_segmentation.render(st, df=df, code_by_country=code_by_country)
