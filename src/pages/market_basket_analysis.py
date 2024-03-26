import os
import re

from apyori import apriori
import pandas as pd
# import plotly.express as px
# import streamlit as st

from src.pages.components.sidebar import append_filters_title, country_filter, date_range_filter, enable_sidebar_filters
from src.settings import Settings

_association_rules_file = os.path.join(Settings.prepared_data_path, f"{__name__}_association_rules.csv")


def maybe_prepare_data_on_disk(df):
    if not os.path.isfile(_association_rules_file) or (
        os.path.getmtime(_association_rules_file) <= os.path.getmtime(Settings.dataset_csv_path)
    ):
        stock_code_by_invoice_id = df.groupby("Invoice ID", observed=False)["StockCode"].apply(list).reset_index()
        transactions = stock_code_by_invoice_id["StockCode"]

        description_by_stock_code = df.groupby("StockCode", observed=False)["Description"].first()

        # it takes about 5 min to calculate
        relations_generator = apriori(transactions, min_support=0.0045, min_confidence=0.2, min_lift=3, min_length=2)
        relations = list(relations_generator)

        def _clean_str(string):
            string = string.strip()
            string = re.sub(" +", " ", string)
            return string

        results = []
        for relation in relations:
            # we take only rules with one item in the base
            ordered_statistics_one_item_base = [
                stat for stat in relation.ordered_statistics if len(stat.items_base) == 1
            ]
            if len(ordered_statistics_one_item_base) > 0:
                # we interested in rule with maximal confidence
                confident_stat = max(ordered_statistics_one_item_base, key=lambda x: x.confidence)

                consequent = _clean_str(description_by_stock_code[list(confident_stat.items_base)[0]])
                antecedent = [_clean_str(description_by_stock_code[item]) for item in confident_stat.items_add]
                confidence = confident_stat.confidence
                lift = confident_stat.lift

                support = relation.support
                rows = (consequent, antecedent, support, confidence, lift)
                results.append(rows)

        ar = pd.DataFrame(results, columns=["Consequent", "Anticedent", "Support", "Confidence", "Lift"])
        ar.sort_values("Consequent", ascending=True, inplace=True)

        ar.to_csv(_association_rules_file, index=False)


def maybe_initialize_session_state(st):
    pass


def render(st, df, code_by_country):
    enable_sidebar_filters()
    df, dates, country = _apply_sidebar_filters(df, code_by_country)

    _ar = _association_rules(df)

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


def _association_rules(df):
    ar = pd.read_csv(_association_rules_file)
    return ar


def _apply_sidebar_filters(df, code_by_country):
    # st.sidebar.subheader("🍰 Segments count")

    # segment_count = st.sidebar.selectbox("Select the number of segments you want to create:", [2, 3, 4, 5])

    df, _filter_key, dates = date_range_filter(df)
    df, _filter_key, country = country_filter(df, code_by_country)

    return df, dates, country
