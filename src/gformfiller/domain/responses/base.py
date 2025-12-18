# gformfiller/domain/responses/base.py

from abc import ABC, abstractmethod
from typing import Union
from selenium.webdriver.remote.webelement import WebElement

from .constants import ResponseType
from .exceptions import QuestionNotAFormQuestionError
from gformfiller.infrastructure.element_locators import GoogleFormElement, ElementLocator

class BaseResponse(ABC):
    """
    Abstract base class for all Google Form response handlers.
    Each subclass is responsible for handling a specific type of form field.
    """

    def __init__(self, gform_question_element: WebElement):
        """
        Initializes the response handler.

        :param gform_question_element: The WebElement representing the
            *container* of the Google Form question (typically role='listitem').
        :raises QuestionNotAFormQuestionError: If the element is not a valid GForm question container.
        """
        if gform_question_element.get_attribute("role") != "listitem":
             raise QuestionNotAFormQuestionError()

        self._element = gform_question_element
        self._locator = ElementLocator(context=self._element)

        if not self._locator.locate_all(GoogleFormElement.QUESTION_DESCRIPTION):
            raise QuestionNotAFormQuestionError()

        self._type = self.set_type() # Set the concrete type upon initialization

    @abstractmethod
    def set_type(self) -> ResponseType:
        """
        Abstract method to be implemented by subclasses to define their
        specific response type.

        :return: The concrete ResponseType enum member.
        """
        pass

    @property
    def response_type(self) -> ResponseType:
        """Read-only property for the response type."""
        return self._type

    @property
    def element(self) -> WebElement:
        """Read-only property for the question container element."""
        return self._element

    @property
    def locator(self) -> ElementLocator:
        """Read-only property for the locator."""
        return self._locator

    @abstractmethod
    def push(self, dsl_expression: str) -> bool:
        """
        Applies the given DSL expression to select and interact with the
        appropriate form element(s).

        :param dsl_expression: The expression from the search DSL to process.
        :return: True if the operation was successful, False otherwise.
        :raises InvalidResponseExpressionError: If the expression is syntactically or logically invalid for the response type.
        """
        # Implementation will involve:
        # 1. Parsing the expression (using the DSL module's match/parse logic).
        # 2. Locating the actual interactive elements within self._element
        #    (using the ElementLocator module).
        # 3. Interacting with the element (e.g., click, send_keys) based on the expression.
        pass
