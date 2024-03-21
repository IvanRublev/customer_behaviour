import pandas as pd
import streamlit as st

from src.analysis.segmentation import k_means_centroids, rfm_scores, summarize_segments


def maybe_initialize_session_state(st):
    pass


def render(st, df):
    st.title("Customer Segmentation", anchor="customer-segmentation")

    segment_count = st.sidebar.selectbox("Select the number of segment you want to create:", [2, 3, 4, 5])

    rfm_scores = _rfm_scores(df)
    rfm_scores["Customer ID"] = pd.Categorical(rfm_scores["Customer ID"])

    labeled_rfm, features_importance = _rfm_segments(rfm_scores, segment_count)
    rfm_summary = _rfm_segment_summary(labeled_rfm)

    st.header("🗂 Axis")
    st.markdown("""
        * __Recency__: The number of days since the last customer's purchase
        * __Frequency__: The number of unique invoices of customer
        * __Monetary__: The total amount spent by customer
        """)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("RFM Segmentation Table")
        st.download_button("⬇️ Download", labeled_rfm.to_csv(index=False), "rfm_segmentation_result.csv")
        st.dataframe(labeled_rfm, height=250)

    with col2:
        st.subheader("Summary")
        st.write("Here is the summary metrics of your segmentation result")
        st.dataframe(rfm_summary, hide_index=True)

    st.header("📊 Recency, Frequency, and Monetary (RFM) analysis")

    st.write("We use K-Means method to segment customers by normalized RFM values.")


@st.cache_data
def _rfm_scores(df):
    return rfm_scores(df)


@st.cache_data
def _rfm_segments(rfm, segments):
    labeled_rfm, features_importance = k_means_centroids(rfm, n_clusters=segments)
    return labeled_rfm, features_importance


@st.cache_data
def _rfm_segment_summary(labeled_rfm):
    return summarize_segments(labeled_rfm)
