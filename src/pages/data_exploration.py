import plotly.express as px
import streamlit as st
from streamlit_ydata_profiling import st_profile_report
from ydata_profiling import ProfileReport

from src.dataframe.preprocess import decode_countries
from src.dataframe.sample import take_sample
from src.logger import logger
from src.pages.components.sidebar import (
    append_filters_title,
    country_filter,
    date_range_filter,
    disable_sidebar_filters,
    enable_sidebar_filters,
)
from src.reports_cache import get_cached_report, is_report_cached
from src.settings import Settings


def maybe_prepare_data_on_disk(df, code_by_country):
    pass


def maybe_initialize_session_state(st):
    if "filters_disabled" not in st.session_state:
        st.session_state["filters_disabled"] = True
        logger.info(f"After init, st.session_state.filters_disabled: {st.session_state.filters_disabled}")


def render(st, df, code_by_country):
    # Apply filters
    df, filter_key, dates, country, rejected_country = _apply_sidebar_filters(df, code_by_country)

    st.title(append_filters_title("Data Exploration", dates, country, rejected_country), anchor="data-exploration")

    logger.info(f"Data Exploration filter_key: {filter_key}, \
cached: {is_report_cached(st.session_state, filter_key)}")

    if not is_report_cached(st.session_state, filter_key):
        disable_sidebar_filters()

    st.header("Full dataset statistics")

    charts_col1, charts_col2 = st.columns(2)

    with charts_col1:
        customers_by_country = _customers_by_country(df, code_by_country)
        fig = px.bar(customers_by_country, x="Country", y="Customers count", title="Customers per Country")
        fig.update_traces(yhoverformat=Settings.plot_integer_format)
        st.plotly_chart(fig, use_container_width=True)

    with charts_col2:
        revenue_by_country = _revenue_by_country(df, code_by_country)
        fig = px.bar(revenue_by_country, x="Country", y="Revenue", title="Revenue per Country")
        fig.update_traces(yhoverformat=Settings.plot_currency_format)
        st.plotly_chart(fig, use_container_width=True)

    st.header("📊 Sample analysis")

    # Take sample for analysis
    sample, description = take_sample(df)

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

    if description:
        st.markdown(f"> {description}")

    st_profile_report(report)
    logger.info("Data Exploration report displayed")

    enable_sidebar_filters()


@st.cache_data
def _customers_by_country(df, code_by_country):
    customers_by_country = decode_countries(df, code_by_country)
    customers_by_country = customers_by_country["Country"].value_counts()
    # Convert the Series to a DataFrame
    customers_by_country = customers_by_country.reset_index()
    customers_by_country.columns = ["Country", "Customers count"]
    return customers_by_country


@st.cache_data
def _revenue_by_country(df, code_by_country):
    revenue_by_country = decode_countries(df, code_by_country)
    revenue_by_country = revenue_by_country.groupby("Country", observed=True)["TotalCost"].sum()
    # Convert the Series to a DataFrame
    revenue_by_country = revenue_by_country.reset_index()
    revenue_by_country.columns = ["Country", "Revenue"]
    return revenue_by_country


def _apply_sidebar_filters(df, code_by_country):
    logger.info(f"Applying data exploration sidebar filters to dataframe of shape: {df.shape}")

    filter_key = "data_exploration_"

    df, filter_key, dates = date_range_filter(df, filter_key)
    df, filter_key, country, rejected_country = country_filter(df, code_by_country, filter_key)

    return df, filter_key, dates, country, rejected_country
