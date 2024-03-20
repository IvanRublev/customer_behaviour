import streamlit as st

from src.settings import Settings


def maybe_initialize_session_state(st):
    pass


def render(st, df):
    st.title("Customer Segmentation", anchor="customer-segmentation")

    st.header("Summary Metrics")

    st.header("📊 Recency, Frequency, and Monetary (RFM) analysis")

    st.write("This page is under construction")
