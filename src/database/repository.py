import pandas as pd
from sqlalchemy import create_engine
from src.settings import Settings

_engine = create_engine(Settings.database_url)


# it loads nonexisting rows to the table
def reload_99_users_dataset(csv_file_path):
    df = pd.read_csv(csv_file_path)
    df.to_sql("99_users_dataset", _engine, if_exists="replace", index=False)
