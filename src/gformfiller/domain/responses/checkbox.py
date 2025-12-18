# gformfiller/domain/responses/checkbox.py

from gformfiller.infrastructure.element_locators import (
    GoogleFormElement, ElementNotFoundError
)
from gformfiller.infrastructure.dsl import match
from .base import BaseResponse
from .constants import ResponseType
from .exceptions import ElementTypeMismatchError, InvalidResponseExpressionError
import logging

logger = logging.getLogger(__name__)

class CheckboxResponse(BaseResponse):
    """Handler for checkbox fields (multiple selection)."""

    def set_type(self) -> ResponseType:
        """Sets the type to CHECKBOXES and validates the presence of options."""
        try:
            self._all_checkboxes = self.locator.locate_all(GoogleFormElement.CHECKBOX)
            if not self._all_checkboxes:
                raise ElementNotFoundError("CHECKBOX", self.locator._strategy.name)
        except ElementNotFoundError as e:
            raise ElementTypeMismatchError(ResponseType.CHECKBOXES.name, self._element.tag_name) from e
            
        return ResponseType.CHECKBOXES

    def push(self, dsl_expression: str) -> bool:
        """
        Selects one or more checkboxes based on the DSL expression.

        :param dsl_expression: The DSL expression (e.g., "Option A & Option B").
        :return: True if at least one checkbox was successfully clicked.
        """
        successful_clicks = 0
        
        for checkbox in self._all_checkboxes:
            option_label = checkbox.get_attribute("aria-label")
            
            if option_label is None:
                logger.warning(f"Skipping checkbox element without aria-label in question.")
                continue
            
            try:
                is_selected = match(text=option_label, expression=dsl_expression)
            except Exception as e:
                logger.error(
                    f"DSL evaluation failed for expression '{dsl_expression}' against option '{option_label}': {e}",
                    exc_info=True
                )
                raise InvalidResponseExpressionError(self.response_type.name, dsl_expression, "DSL evaluation error.") from e

            is_checked = checkbox.get_attribute("aria-checked") == "true" or checkbox.get_attribute("checked") == "true"
            if is_selected is True:
                if not is_checked:
                    try:
                        checkbox.click()
                        successful_clicks += 1
                        logger.info(f"Clicked checkbox: '{option_label}' matching expression '{dsl_expression}'.")
                    except Exception as e:
                        logger.error(f"Failed to click checkbox '{option_label}': {e}", exc_info=True)
                else:
                    logger.debug(f"Checkbox '{option_label}' is already selected.")

            elif is_selected is False and is_checked:
                 try:
                     checkbox.click()
                     logger.info(f"Unchecked checkbox: '{option_label}' based on negative DSL match.")
                 except Exception as e:
                     logger.error(f"Failed to uncheck checkbox '{option_label}': {e}", exc_info=True)


        if successful_clicks == 0 and not self._all_checkboxes:
            logger.warning(f"No checkboxes were found or selected for expression: {dsl_expression}")
            return False
            
        return True