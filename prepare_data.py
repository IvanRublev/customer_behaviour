from src.customer_behaviour import prepare_dataframe, PAGES
from src.logger import logger


if __name__ == "__main__":
    # This is entrypoint for application to prepare data during the deployment.
    df, code_by_country = prepare_dataframe()

    for page in PAGES:
        logger.info(f"Preparing data for {page.__name__}...")
        page.maybe_prepare_data_on_disk(df, code_by_country)
        logger.info("Done.")
