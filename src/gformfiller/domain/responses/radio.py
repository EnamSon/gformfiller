# gformfiller/domain/responses/radio.py

from gformfiller.infrastructure.element_locators import (
    GoogleFormElement, ElementNotFoundError
)
from gformfiller.infrastructure.dsl import match
from .base import BaseResponse
from .constants import ResponseType
from .exceptions import ElementTypeMismatchError, InvalidResponseExpressionError
import logging


logger = logging.getLogger(__name__)

class RadioResponse(BaseResponse):
    """Handler for radio button fields (single selection)."""

    def set_type(self) -> ResponseType:
        """Sets the type to RADIO and validates the presence of options."""
        try:
            self._all_radio_options = self.locator.locate_all(GoogleFormElement.RADIO)
            if not self._all_radio_options:
                raise ElementNotFoundError("RADIO", self.locator._strategy.name)
        except ElementNotFoundError as e:
            raise ElementTypeMismatchError(ResponseType.RADIO.name, self._element.tag_name) from e
            
        return ResponseType.RADIO

    def push(self, dsl_expression: str) -> bool:
        """
        Selects a single radio option based on the DSL expression.

        :param dsl_expression: The DSL expression (e.g., "Option A" or "Option A | Option B").
        :return: True if exactly one radio option was successfully clicked.
        """

        found_match = False
        
        for radio_option in self._all_radio_options:
            option_label = radio_option.get_attribute("aria-label")
            
            if not option_label:
                logger.warning(f"Skipping radio option element without aria-label.")
                continue

            try:
                is_selected = match(text=option_label, expression=dsl_expression)
            except Exception as e:
                logger.error(f"DSL evaluation failed for expression '{dsl_expression}' against option '{option_label}': {e}", exc_info=True)
                raise InvalidResponseExpressionError(self.response_type.name, dsl_expression, "DSL evaluation error.") from e

            if is_selected is True:
                if not radio_option.is_selected():
                    try:
                        radio_option.click()
                        logger.info(f"Clicked radio option: '{option_label}' matching expression '{dsl_expression}'.")
                        found_match = True
                        break
                    except Exception as e:
                        logger.error(f"Failed to click radio option '{option_label}': {e}", exc_info=True)
                        raise e
                else:
                    logger.debug(f"Radio option '{option_label}' is already selected.")
                    found_match = True

        if not found_match:
            logger.warning(f"No radio option found matching expression: {dsl_expression}")
            return False
            
        return found_match