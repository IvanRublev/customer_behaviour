import pandas as pd
import plotly.express as px
import streamlit as st

from src.analysis.segmentation import k_means_centroids, rfm_scores, summarize_segments
from src.pages.components.sidebar import append_filters_title, country_filter, date_range_filter, enable_sidebar_filters


def maybe_prepare_data_on_disk(df):
    pass


def maybe_initialize_session_state(st):
    pass


def render(st, df, code_by_country):
    enable_sidebar_filters()
    df, segment_count, dates, country = _apply_sidebar_filters(df, code_by_country)

    st.title(append_filters_title("Customer Segmentation", dates, country), anchor="customer-segmentation")

    st.write("We use K-Means method to segment customers by normalized Recency Frequency and Monetary (RFM) values.")

    rfm_scores, rfm_segments, rfm_segments_summary, features_importance = _rfm_tables(df, segment_count)
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
        st.dataframe(rfm_segments_summary, hide_index=True)

    with col2:
        st.subheader("RFM Segmentation Table")
        st.download_button("⬇️ Download", rfm_segments.to_csv(index=False), "rfm_segmentation_result.csv")
        st.dataframe(rfm_segments, height=250)

    st.header("📊 Recency, Frequency, and Monetary Segmentation Exploration")

    tab0, tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Customers Distribution",
            "3D Plot of RFM",
            "1️⃣ Recency vs Frequency",
            "2️⃣ Recency vs Monetary",
            "3️⃣ Frequency vs Monetary",
        ]
    )

    with tab0:
        fig = px.bar(
            rfm_segments_summary, y="Segment ID", x="Customer Count", orientation="h", title="Customers Distribution"
        )
        fig.update_yaxes(dtick=1)
        st.plotly_chart(fig, use_container_width=True)

    px_category_order = {"Segment ID": [str(i) for i in range(1, segment_count + 1)]}
    colorbar_ticks = {
        "tickvals": list(range(1, segment_count + 1)),
        "ticktext": [str(i) for i in range(1, segment_count + 1)],
    }

    with tab1:
        fig = px.scatter_3d(
            rfm_segments,
            x="Recency",
            y="Frequency",
            z="Monetary",
            color="Segment ID",
            title="3D Plot of RFM",
            category_orders=px_category_order,
        )
        fig.update_coloraxes(colorbar=colorbar_ticks)
        fig.update_layout(scene={"xaxis_title": "Recency (Days)", "yaxis_title": "Frequency (Invoices)"})
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        fig = px.scatter(
            rfm_segments,
            x="Recency",
            y="Frequency",
            color="Segment ID",
            title="Recency vs Frequency",
            category_orders=px_category_order,
        )
        fig.update_coloraxes(colorbar=colorbar_ticks)
        fig.update_layout(xaxis_title="Recency (Days)", yaxis_title="Frequency (Invoices)")
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        fig = px.scatter(
            rfm_segments,
            x="Recency",
            y="Monetary",
            color="Segment ID",
            title="Recency vs Monetary",
            category_orders=px_category_order,
        )
        fig.update_coloraxes(colorbar=colorbar_ticks)
        fig.update_layout(xaxis_title="Recency (Days)")
        st.plotly_chart(fig, use_container_width=True)

    with tab4:
        fig = px.scatter(
            rfm_segments,
            x="Frequency",
            y="Monetary",
            color="Segment ID",
            title="Frequency vs Monetary",
            category_orders=px_category_order,
        )
        fig.update_coloraxes(colorbar=colorbar_ticks)
        fig.update_layout(xaxis_title="Frequency (Invoices)")
        st.plotly_chart(fig, use_container_width=True)


@st.cache_data
def _rfm_tables(df, segments):
    scores = rfm_scores(df)
    segments, features_importance = k_means_centroids(scores, n_clusters=segments)
    segments_summary = summarize_segments(segments)
    return scores, segments, segments_summary, features_importance


def _apply_sidebar_filters(df, code_by_country):
    st.sidebar.subheader("🍰 Segments count")

    segment_count = st.sidebar.selectbox("Select the number of segments you want to create:", [2, 3, 4, 5])

    df, _filter_key, dates = date_range_filter(df)
    df, _filter_key, country = country_filter(df, code_by_country)

    return df, segment_count, dates, country
