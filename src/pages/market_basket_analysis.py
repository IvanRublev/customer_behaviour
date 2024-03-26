import pandas as pd
import plotly.express as px
import streamlit as st

from src.analysis.segmentation import k_means_centroids, rfm_scores, summarize_segments
from src.pages.components.sidebar import append_filters_title, country_filter, date_range_filter, enable_sidebar_filters


def maybe_initialize_session_state(st):
    pass


def render(st, df, code_by_country):
    enable_sidebar_filters()
    df, dates, country = _apply_sidebar_filters(df, code_by_country)

    st.title(append_filters_title("Market Basket Analysis", dates, country), anchor="market-basket-analysis")

    st.markdown("We use Apriori algorithm to find associations rules between products.")

    st.header("🗂 Axis")

    st.markdown("""
        * __Association rule__: A rule that implies that if a customer buys a product,
                                then he will also buy another product
        * __Support__: Frequency of the items X and Y bought together appearance 
                       in the data set, as number of transactions with the items 
                       to toal transactions
        * __Confidence__: Percentage of all transactions satisfying X that also satisfy Y, 
                          as number of transactions with X and Y to total transactions with X
        * __Lift__: Observed support divided by expected support if X and Y were independent. 
                    If >1 then X and Y are more likely to be dependent on each other
        * __Conviciton__: The ratio of the expected frequency that the rule makes incorrect
                          prediction if X and Y were independent to the observed frequency 
                          of incorrect predictions. Conviction of 1.2 means that the rule 
                          is incorrect 20% times more often if the association 
                          between X and Y were purely random
        """)


def _apply_sidebar_filters(df, code_by_country):
    # st.sidebar.subheader("🍰 Segments count")

    # segment_count = st.sidebar.selectbox("Select the number of segments you want to create:", [2, 3, 4, 5])

    df, _filter_key, dates = date_range_filter(df)
    df, _filter_key, country = country_filter(df, code_by_country)

    return df, dates, country
