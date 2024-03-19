import os
import toml

with open("pyproject.toml", "r") as file:
    _pyproject_content = toml.load(file)


class Settings:
    """Represents the settings for the application.

    Some of them are loaded from environment variables, some hardcoded, and others loaded from the pyproject.toml .
    """

    # Loaded from environment variables

    database_url: str = os.environ["DATABASE_URL"]
    port: int = int(os.environ["STREAMLIT_SERVER_PORT"])

    # Hardcoded

    dataset_csv_path: str = "dataset/online_retail_II.csv"

    # From pyproject.toml

    app_name = _pyproject_content["tool"]["poetry"]["name"]
    app_description = _pyproject_content["tool"]["poetry"]["description"]
    app_version = _pyproject_content["tool"]["poetry"]["version"]
