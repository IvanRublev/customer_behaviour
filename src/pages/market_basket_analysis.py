import ast
import os
import re

from apyori import apriori
import pandas as pd
import plotly.express as px
import streamlit as st

from src.dataframe.preprocess import reject_outliers_by_iqr
from src.logger import logger
from src.pages.components.sidebar import (
    append_filters_title,
    country_filter_key,
    do_filter_by_country_code,
    enable_sidebar_filters,
    rejected_uk_country,
)
from src.settings import Settings

_rules_count_by_country_filename = os.path.join(Settings.prepared_data_path, f"{__name__}_rules_count_by_country.csv")


def maybe_prepare_data_on_disk(df, code_by_country):
    logger.info("Preparing for no filter.")
    _write_csv_files(df, *_file_names(""))

    logger.info("Preparing for uk rejected.")
    _uk_name, uk_code = rejected_uk_country(code_by_country)
    df_uk_rejected = do_filter_by_country_code(df, None, uk_code)
    file_postfix = country_filter_key("", None, uk_code)
    _write_csv_files(df_uk_rejected, *_file_names(file_postfix))

    # For each country
    rules_by_country = {}
    for country_name, country_code in code_by_country.items():
        logger.info(f"Preparing for {country_name}.")
        df_country = do_filter_by_country_code(df, country_code, None)
        file_postfix = country_filter_key("", country_code, None)
        rules_count = _write_csv_files(df_country, *_file_names(file_postfix))
        rules_by_country[country_name] = rules_count

    if not os.path.isfile(_rules_count_by_country_filename) or (
        os.path.getmtime(_rules_count_by_country_filename) <= os.path.getmtime(Settings.dataset_csv_path)
    ):
        rbc = pd.DataFrame.from_dict(rules_by_country, orient="index", columns=["Rules Count"])
        rbc.reset_index(inplace=True)
        rbc.rename(columns={"index": "Country"}, inplace=True)
        rbc.to_csv(_rules_count_by_country_filename, index=False)


def _file_names(postfix=""):
    return (
        os.path.join(Settings.prepared_data_path, f"{__name__}_{postfix}_association_rules.csv"),
        os.path.join(Settings.prepared_data_path, f"{__name__}_{postfix}_transactions_stats.csv"),
        os.path.join(Settings.prepared_data_path, f"{__name__}_{postfix}_basket_sizes.csv"),
    )


def _write_csv_files(df, association_rules_file, transactions_stats_file, basket_sizes_file):
    if not os.path.isfile(association_rules_file) or (
        os.path.getmtime(association_rules_file) <= os.path.getmtime(Settings.dataset_csv_path)
    ):
        description_by_stock_code = df.groupby("StockCode", observed=True)["Description"].first()

        stock_code_by_invoice_id = (
            df.groupby("Invoice ID", observed=True)["StockCode"].apply(list).apply(sorted).reset_index()
        )
        stock_code_by_invoice_id["Basket Size"] = stock_code_by_invoice_id["StockCode"].apply(len)

        # Reject outliers
        stock_code_by_invoice_id = reject_outliers_by_iqr(stock_code_by_invoice_id, "Basket Size")

        stock_code_len_counts = stock_code_by_invoice_id["Basket Size"].value_counts().sort_index(ascending=True)
        stock_code_len_counts.name = "Transactions"
        stock_code_len_counts.to_csv(basket_sizes_file, index=True)

        transactions = list(stock_code_by_invoice_id["StockCode"])
        transactions_count = len(transactions)
        transaction_stats = pd.DataFrame([transactions_count], columns=["Transactions Count"])
        transaction_stats.to_csv(transactions_stats_file, index=False)

        # Apriori works not well on low amount of transactions
        if transactions_count <= 10:
            ar = _associations_dataframe([])
            ar.to_csv(association_rules_file, index=False)
            return 0

        logger.info(f"Analyzing {transactions_count} transactions.")
        # To prevent apriori running for too long and giving rubbish we use different minimum support for search
        min_support = 0.01
        if transactions_count < 10000:
            min_support = 0.03
        if transactions_count < 1000:
            min_support = 0.1
        if transactions_count < 100:
            min_support = 0.2

        relations_generator = apriori(
            transactions, min_support=min_support, min_confidence=0.6, min_lift=3, min_length=2
        )
        relations = list(relations_generator)
        logger.info(f"Found association rules {len(relations)} total.")

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
            if len(ordered_statistics_one_item_base) == 0:
                continue

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

        ar = _associations_dataframe(results)
        ar.sort_values("Consequent", ascending=True, inplace=True)
        ar.to_csv(association_rules_file, index=False)

        return len(ar)


