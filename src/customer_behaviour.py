import pandas as pd
import streamlit as st
from streamlit_ydata_profiling import st_profile_report
from ydata_profiling import ProfileReport

from src.dataframe.preprocess import cast_column_types, encode_countries, reject_outliers_by_iqr
from src.dataframe.sample import take_sample
from src.logger import logger
from src.reports_cache import get_cached_report
from src.settings import Settings


def customer_behaviour_app():
    logger.info("UI loop")

    # Prepare the dataset
    df = pd.read_csv(Settings.dataset_csv_path)

    df = df.drop("Invoice", axis=1)

    df = df.dropna()
    df = df.drop(df[df["Quantity"] <= 0].index)

    df = df.drop_duplicates()

    # we encode the countries to a numerical value to prevent correlation analysis crash
    df, code_by_country = encode_countries(df)

    df = cast_column_types(df)

    # sort for time series analysis
    df = df.sort_values("InvoiceDate")

    df = reject_outliers_by_iqr(df, "TotalCost")

    # Configure UI
    icon = "📊"
    st.set_page_config(page_title=Settings.app_description, page_icon=icon, layout="wide")
    st.sidebar.title(f"{icon} {Settings.app_name}")
    side = st.sidebar.selectbox("Please, choose a Report", ["Home", "Data Exploration"])

    # Apply filters
    df, filter_key = _apply_sidebar_filters(df, code_by_country)

    if side == "Home":
        st.title(Settings.app_description, anchor="home")

        dataset_link = "[Online Retail II dataset](https://archive.ics.uci.edu/dataset/502/online+retail+ii)"
        st.markdown(f"""
                    In this project, we will analyze customer behavior using :
                    * Exploratory Data Analysis
                    * Customer Segmentation using RFM Analysis
                    
                    ## Dataset
                    
                    As an example, we use the {dataset_link} of 1 million records.
                    > Chen,Daqing. (2019). Online Retail II. UCI Machine Learning Repository. https://doi.org/10.24432/C5CG6D.

                    """)

    elif side == "Data Exploration":
        st.title("Data Exploration", anchor="data-exploration")

        sample, description = take_sample(df)
        st.caption(description)

        cache_key = f"data_exploration{filter_key}"
        report = get_cached_report(
            cache_key,
            lambda: ProfileReport(
                sample,
                explorative=True,
                tsmode=True,
                # Setting what variables are time series
                type_schema={
                    "TotalCost": "timeseries",
                    "Quantity": "timeseries",
                },
                missing_diagrams={
                    "bar": False,
                    "matrix": False,
                    "heatmap": False,
                },
                correlations={
                    "auto": {"calculate": True},
                    "pearson": {"calculate": False},
                    "spearman": {"calculate": False},
                    "kendall": {"calculate": False},
                    "phi_k": {"calculate": True},
                    "cramers": {"calculate": False},
                },
            ),
        )

        st_profile_report(report)


def _apply_sidebar_filters(df, code_by_country):
    logger.info(f"Applying sidebar filters to dataframe of shape: {df.shape}")

    filter_key = ""

    # ---
    st.sidebar.subheader("📅 Date Range")

    min_date, max_date = df.InvoiceDate.dt.date.min(), df.InvoiceDate.dt.date.max()
    date = st.sidebar.date_input("Select your date range", (min_date, max_date))
    if len(date) == 2:
        if date[0] >= min_date and date[1] <= max_date:
            df = df[(df["InvoiceDate"] >= pd.to_datetime(date[0])) & (df["InvoiceDate"] <= pd.to_datetime(date[1]))]
        else:
            st.error(
                f"Error, your chosen date is out of range, \
                    our dataset record the transaction between {min_date} to {max_date}",
                icon="🚨",
            )
        logger.info(f"Date range: {date}")

        filter_key += f"_date{date[0]}_{date[1]}_" if date else ""

    # ---
    st.sidebar.subheader("🏠 Country Filter")

    code_by_country = {f"{name} ({code})": code for name, code in code_by_country.items()}
    code_by_country = {**code_by_country, "None": None}
    countries_list = list(code_by_country.keys())
    countries_list.remove("None")
    countries_list.insert(0, "None")
    country = st.sidebar.selectbox(
        "Select the specific country you wish to analyse or select none for all countries:",
        countries_list,
    )
    logger.info(f"Country: {country}")

    country_code = code_by_country[country]
    if country_code:
        df = df[df["Country"] == country_code]
    logger.info(f"Country code: {country_code}")

    filter_key += f"_country{country_code}_" if country_code else ""

    return df, filter_key
