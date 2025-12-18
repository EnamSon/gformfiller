# gformfiller/domain/responses/text.py

from gformfiller.infrastructure.element_locators import (
    GoogleFormElement, ElementNotFoundError
)
from .base import BaseResponse
from .constants import ResponseType
from .exceptions import ElementTypeMismatchError
import logging

logger = logging.getLogger(__name__)

class TextResponse(BaseResponse):
    """Handler for short answer and paragraph text input fields."""

    def set_type(self) -> ResponseType:
        """Sets the type to TEXT and validates the element presence."""
        try:
            self._input_element = self.locator.locate(GoogleFormElement.TEXT_INPUT)
        except ElementNotFoundError:
            raise ElementTypeMismatchError(ResponseType.TEXT.name, self._element.tag_name)
        return ResponseType.TEXT

    def push(self, dsl_expression: str) -> bool:
        """
        Pushes the text represented by the DSL expression into the input field.
        For Text fields, the DSL expression is treated as the literal text to enter.

        :param dsl_expression: The text to be entered.
        :return: True if successful.
        """
        self._input_element.clear()
        self._input_element.send_keys(dsl_expression)
        logger.info(
            f"Successfully set Date field to '{dsl_expression}'."
        )
        return True