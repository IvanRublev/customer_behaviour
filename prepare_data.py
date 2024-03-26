from src.customer_behaviour import prepare_dataframe, PAGES
from src.logger import logger


if __name__ == "__main__":
    # This is entrypoint for application to prepare data as a script run during the deployment.
    df, _ = prepare_dataframe()

    for page in PAGES:
        logger.info(f"Preparing data for {page.__name__}...")
        page.maybe_prepare_data_on_disk(df)
        logger.info("Done.")
