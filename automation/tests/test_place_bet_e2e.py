import time

import pytest

from api.betting_client import BettingApiClient
from pages.home_page import HomePage

STAKE = "10.00"


@pytest.mark.e2e
@pytest.mark.critical
def test_place_bet_end_to_end(
    home_page: HomePage, api: BettingApiClient, clean_balance: float
):
    home_page.driver.refresh()

    starting_balance = home_page.get_header_balance()

    assert starting_balance == pytest.approx(
        clean_balance, abs=0.01
    ), f"Header shows {starting_balance} but the persisted balance is {clean_balance}"

    match_card, bet_slip = home_page.matches.get_match_card(0).select_odd_type("1")

    assert match_card.home_team == bet_slip.get_selection_teams()[0], (
        f"Bet slip home team '{bet_slip.get_selection_teams()[0]}' does not match the "
        f"match card home team '{match_card.home_team}'"
    )

    assert match_card.away_team == bet_slip.get_selection_teams()[1], (
        f"Bet slip away team '{bet_slip.get_selection_teams()[1]}' does not match the "
        f"match card away team '{match_card.away_team}'"
    )

    assert (
        match_card.odd_type == bet_slip.get_odd_type()
    ), f"Bet slip odd type '{bet_slip.get_odd_type()}' does not match the match card odd type '{match_card.odd_type}'"

    assert (
        match_card.odds == bet_slip.get_selection_odds()
    ), f"Bet slip odds '{bet_slip.get_selection_odds()}' does not match the match card odds '{match_card.odds}'"

    bet_slip.enter_stake(STAKE)

    assert bet_slip.get_potential_payout() == bet_slip.get_expected_payout(
        float(STAKE), match_card.odds
    ), f"Bet slip payout does not equal stake x odds"

    bet_slip_info, receipt_modal = bet_slip.place_bet()

    receipt_info = receipt_modal.get_receipt()

    assert bet_slip_info.home_team == receipt_info.home_team, (
        f"Receipt home team '{receipt_info.home_team}' does not match the bet slip "
        f"home team '{bet_slip_info.home_team}'"
    )

    assert bet_slip_info.away_team == receipt_info.away_team, (
        f"Receipt away team '{receipt_info.away_team}' does not match the bet slip "
        f"away team '{bet_slip_info.away_team}'"
    )

    assert receipt_info.stake == pytest.approx(
        float(STAKE), abs=0.01
    ), f"Receipt stake {receipt_info.stake} does not match the stake entered ({STAKE})"

    assert receipt_info.odds == pytest.approx(
        bet_slip_info.odds, abs=0.01
    ), f"Receipt odds {receipt_info.odds} do not match the odds selected ({bet_slip_info.odds})"

    assert receipt_info.payout == pytest.approx(bet_slip_info.payout, abs=0.01), (
        f"Receipt payout {receipt_info.payout} does not match the payout confirmed "
        f"before placement ({bet_slip_info.payout})"
    )

    expected_balance = round(starting_balance - float(STAKE), 2)

    persisted_balance = api.get_current_balance()

    assert persisted_balance == pytest.approx(expected_balance, abs=0.01), (
        f"Persisted balance is {persisted_balance}, expected "
        f"{expected_balance} ({starting_balance} - {STAKE})"
    )

    bet_slip = receipt_modal.close_receipt()

    home_page.driver.refresh()

    displayed_balance = home_page.get_header_balance()
    assert displayed_balance == pytest.approx(
        expected_balance, abs=0.01
    ), f"Header shows {displayed_balance} but the persisted balance is {persisted_balance}"
