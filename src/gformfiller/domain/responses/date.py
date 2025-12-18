# gformfiller/domain/responses/date.py

from gformfiller.infrastructure.element_locators import (
    GoogleFormElement, ElementNotFoundError
)
from .base import BaseResponse
from .constants import ResponseType
from .exceptions import ElementTypeMismatchError, InvalidResponseExpressionError
import logging
import re # Used for simple date format validation

logger = logging.getLogger(__name__)


class DateResponse(BaseResponse):
    """Handler for date input fields."""

    def set_type(self) -> ResponseType:
        """Sets the type to DATE and validates the element presence."""
        try:
            self._input_element = self.locator.locate(GoogleFormElement.DATE)
        except ElementNotFoundError:
            raise ElementTypeMismatchError(ResponseType.DATE.name, self._element.tag_name)
        return ResponseType.DATE

    def push(self, dsl_expression: str) -> bool:
        """
        Pushes the date represented by the DSL expression into the input field.
        For Date fields, the DSL expression is treated as the ISO format date to enter (YYYY-MM-DD).

        :param dsl_expression: The date to be entered.
        :return: True if successful.
        :raises InvalidResponseExpressionError: If the expression is not in YYYY-MM-DD format.
        """
        date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        
        if not date_pattern.match(dsl_expression):
             logger.error(
                 f"Date input failed for expression: '{dsl_expression}'. Expected format YYYY-MM-DD."
             )
             raise InvalidResponseExpressionError(
                 self.response_type.name,
                 dsl_expression,
                 "Date must be provided in YYYY-MM-DD format."
             )

        try:
            self._input_element.clear()
            self._input_element.send_keys(dsl_expression)
            logger.info(
                f"Successfully set Date field to '{dsl_expression}'."
            )
            return True
        except Exception as e:
            logger.error(
                f"Failed to push date '{dsl_expression}' to element: {e}", 
                exc_info=True
            )
            raise e