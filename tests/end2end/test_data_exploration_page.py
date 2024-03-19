import requests

from tests.conftest import get_page
from src.settings import Settings


def test_pass_given_exploration_page(server):
    (page, _) = get_page()

    assert page.title.string == "Data Exploration"
