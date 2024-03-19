import os


class Settings:
    database_url: str = os.environ["DATABASE_URL"]
    port: int = int(os.environ["STREAMLIT_SERVER_PORT"])
