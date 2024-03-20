import streamlit as st

from src.dataframe.statistics import rfm_scores
from src.settings import Settings


def maybe_initialize_session_state(st):
    pass


def render(st, df):
    st.title("Customer Segmentation", anchor="customer-segmentation")

    st.header("Summary Metrics")

    st.header("📊 Recency, Frequency, and Monetary (RFM) analysis")

    rfm = _rfm_scores(df)

    

@st.cache_data
def _rfm_scores(df):
    return rfm_scores(df)
