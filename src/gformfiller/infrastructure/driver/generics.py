# gformfiller/infrastructure/driver/generics.py

"""WebDriver factory for configuring browser drivers"""

import logging
from selenium.webdriver.remote.webdriver import WebDriver

logger = logging.getLogger(__name__)


def configure_timeouts(
    driver: WebDriver,
    page_load_timeout: int,
    script_timeout: int,
    implicit_wait: int,
) -> None:
    """Configure driver timeouts"""
    
    try:
        # Page load timeout
        driver.set_page_load_timeout(page_load_timeout)
        logger.debug(f"Page load timeout set to {page_load_timeout}s")
        
        # Script timeout
        driver.set_script_timeout(script_timeout)
        logger.debug(f"Script timeout set to {script_timeout}s")
        
        # Implicit wait (discouraged, but configurable)
        if implicit_wait > 0:
            driver.implicitly_wait(implicit_wait)
            logger.warning(
                f"Implicit wait set to {implicit_wait}s. "
                "Consider using explicit waits instead."
            )
    
    except Exception as e:
        logger.error(f"Failed to configure timeouts: {e}")
        # Non-critical, continue anyway


def quit_webdriver(driver: WebDriver | None = None) -> None:
    """
    Safely quit WebDriver
    
    Args:
        driver: WebDriver instance to quit
    """
    if driver:
        try:
            driver.quit()
            logger.info("WebDriver quit successfully")
        except Exception as e:
            logger.error(f"Error quitting WebDriver: {e}")