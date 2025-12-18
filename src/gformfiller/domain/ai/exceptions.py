# gformfiller/domain/ai/exceptions.py

class AIClientException(Exception):
    """Base exception for all AI client errors (connection, API, or general processing)."""
    pass

class PromptGenerationError(AIClientException):
    """Raised when an error occurs during the construction of the system or user prompt."""
    pass

class InvalidResponseFormatError(AIClientException):
    """Raised when the AI response cannot be parsed into the expected format (e.g., failed JSON parsing)."""
    pass