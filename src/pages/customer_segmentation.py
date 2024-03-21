import streamlit as st

from src.dataframe.statistics import rfm_scores
from src.dataframe.label import k_means_centroids
from src.settings import Settings


def maybe_initialize_session_state(st):
    pass


def render(st, df):
    st.title("Customer Segmentation", anchor="customer-segmentation")

    segment_count = st.selectbox("Select the number of segment you want to create:", [2, 3, 4, 5])

    rfm_scores = _rfm_scores(df)
    labeled_rfm, features_importance = _rfm_segments(rfm_scores, segment_count)
    rfm_summary = _rfm_segment_summary(labeled_rfm)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🗂 RFM Segmentation Table")
        st.dataframe(rfm_scores)
        st.caption("Download Your Segmentation Result")
        st.download_button("⬇️ Download", rfm_scores.to_csv(index=False), "rfm_segmentation_result.csv")

    with col2:
        st.subheader("📊 Summary Metrics")
        st.write("Here is the summary metrics of your segmentation result")
        st.dataframe(rfm_summary)

    st.header("📊 Recency, Frequency, and Monetary (RFM) analysis")

    st.markdown("""
                Definitions:
                * Recency: The number of days since the last customer's purchase.
                * Frequency: The number of unique invoices of customer.
                * Monetary: The total amount spent by customer.

                We use K-Means method to segment customers by normalized RFM values.
                """)


@st.cache_data
def _rfm_scores(df):
    return rfm_scores(df)


@st.cache_data
def _rfm_segments(rfm, segments):
    labeled_rfm, features_importance = k_means_centroids(rfm, n_clusters=segments)
    return labeled_rfm, features_importance


@st.cache_data
def _rfm_segment_summary(labeled_rfm):
    return (
        labeled_rfm.groupby("segment")
        .agg({"recency": "mean", "frequency": "mean", "monetary": "mean", "Customer ID": "count"})
        .reset_index()
        .rename(
            columns={
                "recency": "Recency",
                "frequency": "Frequency",
                "monetary": "Monetary",
                "CustomerID": "Customer Count",
            }
        )
    )
