import allure
import pytest

from api.betting_client import BettingApiClient
from config import BusinessRules

NEGATIVE_STAKES = [-0.01, -10, -1000000]


@pytest.fixture
def match_id(api: BettingApiClient) -> str:
    return api.get_first_match_id()


@allure.title("Negative stake ({stake}) is rejected, not credited")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.api
@pytest.mark.critical
@pytest.mark.parametrize("stake", NEGATIVE_STAKES)
def test_negative_stake_is_rejected(
    api: BettingApiClient,
    match_id: str,
    clean_balance: float,
    stake: float,
):
    """The one flow that actually moves money - if this breaks, nothing else matters."""

    response = api.place_bet(match_id=match_id, selection="HOME", stake=stake)

    assert response.status_code == 422, (
        f"Stake {stake} returned {response.status_code}, expected 422. "
        f"Response: {response.text}"
    )
    assert (
        response.json().get("error") == "invalid_stake_min"
    ), f"Expected 'invalid_stake_min' for stake {stake}, got: {response.json()}"

    balance_after = api.get_current_balance()
    assert balance_after == pytest.approx(clean_balance, abs=0.01), (
        f"Balance moved from {clean_balance} to {balance_after} on a rejected "
        f"bet with stake {stake}"
    )


@allure.title("Out-of-range stake ({stake}) is rejected as {expected_error}")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.api
@pytest.mark.parametrize(
    "stake, expected_error",
    [
        (0.99, "invalid_stake_min"),
        (100.01, "invalid_stake_max"),
    ],
)
def test_out_of_range_stake_is_rejected(
    api: BettingApiClient,
    match_id: str,
    clean_balance: float,
    stake: float,
    expected_error: str,
):
    """Worst case in the whole app: a negative stake flips the balance
    operation instead of just being an invalid bet."""

    response = api.place_bet(match_id=match_id, selection="HOME", stake=stake)

    assert response.status_code == 422, (
        f"Stake {stake} returned {response.status_code}, expected 422. "
        f"Response: {response.text}"
    )
    assert (
        response.json().get("error") == expected_error
    ), f"Expected '{expected_error}' for stake {stake}, got: {response.json()}"

    balance_after = api.get_current_balance()
    assert balance_after == pytest.approx(
        clean_balance, abs=0.01
    ), f"Balance moved from {clean_balance} to {balance_after} on a rejected bet"


@allure.title("Boundary stake ({stake}) is accepted")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.api
@pytest.mark.parametrize("stake", [BusinessRules.STAKE_MIN, BusinessRules.STAKE_MAX])
def test_boundary_stake_is_accepted(
    api: BettingApiClient,
    match_id: str,
    clean_balance: float,
    stake: float,
):
    """Checking the valid edges too, not just the rejections - a validator
    that's too strict is as much a bug as one that's too loose."""

    response = api.place_bet(match_id=match_id, selection="HOME", stake=stake)

    assert response.status_code == 200, (
        f"Stake {stake} is within range but returned {response.status_code}. "
        f"Response: {response.text}"
    )

    body = response.json()

    assert (
        body["currency"] == BusinessRules.CURRENCY
    ), f"Expected currency {BusinessRules.CURRENCY}, got {body['currency']}"

    expected_payout = round(stake * body["odds"], 2)
    assert body["payout"] == pytest.approx(expected_payout, abs=0.01), (
        f"Payout {body['payout']} does not equal stake x odds "
        f"({stake} x {body['odds']} = {expected_payout})"
    )

    expected_balance = round(clean_balance - stake, 2)
    assert body["balance"] == pytest.approx(
        expected_balance, abs=0.01
    ), f"Balance in response is {body['balance']}, expected {expected_balance}"
