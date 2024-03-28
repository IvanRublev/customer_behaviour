import pandas as pd
import streamlit as st

from src.logger import logger


def append_filters_title(title, dates, country, rejected_country):
    """Appends the selected filters to the title.

    Args:
        title (str): The title to be appended to.
        dates (tuple): The date range.
        country (str): The selected country.
        rejected_country (str): The rejected country (if any).

    Returns:
        str: The updated title.
    """

    if dates:
        title += f" ({dates[0]} to {dates[1]})"

    if country:
        title += f" for {country}"

    if rejected_country:
        title += " UK rejected"

    return title


def enable_sidebar_filters():
    # we rerun the app to make Input widgets pickup the disabled state
    # if flag is not changing, we don't want to rerun the app
    if st.session_state.filters_disabled:
        st.session_state["filters_disabled"] = False
        logger.info(f"After enable sidebar filters, \
st.session_state.filters_disabled: {st.session_state.filters_disabled}, return")
        st.rerun()


def disable_sidebar_filters():
    if not st.session_state.filters_disabled:
        st.session_state["filters_disabled"] = True
        logger.info(
            f"After disable sidebar filters, \
st.session_state.filters_disabled: {st.session_state.filters_disabled}, rerun"
        )
        st.rerun()


def date_range_filter(df, filter_key=""):
    """Date range input that filters the DataFrame based on the selection.

    Args:
        df (pandas.DataFrame): The DataFrame to be filtered.
        filter_key (str, optional): The filter cache key to be appended to. Defaults to "".

    Returns:
        tuple: A tuple containing the filtered DataFrame and the updated filter key.
    """

    st.sidebar.subheader("📅 Date Range")

    min_date, max_date = df["Invoice Date"].dt.date.min(), df["Invoice Date"].dt.date.max()
    date = st.sidebar.date_input(
        "Select your date range",
        (min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        disabled=st.session_state.filters_disabled,
    )

    if len(date) == 2 and (date[0] != min_date or date[1] != max_date):
        if date[0] >= min_date and date[1] <= max_date:
            df = do_filter_by_date(df, date)
            filter_key += f"_date{date[0]}_{date[1]}_" if date else ""
        else:
            date = None
            st.error(
                f"Error, your chosen date is out of range, \
our dataset record the transaction between {min_date} to {max_date}",
                icon="🚨",
            )
    else:
        date = None

    logger.info(f"Date range: {date}")

    return df, filter_key, date


@st.cache_data
def do_filter_by_date(df, date):
    return df[(df["Invoice Date"] >= pd.to_datetime(date[0])) & (df["Invoice Date"] <= pd.to_datetime(date[1]))]


def country_filter(df, code_by_country, filter_key=""):
    """Country dropdown that filters the DataFrame based on the selected country.

    Args:
        df (pandas.DataFrame): The DataFrame to be filtered.
        code_by_country (dict): A dictionary mapping country names to country codes.
        filter_key (str, optional): The filter cache key to be appended. Defaults to "".

    Returns:
        tuple: A tuple containing the filtered DataFrame, the updated filter key,
        the selected country, and the rejected country.
    """

    st.sidebar.subheader("🏠 Country Filter")

    uk_name, uk_code = rejected_uk_country(code_by_country)
    reject_uk = st.sidebar.toggle("Reject UK", True, disabled=st.session_state.filters_disabled)

    code_by_country = {
        f"{name} ({code})": code
        for name, code in code_by_country.items()
        if not reject_uk or (reject_uk and name != uk_name)
    }
    code_by_country = {**code_by_country, "None": None}
    countries_list = list(code_by_country.keys())
    countries_list.remove("None")
    countries_list.insert(0, "None")
    country = st.sidebar.selectbox(
        "Select the specific country you wish to analyse or select None for all countries:",
        countries_list,
        disabled=st.session_state.filters_disabled,
    )
    logger.info(f"Country: {country}")

    country_code = code_by_country[country]
    reject_code = uk_code if reject_uk and not country_code else None
    df = do_filter_by_country_code(df, country_code, reject_code)

    logger.info(f"Country code: {country_code}")

    filter_key = country_filter_key(filter_key, country_code, reject_code)

    # Prepare titles
    if country == "None":
        country = None

    rejected_country = uk_name if reject_code else None

    return df, filter_key, country, rejected_country


def rejected_uk_country(code_by_country):
    """Get the name and code of the United Kingdom.

    Args:
        code_by_country (dict): A dictionary mapping country names to country codes.

    Returns:
        tuple: A tuple containing the name and code of the United Kingdom.
    """
    uk_name = "United Kingdom"
    uk_code = code_by_country[uk_name]

    return uk_name, uk_code


def country_filter_key(filter_key, country_code, reject_country_code):
    """Append a country suffix to filter key based on the provided country code and reject country code.

    Args:
        filter_key (str): The base filter key.
        country_code (str): The country code to include in the filter key.
        reject_country_code (str): The reject country code to include in the filter key.

    Returns:
        str: The constructed filter key.

    """
    filter_key += f"_country{country_code}_" if country_code else ""
    filter_key += f"_rejected_country{reject_country_code}_" if reject_country_code else ""
    return filter_key


@st.cache_data
def do_filter_by_country_code(df, country_code, reject_country_code):
    """Filters the DataFrame based on the given country code and reject country code.

    Args:
        df (pandas.DataFrame): The DataFrame to be filtered.
        country_code (str): The country code to filter by.
        reject_country_code (str): The country code to reject by.

    Returns:
        pandas.DataFrame: The filtered DataFrame.
    """
    if country_code:
        df = df[df["Country"] == country_code]

    if reject_country_code:
        df = df[df["Country"] != reject_country_code]

    return df
