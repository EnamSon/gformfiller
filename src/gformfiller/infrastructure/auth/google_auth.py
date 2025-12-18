# gformfiller/infrastructure/auth/google_auth.py

import logging
import time
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException


logger = logging.getLogger(__name__)

class GoogleAuth:
    _SIGNIN_URL = "https://accounts.google.com/"
    _SUCCESS_URL_PREFIX = "https://myaccount.google.com" 
    _DEFAULT_WAIT_TIME = 300.0 

    def __init__(self, driver: WebDriver, wait_time: float = _DEFAULT_WAIT_TIME):
        self._driver = driver
        self._wait_time = wait_time

    def sign_in(self) -> bool:
        """
        Navigates to the Google sign-in page and waits for the user to sign in 
        by monitoring the URL change away from the initial sign-in page.

        :return: True if successful sign-in is detected, False otherwise.
        """
        logger.info(f"Navigating to Google Sign-In page: {self._SIGNIN_URL}")
        self._driver.get(self._SIGNIN_URL)
        
        logger.warning(
            f"Please sign in manually within {self._wait_time} seconds. "
            f"The script will wait until the URL is NO LONGER the sign-in URL..."
        )

        try:
            # Wait until the URL has changed AND is no longer the sign-in URL.
            # This handles immediate redirects back to the original application.

            #WebDriverWait(self._driver, self._wait_time).until_not(
            #    EC.url_matches(self._SIGNIN_URL)
            #)

            email = WebDriverWait(self._driver, self._wait_time).until(
                EC.presence_of_element_located((By.XPATH, './/meta[@name="og-profile-acct"]'))
            ).get_attribute("content")

            time.sleep(1.0)
            logger.info(f"Successful Google sign-in detected. Current URL: {self._driver.current_url}")
            return True

        except TimeoutException:
            meta = self._driver.find_element(By.XPATH, ".//meta[@name='og-profile-acct']")
            email = meta.get_attribute("content")
            return True
        except NoSuchElementException:
            logger.error(f"Sign-in timed out after {self._wait_time} seconds. The URL did not change away from '{self._SIGNIN_URL}'.")
            return False
        except Exception as e:
            logger.critical(f"An unexpected error occurred during the sign-in process: {e}", exc_info=True)
            return False