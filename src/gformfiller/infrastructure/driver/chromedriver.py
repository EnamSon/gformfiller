# gformfiller/infrastructure/driver/chromedriver.py

"""Module for creating and configuring chromedriver"""

import logging
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeDriver
from selenium.webdriver.remote.webdriver import WebDriver

from .exceptions import DriverCreationError, DriverNotFoundError, BrowserNotFoundError
from .generics import configure_timeouts, quit_webdriver
from .constants import (
    DEFAULT_USER_AGENTS,
    DEFAULT_PAGE_LOAD_TIMEOUT,
    DEFAULT_SCRIPT_TIMEOUT,
    DEFAULT_PAGE_LOAD_STRATEGY,
    DEFAULT_REMOTE_HOST,
    DEFAULT_REMOTE_PORT,
    DOCKER_CHROME_ARGS,
)

logger = logging.getLogger(__name__)

def get_chromedriver(
    driver_path: str,
    binary_location: str | None = None,
    user_data_dir: str | None = None,
    headless: bool = False,
    port: int = 0,
    remote: bool = False,
    remote_host: str = DEFAULT_REMOTE_HOST,
    remote_port: int = DEFAULT_REMOTE_PORT,
    user_agent: str | None = None,
    disable_images: bool = False,
    no_sandbox: bool = False,
    disable_gpu: bool = False,
    disable_dev_shm: bool = False,
    page_load_strategy: str = DEFAULT_PAGE_LOAD_STRATEGY,
    page_load_timeout: int = DEFAULT_PAGE_LOAD_TIMEOUT,
    script_timeout: int = DEFAULT_SCRIPT_TIMEOUT,
    implicit_wait: int = 0,
    window_size: str | None = None
) -> ChromeDriver:
    """
    Create and configure a chromedriver instance
    
    Args:
        driver_path: Path to driver executable (optional, will auto-download if not provided)
        binary_location: Location of binary browser
        user_data_dir: Chrome profile dir (user data dir)
        headless: Run in headless mode
        remote: Connect to remote browser
        remote_host: Remote browser host
        remote_port: Remote browser debugging port
        user_agent: Custom user agent
        disable_images: Disable image loading for faster performance
        no_sandbox: Disable sandbox (for Docker/CI)
        disable_gpu: Disable GPU hardware acceleration
        disable_dev_shm: Disable /dev/shm usage (for Docker)
        page_load_strategy: Page load strategy (normal, eager, none)
        page_load_timeout: Page load timeout in seconds
        script_timeout: Script execution timeout in seconds
        implicit_wait: Implicit wait timeout in seconds
        
    Returns:
        Configured chromedriver instance
        
    Raises:
        DriverNotFoundError: If driver executable not found
        BrowserNotFoundError: If browser binary not found
        DriverCreationError: If driver creation fails
    """

    try:
        options = _get_chromeoptions(
            binary_location=binary_location,
            user_data_dir=user_data_dir,
            remote=remote,
            remote_host=remote_host,
            remote_port=remote_port,
            headless=headless,
            user_agent=user_agent,
            disable_images=disable_images,
            no_sandbox=no_sandbox,
            disable_gpu=disable_gpu,
            disable_dev_shm=disable_dev_shm,
            page_load_strategy=page_load_strategy,
            window_size=window_size
        )
        service = _get_chromeservice(driver_path, port)
        chromedriver = webdriver.Chrome(options=options, service=service)
        configure_timeouts(chromedriver, page_load_timeout, script_timeout, implicit_wait)

        logger.info("Chromedriver created successfully")
        return chromedriver

    except (DriverNotFoundError, BrowserNotFoundError):
        raise

    # Catch all other exceptions as DriverCreationError
    except Exception as e:
        logger.error(f"Failed to create WebDriver: {e}", exc_info=True)
        raise DriverCreationError("chrome", str(e))


def _get_chromeoptions(
    binary_location: str | None,
    user_data_dir: str | None,
    remote: bool,
    remote_host: str,
    remote_port: int,
    headless: bool,
    user_agent: str | None,
    disable_images: bool,
    no_sandbox: bool,
    disable_gpu: bool,
    disable_dev_shm: bool,
    page_load_strategy: str,
    window_size: str | None
) -> ChromeOptions:
    """Configure chrome options"""

    options = ChromeOptions()

    # Remote debugging
    if remote:
        options.debugger_address = f"{remote_host}:{remote_port}"
        return options

    # Binary location
    if binary_location:
        if not Path(binary_location).exists():
            raise BrowserNotFoundError("chrome", binary_location)
        options.binary_location = binary_location

    # User data dir
    if user_data_dir:
        options.add_argument(f"user-data-dir={user_data_dir}")

    # Headless
    if headless:
        options.add_argument("--headless=new")  # New headless mode
    
    # User agent
    if user_agent:
        options.add_argument(f"user-agent={user_agent}")
    elif not user_agent and headless:
        # Use default desktop user agent in headless to avoid detection
        options.add_argument(f"user-agent={DEFAULT_USER_AGENTS['chrome']}")
    
    if disable_images:
        prefs: dict[str, int] = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
    
    # Docker/CI options
    if no_sandbox:
        options.add_argument("--no-sandbox")
    
    if disable_gpu:
        options.add_argument("--disable-gpu")
    
    if disable_dev_shm:
        options.add_argument("--disable-dev-shm-usage")

    if window_size:
        options.add_argument(f'--window-size="{window_size}"')
    # Page load strategy
    options.page_load_strategy = page_load_strategy
    
    # Additional recommended options
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    # Disable unnecessary features
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-notifications")

    return options


def _get_chromeservice(
    driver_path: str,
    port: int
) -> ChromeService:

    if not Path(driver_path).exists():
        raise DriverNotFoundError("chrome", driver_path)

    return ChromeService(executable_path=driver_path, port=port)

def quit_chromedriver(chromedriver: ChromeDriver | None = None):
    quit_webdriver(chromedriver)
