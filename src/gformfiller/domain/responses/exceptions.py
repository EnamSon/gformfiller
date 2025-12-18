# gformfiller/domain/responses/exceptions.py

class ResponseException(Exception):
    """Base class for all response module exceptions."""
    pass

class ElementTypeMismatchError(ResponseException):
    """
    Raised when the concrete Response class is initialized with a WebElement
    that does not match the expected type (e.g., trying to use TextResponse on a Checkbox).
    """
    def __init__(self, expected_type: str, actual_element_html: str):
        super().__init__(
            f"The provided WebElement is not a valid element for a '{expected_type}' response. "
            f"Element HTML fragment: '{actual_element_html[:50]}...'"
        )

class InvalidResponseExpressionError(ResponseException):
    """
    Raised when the DSL expression provided to the push() method is invalid
    for the specific response type (e.g., using a sequence operator on a single-choice question).
    """
    def __init__(self, response_type: str, expression: str, reason: str):
        super().__init__(
            f"Invalid response expression for {response_type}: '{expression}'. Reason: {reason}"
        )

class QuestionNotAFormQuestionError(ResponseException):
    """
    Raised when the provided WebElement does not represent a valid GForm question container.
    """
    def __init__(self):
        super().__init__(
            "The provided WebElement does not appear to be a Google Form question container."
        )