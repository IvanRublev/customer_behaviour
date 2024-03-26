import ast
import os
import re

from apyori import apriori
import pandas as pd
import plotly.express as px
import streamlit as st

from src.dataframe.preprocess import reject_outliers_by_iqr
from src.pages.components.sidebar import append_filters_title, enable_sidebar_filters
from src.settings import Settings

_association_rules_file = os.path.join(Settings.prepared_data_path, f"{__name__}_association_rules.csv")
_transactions_stats_file = os.path.join(Settings.prepared_data_path, f"{__name__}_transactions_stats.csv")
_stock_code_lens_file = os.path.join(Settings.prepared_data_path, f"{__name__}_basket_sizes.csv")


def maybe_prepare_data_on_disk(df):
    if not os.path.isfile(_association_rules_file) or (
        os.path.getmtime(_association_rules_file) <= os.path.getmtime(Settings.dataset_csv_path)
    ):
        description_by_stock_code = df.groupby("StockCode", observed=True)["Description"].first()

        stock_code_by_invoice_id = (
            df.groupby("Invoice ID", observed=True)["StockCode"].apply(list).apply(sorted).reset_index()
        )
        stock_code_by_invoice_id["Basket Size"] = stock_code_by_invoice_id["StockCode"].apply(len)

        # Reject outliers
        stock_code_by_invoice_id = reject_outliers_by_iqr(stock_code_by_invoice_id, "Basket Size")

        stock_code_len_counts = stock_code_by_invoice_id["Basket Size"].value_counts().sort_index(ascending=True)
        stock_code_len_counts.to_csv(_stock_code_lens_file, index=True)

        transactions = stock_code_by_invoice_id["StockCode"]
        transactions_count = len(transactions)

        transaction_stats = pd.DataFrame([transactions_count], columns=["Transactions Count"])
        transaction_stats.to_csv(_transactions_stats_file, index=False)

        # The following takes about 5 min to calculate
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

                antecedent = _clean_str(description_by_stock_code[list(confident_stat.items_base)[0]])
                consequent = [_clean_str(description_by_stock_code[item]) for item in confident_stat.items_add]

                support = relation.support
                confidence = confident_stat.confidence
                lift = confident_stat.lift
                transactions_seen = int(support * transactions_count)

                stock_codes = list(confident_stat.items_base) + list(confident_stat.items_add)

                # find statistics for baskets including all rule's stock codes
                basket_sizes = [
                    len(transaction)
                    for transaction in transactions
                    if all(stock_code in transaction for stock_code in stock_codes)
                ]
                basket_sizes.sort(reverse=False)
                basket_size_min = min(basket_sizes)
                basket_size_avg = int(round(sum(basket_sizes) / len(basket_sizes)))
                basket_size_median = basket_sizes[len(basket_sizes) // 2]
                basket_size_max = max(basket_sizes)

                rows = (
                    antecedent,
                    consequent,
                    support,
                    confidence,
                    lift,
                    transactions_seen,
                    basket_size_min,
                    basket_size_avg,
                    basket_size_median,
                    basket_size_max,
                )
                results.append(rows)

        ar = pd.DataFrame(
            results,
            columns=[
                "Antecedent",
                "Consequent",
                "Support",
                "Confidence",
                "Lift",
                "Transactions seen",
                "Basket Size Min",
                "Basket Size Avg",
                "Basket Size Median",
                "Basket Size Max",
            ],
        )
        ar.sort_values("Consequent", ascending=True, inplace=True)

        ar.to_csv(_association_rules_file, index=False)


def maybe_initialize_session_state(st):
    pass


def render(st, df, code_by_country):
    enable_sidebar_filters()
    ar, antecendent_items, consequent_counts, ts, scl = _read_files()
    ar, dates, country = _apply_sidebar_filters(ar, antecendent_items, consequent_counts, code_by_country)

    st.title(append_filters_title("Market Basket Analysis", dates, country), anchor="market-basket-analysis")

    st.markdown("We use Apriori algorithm to find associations rules between products.")

    col1, col2 = st.columns(2)

    with col1:
        st.header("🗂 Legend")

        st.markdown("""
            #### Entities
            * __Association rule__: A rule that implies that if a customer buys a product,
                                    then he will also buy another product
            * __Antecedent__: The item X that is bought first
            * __Consequent__: The item Y that is bought next
            * __Transaction__: A single purchase defined by the invoice
            * __Basket Size__: The number of items bought in a transaction
                    
            #### Metrics
            * __Support__: Frequency of the items X and Y bought together, 
                        as number of transactions with the items to total transactions
            * __Confidence__: Percentage of all transactions satisfying X that also satisfy Y, 
                            as number of transactions with X and Y to total transactions with X
            * __Lift__: Observed support divided by expected support if X and Y were independent. 
                        If >1 then X and Y are more likely to be dependent on each other
            """)

    with col2:
        fig = px.histogram(
            scl,
            x="Basket Size",
            y="count",
            nbins=30,
            title="Basket Size Distribution",
            range_x=[1, max(scl["Basket Size"]) + 1],
        )
        st.plotly_chart(fig, use_container_width=True)

    st.header("📊 Association Rules")

    st.write(
        "A total of ",
        len(ar),
        " association rules found in ",
        ts["Transactions Count"].values[0],
        " transactions.",
    )

    tab0, tab1 = st.tabs(
        [
            "Top 10 by Confidence",
            "All association rules",
        ]
    )

    frame_height = 450

    with tab0:
        st.dataframe(_top_10_by_confidence(ar), height=frame_height)

    with tab1:
        st.dataframe(ar, height=frame_height)


def _apply_sidebar_filters(ar, antecendent_items, consequent_counts, code_by_country):
    st.sidebar.subheader("🧃 Antecendent item")
    antecendent_items.insert(0, "None")
    antcendent_item = st.sidebar.selectbox(
        "Select the item bought first, to see what were bought together or select None for all variants:",
        antecendent_items,
    )

    st.sidebar.subheader("➡️ Consequent items")
    consequents_number = st.sidebar.selectbox(
        "Select the number of items bought togheter with an antecendent item:", consequent_counts
    )

    ar = _filter_association_rules(ar, antcendent_item, consequents_number)

    # df, _filter_key, dates = date_range_filter(df)
    # df, _filter_key, country = country_filter(df, code_by_country)

    return ar, None, None


def _read_files():
    ar = pd.read_csv(_association_rules_file)
    ar["Consequent"] = ar["Consequent"].apply(ast.literal_eval)  # to parse string into list of strings
    antecendent_items = list(ar["Antecedent"].unique())
    antecendent_items.sort()
    consequent_counts = list(ar["Consequent"].apply(len).unique())
    consequent_counts.sort()

    ts = pd.read_csv(_transactions_stats_file)

    scl = pd.read_csv(_stock_code_lens_file)

    return ar, antecendent_items, consequent_counts, ts, scl


@st.cache_data
def _filter_association_rules(ar, antecendent_item, consequents_number):
    if antecendent_item != "None":
        ar = ar[ar["Antecedent"] == antecendent_item]

    ar = ar[ar["Consequent"].apply(len) == consequents_number]

    return ar.sort_values(by="Confidence", ascending=False).reset_index(drop=True)


@st.cache_data
def _top_10_by_confidence(ar):
    ar.sort_values(by="Confidence", ascending=False)
    return ar.head(10)
