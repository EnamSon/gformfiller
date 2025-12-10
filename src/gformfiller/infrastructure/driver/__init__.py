# gformfiller/infrastructure/driver/__init__.py

"""
Driver module initialization. 
Exposes main functions and exceptions for easy access.
"""

from .chromedriver import get_chromedriver, quit_chromedriver
from .generics import configure_timeouts, quit_webdriver
from .exceptions import (
    DriverError,
    DriverCreationError,
    DriverNotFoundError,
    BrowserNotFoundError,
    RemoteConnectionError,
    UnsupportedBrowserError,
)
from .constants import (
    BrowserType,
    PageLoadStrategy,
    DEFAULT_USER_AGENTS,
)


__all__ = [
    # Main Driver Functions
    "get_chromedriver",
    "quit_chromedriver",
    "configure_timeouts",
    "quit_webdriver",

    # Exceptions
    "DriverError",
    "DriverCreationError",
    "DriverNotFoundError",
    "BrowserNotFoundError",
    "RemoteConnectionError",
    "UnsupportedBrowserError",

    # Constants
    "BrowserType",
    "PageLoadStrategy",
    "DEFAULT_USER_AGENTS",
]