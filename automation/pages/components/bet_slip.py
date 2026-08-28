from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from pages.components.receipt_modal import ReceiptModal
from pages.models import BetSlipInfo
from utils import parse_number


class BetSlip(BasePage):

    SELECTION_TEAMS = (By.CSS_SELECTOR, ".betSelectionTeams")
    SELECTION_MARKET = (By.CSS_SELECTOR, ".betSelectionMarket")
    SELECTION_ODDS = (By.CSS_SELECTOR, ".betSelectionOdds")
    SLIP_BALANCE = (By.ID, "bet-slip")
    STAKE_INPUT = (By.ID, "bet-slip-stake-input")
    POTENTIAL_PAYOUT = (By.ID, "bet-slip-potential-payout")
    PLACE_BET_BUTTON = (By.ID, "bet-slip-place-bet")

    LABEL_TO_OUTCOME = {"HOME": "1", "DRAW": "X", "AWAY": "2"}

    def __init__(self, driver):
        super().__init__(driver)
        self.find(self.SLIP_BALANCE)

    def enter_stake(self, amount: str) -> "BetSlip":
        self.type_text(self.STAKE_INPUT, amount)
        return self

    def get_selection_teams(self) -> str:
        text = self.get_text(self.SELECTION_TEAMS)
        parts = [p.strip() for p in text.replace("\n", " ").split(" vs ")]
        return parts[0], parts[1]

    def get_odd_type(self) -> str:
        label = self.get_text(self.SELECTION_MARKET).split(":")[-1].strip().upper()
        return self.LABEL_TO_OUTCOME[label]

    def get_expected_payout(self, stake: float, odds: float) -> float:
        return round(stake * odds, 2)

    def get_selection_odds(self) -> float:
        return parse_number(self.get_text(self.SELECTION_ODDS))

    def get_potential_payout(self) -> float:
        return parse_number(self.get_text(self.POTENTIAL_PAYOUT))

    def is_place_bet_enabled(self) -> bool:
        return self.is_enabled(self.PLACE_BET_BUTTON)

    def place_bet(self) -> tuple[BetSlipInfo, ReceiptModal]:
        home_team, away_team = self.get_selection_teams()
        odds = self.get_selection_odds()
        potential_payout = self.get_potential_payout()

        if self.is_place_bet_enabled():
            self.click(self.PLACE_BET_BUTTON)

        return BetSlipInfo(
            home_team=home_team,
            away_team=away_team,
            odds=odds,
            payout=potential_payout,
        ), ReceiptModal(self.driver)
