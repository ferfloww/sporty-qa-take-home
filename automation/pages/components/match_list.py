from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from pages.base_page import BasePage
from pages.components.bet_slip import BetSlip
from pages.models import MatchSelection
from utils import parse_number


class MatchList(BasePage):

    MATCH_ROWS = (By.CLASS_NAME, "matchCard")

    def get_match_cards(self) -> list["MatchCard"]:
        return [MatchCard(self.driver, e) for e in self.find_all(self.MATCH_ROWS)]

    def get_match_card(self, index: int = 0) -> "MatchCard":
        return self.get_match_cards()[index]


class MatchCard(BasePage):

    HOME_TEAM = (By.CSS_SELECTOR, ".teamRow:nth-of-type(1) .teamName")
    AWAY_TEAM = (By.CSS_SELECTOR, ".teamRow:nth-of-type(2) .teamName")
    HOME_ODDS_BUTTON = (By.CSS_SELECTOR, "button[id$='-home']")
    AWAY_ODDS_BUTTON = (By.CSS_SELECTOR, "button[id$='-away']")
    DRAW_ODDS_BUTTON = (By.CSS_SELECTOR, "button[id$='-draw']")
    ODDS_VALUE = (By.CSS_SELECTOR, ".oddsButtonValue")

    OUTCOME_BUTTONS = {
        "1": HOME_ODDS_BUTTON,
        "X": DRAW_ODDS_BUTTON,
        "2": AWAY_ODDS_BUTTON,
    }

    def __init__(self, driver, element: WebElement):
        super().__init__(driver)
        self.element = element

    def get_teams(self) -> tuple[str, str]:
        home_team = self.element.find_element(*self.HOME_TEAM).text.strip()
        away_team = self.element.find_element(*self.AWAY_TEAM).text.strip()
        return home_team, away_team

    def get_odds(self, odd_type: str) -> float:
        button = self.element.find_element(*self._button_locator(odd_type))
        return parse_number(button.find_element(*self.ODDS_VALUE).text)

    def select_odd_type(self, odd_type: str) -> tuple[MatchSelection, BetSlip]:
        home_team, away_team = self.get_teams()
        odds = self.get_odds(odd_type)

        button_locator = self._button_locator(odd_type)
        self.element.find_element(*button_locator).click()

        selection = MatchSelection(
            home_team=home_team,
            away_team=away_team,
            odd_type=odd_type,
            odds=odds,
        )
        return selection, BetSlip(self.driver)

    def _button_locator(self, odd_type: str) -> tuple[str, str]:
        return self.OUTCOME_BUTTONS[odd_type]
