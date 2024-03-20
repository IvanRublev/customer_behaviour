import pytest
import pandas as pd

from src.database.models.base import Base
from src.database import repository


# fixtures for database


@pytest.fixture(scope="function", autouse=True)
def db_session():
    session = repository.SessionLocal()

    yield session

    session.rollback()  # for case if we have an uncommitted transaction due to an exception

    # Drop all records in all tables after each test
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())

    session.commit()
    session.close()


def build_dataframe(rows_count: int = 100):
    """Returns a dataframe with N rows"""
    df = pd.read_csv("dataset/online_retail_II_100.csv")

    while len(df) < rows_count:
        df = pd.concat([df, df])

    # If the dataframe is larger than the desired size, trim it down
    df = df.iloc[:rows_count]

    return df
