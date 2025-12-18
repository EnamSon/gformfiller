# gformfiller/domain/responses/listbox.py

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from gformfiller.infrastructure.element_locators import (
    GoogleFormElement, ElementNotFoundError
)
from gformfiller.infrastructure.dsl import match
from .base import BaseResponse
from .constants import ResponseType
from .exceptions import ElementTypeMismatchError, InvalidResponseExpressionError
import logging


logger = logging.getLogger(__name__)

class ListboxResponse(BaseResponse):
    """Handler for dropdown list (listbox) fields (single selection)."""

    def set_type(self) -> ResponseType:
        """Sets the type to LISTBOX and validates the element presence."""
        try:
            self._listbox_control = self.locator.locate(GoogleFormElement.LISTBOX)
        except ElementNotFoundError as e:
            raise ElementTypeMismatchError(ResponseType.LISTBOX.name, self._element.tag_name) from e

        self._driver = self._listbox_control.parent
        try:
             while self._driver.__class__.__name__ not in ['WebDriver', 'Chrome', 'Firefox'] and hasattr(self._driver, 'parent') and self._driver.parent:
                 self._driver = self._driver.parent
        except Exception as e:
             logger.warning(f"Could not cleanly determine WebDriver instance: {e}")
             if not hasattr(self._driver, 'execute_script'):
                 raise RuntimeError("Could not determine a valid WebDriver instance for global operations (e.g., iframe cleanup).")

        self._actions = ActionChains(self._driver)

        return ResponseType.LISTBOX

    def push(self, dsl_expression: str) -> bool:
        """
        Selects a single option from the dropdown list..

        :param dsl_expression: The single term representing the option text.
        :return: True if the option was successfully selected.
        """
        try:
            self._listbox_control.click()
            logger.debug(f"Listbox control clicked to open options for selection term: '{dsl_expression}'.")

            all_options = self.locator.locate_all(GoogleFormElement.LISTBOX_OPTION)

            selected_successfully = False
            
            for option in all_options:
                option_text = option.text.strip()

                is_match = match(text=option_text, expression=dsl_expression)

                if is_match is True:
                    self._actions.move_to_element(option).click().perform()
                    selected_successfully = True
                    logger.info(f"Selected listbox option: '{option_text}' matching expression '{dsl_expression}'.")
                    break 

            if not selected_successfully:
                logger.warning(f"No listbox option found matching expression: '{dsl_expression}'.")
                return False
                
            return True
        
        except ElementNotFoundError:
            logger.error(f"Failed to find Listbox options after clicking control.")
            raise
        except Exception as e:
            logger.error(
                f"Failed to push listbox selection '{dsl_expression}': {e}", 
                exc_info=True
            )
            raise