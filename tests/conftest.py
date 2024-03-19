from bs4 import BeautifulSoup
import pytest
import requests
import subprocess
import time
from urllib.parse import urljoin

from src.database.models.base import Base
from src.database import repository
from src.settings import Settings

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


@pytest.fixture(scope="module")
def server():
    # Start the Streamlit server
    process = subprocess.Popen(["streamlit", "run", "app.py", "--server.headless", "true"])

    # Give the server some time to start
    attempts = 10
    started = False
    while attempts > 0:
        try:
            requests.get(_page_url())
            started = True
            break
        except requests.exceptions.ConnectionError:
            time.sleep(0.1)
        attempts -= 1

    if not started:
        raise Exception("Server never started")

    # Run test
    yield

    # Stop the Streamlit server
    process.terminate()


def get_page(path: str = ""):
    response = requests.get(_page_url(path))

    page = None
    if response.status_code == 200:
        page = BeautifulSoup(response.text, "html.parser")

    return (page, response)


def _page_url(path: str = ""):
    return urljoin(f"http://localhost:{Settings.port}", path)
