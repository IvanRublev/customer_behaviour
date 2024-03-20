import pandas as pd
import streamlit as st
from streamlit_ydata_profiling import st_profile_report
from ydata_profiling import ProfileReport

from src.dataframe.preprocess import cast_column_types, encode_countries, reject_outliers_by_iqr
from src.dataframe.sample import take_sample
from src.logger import logger
from src.reports_cache import get_cached_report, is_report_cached
from src.settings import Settings


@st.cache_data
def _prepare_dataframe():
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

    return df.copy(), code_by_country


def customer_behaviour_app():
    logger.info("UI loop")

    # Configure UI
    icon = "📊"
    st.set_page_config(page_title=Settings.app_description, page_icon=icon, layout="wide")
    st.sidebar.title(f"{icon} {Settings.app_name}")
    side = st.sidebar.selectbox("Please, choose a Report", ["Home", "Data Exploration"])

    _maybe_initialize_session_state()

    df, code_by_country = _prepare_dataframe()

    if side == "Home":
        st.title(Settings.app_description, anchor="home")

        dataset_link = "[Online Retail II dataset](https://archive.ics.uci.edu/dataset/502/online+retail+ii)"
        st.markdown(f"""
                    In this project, we will analyze customer behavior using :
                    * Exploratory Data Analysis
                    * Customer Segmentation using RFM Analysis
                    
                    ## Dataset
                    
                    As an example, we use the {dataset_link} of ~1 million records.
                    > Chen,Daqing. (2019). Online Retail II. UCI Machine Learning Repository. https://doi.org/10.24432/C5CG6D.

                    """)

    elif side == "Data Exploration":
        st.title("Data Exploration", anchor="data-exploration")

        # Apply filters
        df, filter_key = _apply_data_exploration_sidebar_filters(df, code_by_country)

        logger.info(f"Data Exploration filter_key: {filter_key}, \
cached: {is_report_cached(st.session_state, filter_key)}")

        if not is_report_cached(st.session_state, filter_key):
            _disable_sidebar_filters()

        # Take sample for analysis
        sample, description = take_sample(df)
        st.caption(description)

        report = get_cached_report(
            session_state=st.session_state,
            report_name=filter_key,
            generator_fun=lambda: ProfileReport(
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
        logger.info("Data Exploration report displayed")

        _enable_sidebar_filters()


def _apply_data_exploration_sidebar_filters(df, code_by_country):
    logger.info(f"Applying data exploration sidebar filters to dataframe of shape: {df.shape}")

    filter_key = "data_exploration_"

    # ---
    st.sidebar.subheader("📅 Date Range")

    min_date, max_date = df.InvoiceDate.dt.date.min(), df.InvoiceDate.dt.date.max()
    date = st.sidebar.date_input(
        "Select your date range", (min_date, max_date), disabled=st.session_state.filters_disabled
    )

    if len(date) == 2 and date[0] != min_date and date[1] != max_date:
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
        disabled=st.session_state.filters_disabled,
    )
    logger.info(f"Country: {country}")

    country_code = code_by_country[country]
    if country_code:
        df = df[df["Country"] == country_code]
    logger.info(f"Country code: {country_code}")

    filter_key += f"_country{country_code}_" if country_code else ""

    return df, filter_key


def _maybe_initialize_session_state():
    if "filters_disabled" not in st.session_state:
        st.session_state["filters_disabled"] = True
        logger.info(f"After init, st.session_state.filters_disabled: {st.session_state.filters_disabled}")


def _enable_sidebar_filters():
    # we rerun the app to make Input widgets pickup the disabled state
    # if flag is not changing, we don't want to rerun the app
    if st.session_state.filters_disabled:
        st.session_state["filters_disabled"] = False
        logger.info(f"After enable sidebar filters, \
st.session_state.filters_disabled: {st.session_state.filters_disabled}, return")
        st.rerun()


def _disable_sidebar_filters():
    if not st.session_state.filters_disabled:
        st.session_state["filters_disabled"] = True
        logger.info(
            f"After disable sidebar filters, \
st.session_state.filters_disabled: {st.session_state.filters_disabled}, rerun"
        )
        st.rerun()
