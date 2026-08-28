"""Fixtures shared across tests."""

import pytest
from selenium import webdriver

from api.betting_client import BettingApiClient
from pages.home_page import HomePage


@pytest.fixture
def driver():
    drv = webdriver.Chrome()  # o el driver/opciones que uses en el proyecto
    drv.maximize_window()
    yield drv
    drv.quit()


@pytest.fixture
def home_page(driver) -> HomePage:
    return HomePage(driver).open()


@pytest.fixture
def api() -> BettingApiClient:
    """API client for the configured user."""
    return BettingApiClient()


@pytest.fixture
def clean_balance(api: BettingApiClient) -> float:
    api.reset_balance()
    return api.get_current_balance()
