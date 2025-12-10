# gformfiller/infrastructure/element_locators/exceptions.py

class ElementLocatorException(Exception):
    """Base class for ElementLocator module exceptions."""
    pass

class InvalidStrategyError(ElementLocatorException):
    """Raised when the specified localization strategy is invalid or unsupported."""
    def __init__(self, strategy_value):
        super().__init__(f"Invalid localization strategy: {strategy_value}")

class ElementNotFoundError(ElementLocatorException):
    """Raised when the element cannot be found with the given strategy."""
    def __init__(self, element_name, strategy_name):
        super().__init__(f"Element not found: '{element_name}' using strategy '{strategy_name}'")