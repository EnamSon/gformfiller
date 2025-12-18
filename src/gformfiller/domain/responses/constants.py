# gformfiller/domain/responses/constants.py

from enum import Enum, auto

class ResponseType(Enum):
    """Enumeration of supported Google Form response types."""
    TEXT = auto()
    DATE = auto()
    TIME = auto()
    FILE_UPLOAD = auto()
    CHECKBOXES = auto()
    RADIO = auto()
    LISTBOX = auto()