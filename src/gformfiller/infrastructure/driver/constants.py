# gformfiller/infrastructure/driver/constants.py

"""driver-specific constants"""

from enum import Enum


class BrowserType(Enum):
    """Supported browser types"""
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"
    SAFARI = "safari"


class PageLoadStrategy(Enum):
    """Page load strategies"""
    NORMAL = "normal"      # Wait for full page load
    EAGER = "eager"        # Wait for DOM ready
    NONE = "none"          # Don't wait


DEFAULT_PAGE_LOAD_STRATEGY = PageLoadStrategy.NORMAL.value

# Default user agents (if not specified)
DEFAULT_USER_AGENTS = {
    "chrome": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "firefox": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "edge": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
}

# Docker/CI specific options
DOCKER_CHROME_ARGS = [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
]

# Default timeouts (fallback if not in config)
DEFAULT_PAGE_LOAD_TIMEOUT = 30
DEFAULT_ELEMENT_WAIT_TIMEOUT = 10
DEFAULT_SCRIPT_TIMEOUT = 5


DEFAULT_REMOTE_HOST = "localhost"
DEFAULT_REMOTE_PORT = 9222