def _associations_dataframe(results):
    return pd.DataFrame(
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


def maybe_initialize_session_state(st):
    pass


def render(st, df, code_by_country):
    enable_sidebar_filters()

    country, country_code, rejected_country, rejected_country_code = _initialize_sidebar_country_filter(
        df, code_by_country
    )
    # read filtered data for specific country if any
    ar, antecendent_items, consequent_counts, ts, scl = _read_csv_files(
        *_file_names(country_filter_key("", country_code, rejected_country_code))
    )
    antcendent_item, consequents_number = _initialize_rules_sidebar_filters(antecendent_items, consequent_counts)
    ar = _apply_sidebar_filters(ar, antcendent_item, consequents_number)

    st.title(
        append_filters_title("Market Basket Analysis", None, country, rejected_country),
        anchor="market-basket-analysis",
    )

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
            y="Transactions",
            nbins=30,
            title="Basket Size Distribution",
            range_x=[1, max(scl["Basket Size"]) + 1],
        )
        fig.update_yaxes(title_text="Transactions")
        st.plotly_chart(fig, use_container_width=True)

    st.header("📊 Association Rules")

    st.write(
        "Filtered ",
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


def _initialize_sidebar_country_filter(df, code_by_country):
    st.sidebar.subheader("🏠 Country Filter")

    rbc = pd.read_csv(_rules_count_by_country_filename).to_dict("list")
    rules_count_by_country = dict(zip(rbc["Country"], rbc["Rules Count"]))

    uk_name, uk_code = rejected_uk_country(code_by_country)
    reject_uk = st.sidebar.toggle("Reject UK", True, disabled=st.session_state.filters_disabled)

    def rules_count_postfix(name):
        if rules_count_by_country[name] > 0:
            return f" [Rules: {rules_count_by_country[name]}]"

        return ""

    code_by_country = {
        f"{name} ({code})" + rules_count_postfix(name): code
        for name, code in code_by_country.items()
        if not reject_uk or (reject_uk and name != uk_name)
    }
    code_by_country = {**code_by_country, "None": None}
    countries_list = list(code_by_country.keys())
    countries_list.remove("None")
    countries_list.insert(0, "None")
    country = st.sidebar.selectbox(
        "Select the specific country you wish to analyse or select None for all countries:",
        countries_list,
        disabled=st.session_state.filters_disabled,
    )
    logger.info(f"Country: {country}")

    country_code = code_by_country[country]
    reject_code = uk_code if reject_uk and not country_code else None
    df = do_filter_by_country_code(df, country_code, reject_code)

    logger.info(f"Country code: {country_code}")

    # Prepare titles
    if country == "None":
        country = None

    rejected_country = uk_name if reject_code else None

    return country, country_code, rejected_country, reject_code


def _initialize_rules_sidebar_filters(antecendent_items, consequent_counts):
    st.sidebar.subheader("🧃 Antecendent item")
    antecendent_items.insert(0, "None")
    antcendent_item = st.sidebar.selectbox(
        "Select the item bought first, to see what were bought together or select None for all variants:",
        antecendent_items,
    )

    # We don't need this filter for now because all found rules has only 1 consequent item.
    # consequents_number = 1
    st.sidebar.subheader("➡️ Consequent items")
    consequents_number = st.sidebar.selectbox(
        "Select the number of items bought togheter with an antecendent item:", consequent_counts
    )

    return antcendent_item, consequents_number


@st.cache_data
def _apply_sidebar_filters(ar, antecendent_item, consequents_number):
    if antecendent_item != "None":
        ar = ar[ar["Antecedent"] == antecendent_item]

    ar = ar[ar["Consequent"].apply(len) == consequents_number]

    return ar.sort_values(by="Confidence", ascending=False).reset_index(drop=True)


def _read_csv_files(association_rules_file, transactions_stats_file, basket_sizes_file):
    ar = pd.read_csv(association_rules_file)
    ar["Consequent"] = ar["Consequent"].apply(ast.literal_eval)  # to parse string into list of strings
    antecendent_items = list(ar["Antecedent"].unique())
    antecendent_items.sort()
    consequent_counts = list(ar["Consequent"].apply(len).unique())
    consequent_counts.sort()

    ts = pd.read_csv(transactions_stats_file)

    scl = pd.read_csv(basket_sizes_file)

    return ar, antecendent_items, consequent_counts, ts, scl


@st.cache_data
def _top_10_by_confidence(ar):
    ar.sort_values(by="Confidence", ascending=False)
    return ar.head(10)
