"""Match list page - loads the app and hands back match cards."""

from selenium.webdriver.common.by import By

from config import config
from pages.base_page import BasePage
from pages.components.match_list import BetSlip, MatchList
from utils import parse_number


class HomePage(BasePage):

    HEADER_BALANCE = (By.ID, "header-balance")

    def __init__(self, driver):
        super().__init__(driver)
        self.matches = MatchList(driver)

    def open(self) -> "HomePage":
        self.driver.get(config.app_url)
        self.find(self.HEADER_BALANCE)
        return self

    def get_header_balance(self) -> float:
        return parse_number(self.get_text(self.HEADER_BALANCE))
