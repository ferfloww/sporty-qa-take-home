"""Fixtures shared across tests.

driver is function-scoped on purpose - placing a bet changes the account
balance, so each test should start clean instead of inheriting state from
whatever ran before it.
"""

import pytest

from api.betting_client import BettingApiClient


@pytest.fixture
def api() -> BettingApiClient:
    """API client for the configured user."""
    return BettingApiClient()


@pytest.fixture
def clean_balance(api: BettingApiClient) -> float:
    api.reset_balance()
    return api.get_current_balance()
