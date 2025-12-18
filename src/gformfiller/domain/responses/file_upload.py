# gformfiller/domain/responses/file_upload.py

from gformfiller.infrastructure.element_locators import (
    GoogleFormElement, ElementNotFoundError, ElementLocator
)
from .base import BaseResponse
from .constants import ResponseType
from .exceptions import ElementTypeMismatchError, InvalidResponseExpressionError
import logging
import os 
import time

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchFrameException, NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement

logger = logging.getLogger(__name__)


class FileUploadResponse(BaseResponse):
    """Handler for file upload fields that require interaction with a picker iframe."""

    _PICKER_WAIT_TIME = 5.0
    _INPUT_WAIT_TIME = 5.0
    _UPLOAD_COMPLETE_WAIT_TIME = 30.0

    def set_type(self) -> ResponseType:
        """
        Sets the type to FILE_UPLOAD and validates the presence of the file input element.
        """
        try:
            self._file_list: WebElement = self.locator.locate(GoogleFormElement.LIST)
            self._file_button: WebElement = self.locator.locate(GoogleFormElement.BUTTON)
            
        except ElementNotFoundError as e:
            raise ElementTypeMismatchError(ResponseType.FILE_UPLOAD.name, self._element.tag_name) from e
            

        self._driver = self._file_button.parent
        try:
             while self._driver.__class__.__name__ not in ['WebDriver', 'Chrome', 'Firefox'] and hasattr(self._driver, 'parent') and self._driver.parent:
                 self._driver = self._driver.parent
        except Exception as e:
             logger.warning(f"Could not cleanly determine WebDriver instance: {e}")
             if not hasattr(self._driver, 'execute_script'):
                 raise RuntimeError("Could not determine a valid WebDriver instance for global operations (e.g., iframe cleanup).")

        return ResponseType.FILE_UPLOAD

    def _remove_all_frames(self) -> None:
        """
        Remove all frames on form using a JavaScript injection. 
        This is necessary to prevent old file pickers from masking the new one.
        """
        logger.debug("Executing JavaScript to forcefully remove all iframes from the DOM.")
        self._driver.execute_script(
            "document.querySelectorAll('iframe').forEach(iframe => iframe.remove())"
        )
        logger.debug("All iframes removed.")


    def _clean_driver_context(self) -> None:
        """
        Ensures the WebDriver is in the default content and removes all iframe elements.
        """
        logger.debug("Starting context cleanup: Switching to default content and removing all iframes.")
        try:
            self._driver.switch_to.default_content()
            logger.debug("Successfully switched to default content.")

            self._remove_all_frames()

        except Exception as e:
            logger.warning(f"Error during context cleanup, attempting to proceed: {e}")


    def _get_picker_button(self) -> None:
        """
        Clicks the file button, waits for the picker iframe to load, and switches context to the iframe.
        """
        logger.debug("Attempting to open file picker and switch to iframe.")
        self._file_button.click()
        
        try:
            WebDriverWait(self._driver, self._PICKER_WAIT_TIME).until(
                EC.frame_to_be_available_and_switch_to_it((By.XPATH, GoogleFormElement.PICKER.value.xpath))
            )
            logger.debug("Switched to file picker iframe successfully.")

            self._picker_button = self._driver.find_element(
                By.XPATH, GoogleFormElement.BUTTON.value.xpath
            )
        except TimeoutException as e:
            logger.error(f"Timeout while waiting for file picker iframe or button.")
            self._driver.switch_to.default_content() 
            raise ElementNotFoundError("File Picker Iframe/Button", "XPATH") from e
        except (NoSuchFrameException, NoSuchElementException) as e:
            logger.error(f"Could not find file picker iframe.")
            self._driver.switch_to.default_content() 
            raise ElementNotFoundError("File Picker Iframe", "XPATH") from e


    def _get_file_input_and_send_keys(self, path_to_file: str) -> None:
        """
        Clicks the picker button, waits for the native file input, and sends the file path.
        """
        logger.debug("Attempting to click picker button to reveal native file input.")
        self._picker_button.click()
        
        try:
            file_input = WebDriverWait(self._driver, self._INPUT_WAIT_TIME).until(
                EC.presence_of_element_located((By.XPATH, GoogleFormElement.FILE_INPUT.value.xpath))
            )
            logger.debug("Native file input found. Sending keys.")
            
            file_input.send_keys(path_to_file)
            logger.info(f"File path '{path_to_file}' sent to input element.")
            
        except TimeoutException as e:
            logger.error(f"Timeout while waiting for native file input.")
            raise ElementNotFoundError("Native File Input", "XPATH") from e
            
    def wait_loading_complete(self) -> None:
        """Waits for the upload to complete by checking for the non-empty file list (in default content)."""
        logger.debug("Waiting for file upload completion.")
        try:
            WebDriverWait(self._file_list, self._UPLOAD_COMPLETE_WAIT_TIME).until(
                EC.presence_of_element_located((
                    By.XPATH, GoogleFormElement.ANY.value.xpath 
                ))
            )
            logger.info("File upload confirmed as complete.")
        except TimeoutException as e:
            logger.error("Timeout: File upload did not complete within the allotted time.")
            raise ElementNotFoundError("File Upload Success Indicator", "XPATH") from e

    def push(self, dsl_expression: str) -> bool:
        """
        Executes the full complex file upload workflow.

        :param dsl_expression: The local file path string.
        :return: True if the file path was successfully sent and upload confirmed.
        """
        if ElementLocator(self._file_list).locate_all(GoogleFormElement.ANY):
            logger.warning(f"File already uploaded.")
            return True

        path_to_file = dsl_expression.strip()
        
        if not path_to_file or not os.path.exists(path_to_file):
            logger.error(f"File path invalid or file not found locally: {path_to_file}")
            raise InvalidResponseExpressionError(
                self.response_type.name,
                path_to_file,
                f"File not found locally: {path_to_file}"
            )
        
        path_to_file = os.path.abspath(path_to_file)
        
        try:
            self._clean_driver_context()
            self._get_picker_button()
            self._get_file_input_and_send_keys(path_to_file)
            self._driver.switch_to.default_content()
            logger.debug("Switched back to default content.")
            self.wait_loading_complete()
            return True
            
        except Exception as e:
            logger.error(
                f"Full file upload process failed for file '{path_to_file}'. Attempting cleanup.", 
                exc_info=True
            )

            self._clean_driver_context()
            raise