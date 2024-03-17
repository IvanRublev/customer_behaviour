import pytest
from faker import Faker
from src.database.models.base import Base
from src.database import repository

fake = Faker()

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
