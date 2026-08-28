from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from pages.models import Receipt
from utils import parse_number


class ReceiptModal(BasePage):

    RECEIPT_MODAL = (By.CLASS_NAME, "modalBody")
    RECEIPT_BET_ID = (By.ID, "modal-success-bet-id")
    RECEIPT_MATCH = (By.ID, "modal-success-match")
    RECEIPT_STAKE = (By.ID, "modal-success-stake")
    RECEIPT_ODDS = (By.ID, "modal-success-odds")
    RECEIPT_PAYOUT = (By.ID, "modal-success-payout")
    RECEIPT_CLOSE = (By.ID, "modal-success-close")

    ERROR_MODAL_MESSAGE = (By.ID, "modal-error-message")
    SUCCESS_MODAL_MESSAGE = (By.CLASS_NAME, "modalSuccessIcon")

    def __init__(self, driver):
        super().__init__(driver)
        self.find_any(self.SUCCESS_MODAL_MESSAGE, self.ERROR_MODAL_MESSAGE)

    def get_selection_teams(self) -> tuple[str, str]:
        text = self.get_text(self.RECEIPT_MATCH)
        parts = [p.strip() for p in text.replace("\n", " ").split(" vs ")]
        return parts[0], parts[1]

    def get_receipt(self) -> Receipt:
        home_team, away_team = self.get_selection_teams()
        return Receipt(
            bet_id=self.get_text(self.RECEIPT_BET_ID),
            home_team=home_team,
            away_team=away_team,
            stake=parse_number(self.get_text(self.RECEIPT_STAKE)),
            odds=parse_number(self.get_text(self.RECEIPT_ODDS)),
            payout=parse_number(self.get_text(self.RECEIPT_PAYOUT)),
        )

    def close_receipt(self) -> None:
        self.click(self.RECEIPT_CLOSE)
        self.wait.until(lambda d: not d.find_elements(*self.RECEIPT_MODAL))
