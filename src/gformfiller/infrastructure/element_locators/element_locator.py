# gformfiller/infrastructure/element_locators/element_locator.py

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from typing import Union

from .constants import Element, LocalizationStrategy, GoogleFormElement
from .exceptions import InvalidStrategyError, ElementNotFoundError

class ElementLocator:
    """
    Utility class for locating a specific web element
    from a given context (WebDriver or WebElement).
    """

    def __init__(
            self,
            context: Union[WebDriver, WebElement],
            strategy: LocalizationStrategy = LocalizationStrategy.XPATH
    ):
        """
        Initializes the locator with a context and a default strategy.

        :param context: The WebDriver or WebElement object to search from.
        :param strategy: The default localization strategy (XPATH or CSS_LOCATOR).
        """
        self._context = context
        self._strategy = strategy

    def _get_selenium_by_strategy(self) -> str:
        """Converts the internal strategy to Selenium's By object."""
        if self._strategy == LocalizationStrategy.XPATH:
            return By.XPATH
        elif self._strategy == LocalizationStrategy.CSS_LOCATOR:
            return By.CSS_SELECTOR
        else:
            # This error should not occur if constants are well-defined
            raise InvalidStrategyError(self._strategy.value)

    def _get_selector_value(self, element: Element) -> str:
        """Retrieves the selector value based on the current strategy."""
        if self._strategy == LocalizationStrategy.XPATH:
            return element.xpath
        elif self._strategy == LocalizationStrategy.CSS_LOCATOR:
            return element.css_selector
        else:
            raise InvalidStrategyError(self._strategy.value)

    def locate(self, element_enum: GoogleFormElement) -> WebElement:
        """
        Locates and returns the first WebElement corresponding to the given element
        using the configured localization strategy.

        :param element_enum: An instance of GoogleFormElement (e.g., GoogleFormElement.SUBMIT_BUTTON).
        :return: The found WebElement.
        :raises ElementNotFoundError: If the element is not found within the context.
        """
        element: Element = element_enum.value
        by_strategy = self._get_selenium_by_strategy()
        selector = self._get_selector_value(element)

        if not selector:
            # If the selector is empty for the chosen strategy
            raise ElementNotFoundError(element.type.name, self._strategy.name)

        try:
            # Use find_element (singular) to find the first element
            # The context can be a WebDriver or a WebElement
            return self._context.find_element(by_strategy, selector)
        except Exception as e:
            # Selenium typically raises NoSuchElementException
            raise ElementNotFoundError(
                element.type.name,
                self._strategy.name
            ) from e

    def locate_all(self, element_enum: GoogleFormElement) -> list[WebElement]:
        """
        Locates and returns all WebElements corresponding to the given element.

        :param element_enum: An instance of GoogleFormElement.
        :return: A list of found WebElements (can be empty).
        """
        element: Element = element_enum.value
        by_strategy = self._get_selenium_by_strategy()
        selector = self._get_selector_value(element)

        if not selector:
            return []

        # Use find_elements (plural)
        return self._context.find_elements(by_strategy, selector)

    def set_strategy(self, strategy: LocalizationStrategy):
        """Changes the localization strategy."""
        self._strategy = strategy