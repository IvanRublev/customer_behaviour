import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_ydata_profiling import st_profile_report
from ydata_profiling import ProfileReport

from src.dataframe.preprocess import decode_countries
from src.dataframe.sample import take_sample
from src.logger import logger
from src.reports_cache import get_cached_report, is_report_cached
from src.settings import Settings


def maybe_initialize_session_state(st):
    if "filters_disabled" not in st.session_state:
        st.session_state["filters_disabled"] = True
        logger.info(f"After init, st.session_state.filters_disabled: {st.session_state.filters_disabled}")


def render(st, df, code_by_country):
    st.title("Data Exploration", anchor="data-exploration")

    # Apply filters
    df, filter_key = _apply_data_exploration_sidebar_filters(df, code_by_country)

    logger.info(f"Data Exploration filter_key: {filter_key}, \
cached: {is_report_cached(st.session_state, filter_key)}")

    if not is_report_cached(st.session_state, filter_key):
        _disable_sidebar_filters()

    st.header("Full dataset statistics")

    charts_col1, charts_col2 = st.columns(2)

    with charts_col1:
        users_by_country = _users_by_country(df, code_by_country)
        chart = px.bar(users_by_country, x="Country", y="Users count", title="Users per Country")
        chart.update_traces(yhoverformat=Settings.plot_integer_format)
        st.plotly_chart(chart, use_container_width=True)

    with charts_col2:
        revenue_by_country = _revenue_by_country(df, code_by_country)
        chart = px.bar(revenue_by_country, x="Country", y="Revenue", title="Revenue per Country")
        chart.update_traces(yhoverformat=Settings.plot_currency_format)
        st.plotly_chart(chart, use_container_width=True)

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

    _enable_sidebar_filters()


@st.cache_data
def _users_by_country(df, code_by_country):
    users_by_country = decode_countries(df, code_by_country)
    users_by_country = users_by_country["Country"].value_counts()
    # Convert the Series to a DataFrame
    users_by_country = users_by_country.reset_index()
    users_by_country.columns = ["Country", "Users count"]
    return users_by_country


@st.cache_data
def _revenue_by_country(df, code_by_country):
    revenue_by_country = decode_countries(df, code_by_country)
    revenue_by_country = revenue_by_country.groupby("Country")["TotalCost"].sum()
    # Convert the Series to a DataFrame
    revenue_by_country = revenue_by_country.reset_index()
    revenue_by_country.columns = ["Country", "Revenue"]
    return revenue_by_country


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
