import streamlit as st

from src.dataframe.preprocess import do_prepare_dataframe
from src.logger import logger
from src.settings import Settings
from src.pages import customer_segmentation, data_exploration, home, market_basket_analysis

PAGES = [customer_segmentation, data_exploration, home, market_basket_analysis]


@st.cache_data
def _prepare_dataframe():
    return do_prepare_dataframe()


def customer_behaviour_app():
    logger.info("UI loop")

    # Configure UI
    icon = "🌎"
    st.set_page_config(page_title=Settings.app_description, page_icon=icon, layout="wide")

    st.sidebar.title(f"{icon} {Settings.app_name}")
    side = st.sidebar.selectbox(
        "Please, choose a Report", ["Home", "Data Exploration", "Customer Segmentation", "Market Basket Analysis"]
    )
    if side != "Home":
        st.sidebar.markdown("---")

    df, code_by_country = _prepare_dataframe()

    for page in PAGES:
        page.maybe_initialize_session_state(st)

    if side == "Home":
        home.render(st)

    elif side == "Data Exploration":
        data_exploration.render(st, df=df, code_by_country=code_by_country)

    elif side == "Customer Segmentation":
        customer_segmentation.render(st, df=df, code_by_country=code_by_country)

    elif side == "Market Basket Analysis":
        market_basket_analysis.render(st, df=df, code_by_country=code_by_country)
