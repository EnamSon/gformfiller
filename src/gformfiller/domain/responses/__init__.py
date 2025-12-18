# gformfiller/domain/responses/__init__.py

import logging
from typing import Type, List
from selenium.webdriver.remote.webelement import WebElement

from gformfiller.infrastructure.element_locators import GoogleFormElement, ElementLocator

from .base import BaseResponse
from .constants import ResponseType
from .exceptions import (
    ResponseException,
    QuestionNotAFormQuestionError,
    ElementTypeMismatchError,
    InvalidResponseExpressionError
)

from .text import TextResponse
from .date import DateResponse
from .time import TimeResponse
from .checkbox import CheckboxResponse
from .radio import RadioResponse
from .listbox import ListboxResponse
from .file_upload import FileUploadResponse


RESPONSE_HANDLERS: List[Type[BaseResponse]] = [
    FileUploadResponse, 
    TimeResponse,       
    DateResponse,       
    CheckboxResponse, 
    RadioResponse,      
    ListboxResponse,    
    TextResponse,       
]

logger = logging.getLogger(__name__)


def _validate_question_element(element: WebElement):
    """
    Performs the necessary checks from BaseResponse.__init__ to ensure 
    the element is a valid GForm question container, without instantiating 
    the abstract class.
    
    :raises QuestionNotAFormQuestionError: If the element is invalid.
    """
    if element.get_attribute("role") != "listitem":
         raise QuestionNotAFormQuestionError()

    locator = ElementLocator(context=element)

    if not locator.locate_all(GoogleFormElement.QUESTION_DESCRIPTION):
        raise QuestionNotAFormQuestionError()


def identify_response_type(question_element: WebElement) -> BaseResponse:
    """
    Identifies the specific type of response handler for a given Google Form question element.
    """
    
    try:
        _validate_question_element(question_element)
        logger.debug("Question element passed initial BaseResponse validation.")
    except QuestionNotAFormQuestionError:
        logger.error("Element failed BaseResponse validation (not a listitem or missing description).")
        raise

    for Handler in RESPONSE_HANDLERS:
        try:
            handler_instance = Handler(question_element)
            logger.info(f"Question successfully identified as: {handler_instance.response_type.name}")
            return handler_instance
        
        except ElementTypeMismatchError:
            logger.debug(f"Question did not match type: {Handler.__name__}. Trying next.")
            continue
        except Exception as e:
            logger.error(f"Unexpected error during handler initialization for {Handler.__name__}: {e}", exc_info=True)
            continue

    raise ElementTypeMismatchError("Unknown", f"The question element did not match any known GForm response type.")


__all__ = [
    'BaseResponse',
    'TextResponse',
    'DateResponse',
    'TimeResponse',
    'CheckboxResponse',
    'RadioResponse',
    'ListboxResponse',
    'FileUploadResponse',
    'ResponseType',
    'identify_response_type',
    
    # Exceptions
    'ResponseException',
    'QuestionNotAFormQuestionError',
    'ElementTypeMismatchError',
    'InvalidResponseExpressionError'
]