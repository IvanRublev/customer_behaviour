from src.settings import Settings


def maybe_initialize_session_state(st):
    pass


def render(st):
    st.title(Settings.app_description, anchor="home")

    dataset_link = "[Online Retail II dataset](https://archive.ics.uci.edu/dataset/502/online+retail+ii)"
    st.markdown(f"""
                In this project, we will analyze customer behavior using :
                * Exploratory Data Analysis
                * Customer Segmentation using RFM Analysis
                """)

    st.header("Dataset")

    st.markdown(f"""
                As an example, we use the {dataset_link} of ~500K records.
                > Chen,Daqing. (2019). Online Retail II. UCI Machine Learning Repository. https://doi.org/10.24432/C5CG6D.
                """)
