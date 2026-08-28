"""Fixtures shared across tests."""

import allure
import pytest
from selenium import webdriver

from api.betting_client import BettingApiClient
from pages.home_page import HomePage


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.fixture
def driver(request):
    drv = webdriver.Chrome()  # o el driver/opciones que uses en el proyecto
    drv.maximize_window()
    yield drv
    if getattr(request.node, "rep_call", None) is not None and request.node.rep_call.failed:
        allure.attach(
            drv.get_screenshot_as_png(),
            name="failure-screenshot",
            attachment_type=allure.attachment_type.PNG,
        )
        allure.attach(
            drv.page_source,
            name="page-source",
            attachment_type=allure.attachment_type.HTML,
        )
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
