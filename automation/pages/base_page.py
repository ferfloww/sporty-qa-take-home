"""Shared page object helpers."""

from typing import Callable

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import config


class BasePage:

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, config.EXPLICIT_WAIT)

    def find(self, locator: tuple[str, str]) -> WebElement:
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_until(
        self, locator: tuple[str, str], predicate: Callable[[str], bool]
    ) -> WebElement:
        return self.wait.until(
            lambda d: (
                d.find_element(*locator)
                if predicate(d.find_element(*locator).text)
                else False
            )
        )

    def get_text(self, locator: tuple[str, str]) -> str:
        return self.get_text_until(locator, lambda text: bool(text.strip()))

    def get_text_until(
        self, locator: tuple[str, str], predicate: Callable[[str], bool]
    ) -> str:
        return self.find_until(locator, predicate).text

    def find_all(self, locator: tuple[str, str]) -> list[WebElement]:
        self.wait.until(EC.presence_of_element_located(locator))
        return self.driver.find_elements(*locator)

    def find_any(self, *locators: tuple[str, str]) -> WebElement:
        """Espera a que aparezca cualquiera de los locators dados y devuelve el primero encontrado."""
        self.wait.until(
            lambda d: any(d.find_elements(*locator) for locator in locators)
        )

        for locator in locators:
            elements = self.driver.find_elements(*locator)
            if elements:
                return elements[0]

    def click(self, locator: tuple[str, str]) -> None:
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def type_text(self, locator: tuple[str, str], text: str) -> None:
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.clear()
        element.send_keys(text)

    def is_enabled(self, locator: tuple[str, str]) -> bool:
        element = self.find(locator)
        if not element.is_enabled():
            return False
        return element.get_attribute("aria-disabled") != "true"
