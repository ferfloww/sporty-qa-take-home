from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from automation.utils import parse_number
from config import config
from pages.base_page import BasePage
from pages.models import MatchSelection
from utils import parse_number


class MatchList(BasePage):

    MATCH_ROWS = (By.CLASS_NAME, "matchCard")

    def get_match_cards(self) -> list["MatchCard"]:
        return [
            MatchCard(self.driver, e) for e in self.driver.find_all(*self.MATCH_ROWS)
        ]

    def get_match_card(self, index: int = 0) -> "MatchCard":
        return self.get_match_cards()[index]


class MatchCard(BasePage):

    HOME_TEAM = (By.CSS_SELECTOR, ".teamRow:nth-of-type(1) .teamName")
    AWAY_TEAM = (By.CSS_SELECTOR, ".teamRow:nth-of-type(2) .teamName")
    HOME_ODDS_BUTTON = (By.CSS_SELECTOR, "button[id$='-home']")
    AWAY_ODDS_BUTTON = (By.CSS_SELECTOR, "button[id$='-away']")
    DRAW_ODDS_BUTTON = (By.CSS_SELECTOR, "button[id$='-draw']")
    ODDS_VALUE = (By.CSS_SELECTOR, ".oddsButtonValue")

    def __init__(self, driver, element: WebElement):
        super().__init__(driver)
        self.element = element

    def get_odds(self, outcome: str) -> float:
        button = self._button_for(outcome)
        return parse_number(button.find(*self.ODDS_VALUE).text)

    def get_teams(self) -> tuple[str, str]:
        home_team = self.element.find(*self.HOME_TEAM).text.strip()
        away_team = self.element.find(*self.AWAY_TEAM).text.strip()
        return home_team, away_team

    def select(self, outcome: str) -> MatchSelection:
        button = self._button_for(outcome)

        odds = parse_number(button.find(*self.ODDS_VALUE).text)
        home_team, away_team = self.get_teams()

        button.click()

        return MatchSelection(home_team, away_team, outcome, odds)

    def _button_for(self, outcome: str) -> WebElement:
        if outcome == "1":
            return self.element.click(*self.HOME_ODDS_BUTTON)
        elif outcome == "2":
            return self.element.click(*self.AWAY_ODDS_BUTTON)
        elif outcome == "X":
            return self.element.click(*self.DRAW_ODDS_BUTTON)
        else:
            raise ValueError(f"Unknown outcome {outcome!r}")
