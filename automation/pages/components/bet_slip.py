from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from pages.models import Receipt
from utils import parse_number


class BetSlip(BasePage):

    SLIP_BALANCE = (By.ID, "bet-slip")
    STAKE_INPUT = (By.ID, "bet-slip-stake-input")
    TOTAL_STAKE = (By.ID, "totalsValue")
    POTENTIAL_PAYOUT = (By.ID, "bet-slip-potential-payout")
    PLACE_BET_BUTTON = (By.ID, "bet-slip-place-bet")
    STAKE_ERROR_MESSAGE = (
        By.CSS_SELECTOR,
        ".stakeWarning > span:not(.stakeWarningIcon)",
    )

    def __init__(self, driver):
        super().__init__(driver)
        self.find(self.SLIP_BALANCE)

    def enter_stake(self, amount: str) -> "BetSlip":
        self.type_text(self.STAKE_INPUT, amount)
        return self

    def get_potential_payout(self) -> float:
        return parse_number(self.get_text(self.POTENTIAL_PAYOUT))

    def get_total_stake(self) -> float:
        return parse_number(self.get_text(self.TOTAL_STAKE))

    def get_slip_balance(self) -> float:
        return parse_number(self.get_text(self.SLIP_BALANCE))

    def is_place_bet_enabled(self) -> bool:
        return self.is_enabled(self.PLACE_BET_BUTTON)

    def get_stake_error_message(self) -> str:
        return self.get_text(self.STAKE_ERROR_MESSAGE)

    def has_stake_error_message(self, timeout: int = 3) -> bool:
        return self.is_visible(self.STAKE_ERROR_MESSAGE, timeout=timeout)

    def place_bet(self) -> "BetSlipModal":
        self.click(self.PLACE_BET_BUTTON)
        return BetSlipModal(self.driver)


class BetSlipModal(BasePage):

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

    def is_receipt_displayed(self) -> bool:
        return self.is_visible(self.RECEIPT_MODAL, timeout=5)

    def is_error_modal_displayed(self) -> bool:
        return self.is_visible(self.ERROR_MODAL_MESSAGE, timeout=3)

    def get_receipt(self) -> Receipt:
        return Receipt(
            bet_id=self.get_text(self.RECEIPT_BET_ID),
            match=self.get_text(self.RECEIPT_MATCH),
            stake=parse_number(self.get_text(self.RECEIPT_STAKE)),
            odds=parse_number(self.get_text(self.RECEIPT_ODDS)),
            payout=parse_number(self.get_text(self.RECEIPT_PAYOUT)),
        )

    def close_receipt(self) -> "BetSlip":
        self.click(self.RECEIPT_CLOSE)
        self.wait.until(lambda d: not d.find_all(*self.RECEIPT_MODAL))
        return BetSlip(self.driver)
