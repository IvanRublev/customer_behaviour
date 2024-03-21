import pandas as pd
import streamlit as st

from src.analysis.segmentation import k_means_centroids, rfm_scores, summarize_segments


def maybe_initialize_session_state(st):
    pass


def render(st, df):
    st.title("Customer Segmentation", anchor="customer-segmentation")

    st.write("We use K-Means method to segment customers by normalized Recency Frequency and Monetary (RFM) values.")

    segment_count = st.sidebar.selectbox("Select the number of segment you want to create:", [2, 3, 4, 5])

    rfm_scores, labeled_rfm, rfm_summary, features_importance = _rfm_tables(df, segment_count)
    rfm_scores["Customer ID"] = pd.Categorical(rfm_scores["Customer ID"])

    st.header("🗂 Axis")
    st.markdown("""
        * __Recency__: The number of days since the customer's last purchase
        * __Frequency__: Number of customer invoices
        * __Monetary__: The total amount spent by customer
        """)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Summary")
        st.write("Here is the summary metrics of the segmentation result.")
        st.dataframe(rfm_summary, hide_index=True)

    with col2:
        st.subheader("RFM Segmentation Table")
        st.download_button("⬇️ Download", labeled_rfm.to_csv(index=False), "rfm_segmentation_result.csv")
        st.dataframe(labeled_rfm, height=250)

    st.header("📊 Recency, Frequency, and Monetary (RFM) Segmentation Exploration")


@st.cache_data
def _rfm_tables(df, segments):
    scores = rfm_scores(df)
    labeled_rfm, features_importance = k_means_centroids(scores, n_clusters=segments)
    summary = summarize_segments(labeled_rfm)
    return scores, labeled_rfm, summary, features_importance
