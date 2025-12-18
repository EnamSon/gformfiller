# gformfiller/domain/form_filler.py

import logging
from typing import Dict, List, Optional, Type, Any
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

from gformfiller.infrastructure.element_locators import GoogleFormElement, ElementLocator, ElementNotFoundError
from gformfiller.infrastructure.dsl import match 
from gformfiller.domain.responses import (
    identify_response_type, 
    ElementTypeMismatchError, 
    InvalidResponseExpressionError,
    BaseResponse
)
from gformfiller.domain.responses import (
    TextResponse, DateResponse, TimeResponse, CheckboxResponse, 
    RadioResponse, ListboxResponse, FileUploadResponse
)
from gformfiller.domain.ai import create_ai_client, LLMClient, AIClientException
from gformfiller.domain.ai.constants import NA_VALUE
import os
import time
import base64
from datetime import datetime 


# Type alias for the data structure: 
# ResponseType (str) -> Dict[QuestionDsl (str), AnswerDsl (str)]
FormData = Dict[str, Dict[str, str]]

# Mapping to find the corresponding key in FormData from the Python class
REVERSE_CLASS_MAP: Dict[Type[BaseResponse], str] = {
    TextResponse: 'TextResponse',
    DateResponse: 'DateResponse',
    TimeResponse: 'TimeResponse',
    CheckboxResponse: 'CheckboxResponse',
    RadioResponse: 'RadioResponse',
    ListboxResponse: 'ListboxResponse',
    FileUploadResponse: 'FileUploadResponse',
}


logger = logging.getLogger(__name__)


class FormFiller:
    """
    Orchestrates the process of filling the form based on a data structure 
    that defines the response type, the question DSL, and the answer DSL.
    The primary logic is to find all questions on the page, identify their type, 
    and then match the question text against the provided DSL expressions.
    """
    
    _DEFAULT_WAIT_TIME = 10.0

    def __init__(
        self, 
        driver: WebDriver, 
        form_data: Optional[FormData] = None,
        ai_client: Optional[LLMClient] = None,
        user_context: Optional[str] = None,
        max_retries: int = 1,
        submit: bool = False,
        screenshots_dir: Optional[str] = None,
        output_dir: Optional[str] = None
    ):
        """
        Initializes the FormFiller.
        
        :param driver: The Selenium WebDriver instance.
        :param form_data: The nested dictionary containing answers.
        :param max_retries: Maximum number of fill attempts per question.
        :param submit: If True, automatically submits the form after the last page.
        :param screenshots_dir: Path to the folder to save screenshots, or None to disable.
        """
        self._driver = driver
        self._form_data = form_data
        self._ai_client = ai_client
        self._user_context = user_context
        self._max_retries = max_retries
        self._should_submit = submit
        self._current_page = 0 # Track current page index (0-based)
        
        self._global_locator = ElementLocator(context=self._driver)
        
        self._failed_questions: List[str] = []
        
        # Directories management
        self._screenshots_dir = self._initialize_dir(screenshots_dir, "Screenshots")
        self._output_dir = self._initialize_dir(output_dir, "Output (PDF)")

        # Cache
        self._page = -1
        self._questions: list[WebElement] = []

    def _initialize_dir(self, path: Optional[str], label: str) -> Optional[str]:
        """Utility to ensure directory exists."""
        if path:
            try:
                os.makedirs(path, exist_ok=True)
                logger.info(f"{label} will be saved to: {os.path.abspath(path)}")
                return path
            except Exception as e:
                logger.error(f"Failed to create {label} directory '{path}': {e}")
        return None

    def _take_screenshot(self, filename: str):
        """
        Takes a screenshot of the browser and saves it to the specified directory.
        
        :param filename: The base name for the file (without extension or path).
        """
        if not self._screenshots_dir:
            return

        # Use a timestamp to ensure uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        full_filename = f"{filename}_{timestamp}.png"
        full_path = os.path.join(self._screenshots_dir, full_filename)
        
        try:
            self._driver.save_screenshot(full_path)
            logger.debug(f"Screenshot saved: {full_path}")
        except Exception as e:
            logger.error(f"Could not save screenshot to {full_path}. Error: {e}")

    def save_page_as_pdf(self, filename: str):
        """
        Prints the current page to PDF using Chrome DevTools Protocol.
        """
        if not self._output_dir:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        full_path = os.path.join(self._output_dir, f"{filename}_{timestamp}.pdf")
        
        try:
            # Use CDP (Chrome DevTools Protocol) to print to PDF
            print_options = {
                'landscape': False,
                'displayHeaderFooter': False,
                'printBackground': True,
                'preferCSSPageSize': True,
            }
            # execute_cdp_cmd is available in Chrome/Edge drivers
            result = self._driver.execute_cdp_cmd("Page.printToPDF", print_options)
            
            with open(full_path, "wb") as f:
                f.write(base64.b64decode(result['data']))
                
            logger.info(f"Page saved as PDF: {full_path}")
        except Exception as e:
            logger.error(f"Failed to save PDF to {full_path}. Error: {e}")

    def _extract_page_questions_data(self) -> List[Dict[str, Any]]:
        """Scans the page to identify questions and their metadata."""
        elements = self._locate_all_questions()
        data = []

        for elem in elements:
            text = self._get_question_text(elem)
            if not text: continue

            try:
                handler = identify_response_type(elem)
                # Capture specific options for Radio/Checkboxes/Listbox
                options = getattr(handler, 'options', None)
                
                data.append({
                    "text": text,
                    "type": handler.__class__.__name__,
                    "options": options,
                    "handler": handler
                })
            except Exception as e:
                logger.debug(f"Could not identify handler for question '{text}': {e}")
                continue
        return data

    def _locate_all_questions(self) -> List[WebElement]:
        """Locates all potential question containers on the current page."""
        logger.debug("Locating all question containers on the current page.")

        if self._current_page != self._page:
            self._page = self._current_page
            self._questions = self._global_locator.locate_all(GoogleFormElement.QUESTION)

        return self._questions

    def _get_question_text(self, question_element: WebElement) -> Optional[str]:
        """Retrieves the main text of the question."""
        return question_element.text.strip()

    def _attempt_to_fill_question(
        self, 
        handler: BaseResponse, 
        response_dsl: str,
        question_dsl: str
    ) -> bool:
        """
        Attempts to push the answer using the already initialized handler.
        
        :param handler: The initialized BaseResponse subclass instance.
        :param response_dsl: The DSL expression for the answer (e.g., "optionA | optionB").
        :param question_dsl: The DSL expression used to match the question (for logging/screenshots).
        """
        try:
            success = handler.push(response_dsl)
            
            if success:
                logger.info(f"Successfully filled question matching DSL '{question_dsl}' ({handler.response_type.name}).")
                return True
            else:
                logger.warning(f"Handler {handler.response_type.name} returned False for question matching DSL '{question_dsl}'.")
                self._take_screenshot(f"FAIL_FILL_{handler.response_type.name}") 
                return False

        except Exception as e:
            logger.error(f"FATAL ERROR during processing of question matching DSL '{question_dsl}'. Details: {e}", exc_info=True)
            self._take_screenshot(f"FAIL_FATAL") 
            return False

    def _fill_question(
        self, 
        handler: BaseResponse, 
        response_dsl: str,
        question_dsl: str
    ) -> bool:
        # Attempt to fill the question with retry management
        for attempt in range(self._max_retries):
            if self._attempt_to_fill_question(
                handler, 
                response_dsl, 
                question_dsl
            ):
                return True
        return False

    def fill_current_page_with_dsl(self, form_data: FormData) -> int:
        """
        Fills all questions found on the current form page by matching their text 
        against the DSL expressions in form_data.
        
        :return: The number of questions successfully filled.
        """
        questions_on_page = self._locate_all_questions()
        logger.info(f"Found {len(questions_on_page)} potential questions on the current page.")

        filled_count = 0
        
        for i, question_element in enumerate(questions_on_page):
            question_text = self._get_question_text(question_element)
            
            if question_text is None:
                continue

            try:
                handler: BaseResponse = identify_response_type(question_element)
                type_name = REVERSE_CLASS_MAP.get(handler.__class__)
                if not type_name:
                    continue

                response_map = form_data.get(type_name, {})
                
            except Exception:
                continue

            for question_dsl, response_dsl in response_map.items():
                if match(text=question_text, expression=question_dsl):
                    if self._fill_question(
                        handler,
                        response_dsl,
                        question_dsl,
                    ):
                        filled_count += 1
                        break

        logger.info(f"Page filling complete. {filled_count} questions filled from the data.")
        return filled_count

    def fill_current_page_with_ai(self, ai_client: LLMClient, user_context: str) -> int:
        """Fills the current page questions using AI batch processing."""
        filled_count = 0

        questions_data = self._extract_page_questions_data()
        logger.info(f"Found {len(questions_data)} potential questions on the current page.")

        if not questions_data:
            return filled_count

        try:
            ai_input = [{k: v for k, v in q.items() if k != 'handler'} for q in questions_data]
            response = ai_client.generate_page_answers(ai_input, user_context)
            
            for i, q in enumerate(questions_data):
                if i >= len(response.answers): break
                
                answer = response.answers[i]
                if answer == NA_VALUE: continue

                handler = q['handler']
                if self._fill_question(handler, answer, q["text"]):
                    filled_count += 1

        except AIClientException as e:
            logger.error(f"AI Batch filling failed: {e}")
            self._take_screenshot("AI_FAILURE")

        logger.info(f"Page filling complete. {filled_count} questions filled with ai.")
        return filled_count

    def _navigate_to_next_page(self) -> bool:
        """Attempts to click the 'Next' button if present, handling the first section special case."""
        # Check if the final page is reached
        try:
            self._global_locator.locate(GoogleFormElement.SUBMIT_BUTTON)
            logger.info("Submit button detected, last page of the form reached.")
            return False
        except ElementNotFoundError:
            pass

        if self._current_page == 0:
            button_element = GoogleFormElement.NEXT_BUTTON_ON_FIRST_SECTION
        else:
            button_element = GoogleFormElement.NEXT_BUTTON
            
        try:
            next_button = self._global_locator.locate(button_element)
            next_button.click()

            self._current_page += 1
            logger.info(f"Clicked 'Next' button to navigate to the next section (Now on page {self._current_page + 1}).")
            return True
        except ElementNotFoundError:
            logger.debug(f"No '{button_element.name}' button found on the current page.")
            return False
        except Exception as e:
            logger.error(f"Error during 'Next' button click: {e}", exc_info=True)
            self._take_screenshot("FAIL_NEXT_BUTTON")
            return False

    def submit(self) -> bool:
        """Attempts to click the 'Submit' button if present."""
        if not self._should_submit:
            logger.info("Submission skipped as per configuration (submit=False).")
            return False
            
        try:
            submit_button = self._global_locator.locate(GoogleFormElement.SUBMIT_BUTTON)
            submit_button.click()
            logger.info("Clicked 'Submit' button. Form submission complete.")
            self._take_screenshot("SUCCESS_SUBMIT")
            return True
        except ElementNotFoundError:
            logger.error("Attempted to submit form, but no 'Submit' button was found.")
            self._take_screenshot("FAIL_SUBMIT_NOT_FOUND")
            return False
        except Exception as e:
            logger.error(f"Error during form submission: {e}", exc_info=True)
            self._take_screenshot("FAIL_SUBMIT_ERROR")
            return False

    def run(self) -> bool:
        """Main entry point. Fills the entire form, navigating pages as necessary."""
        logger.info("Starting form filling process.")
        
        success = False
        try:
            while True:
                logger.info(f"--- Starting Page {self._current_page + 1} ---")
                
                if self._ai_client is not None and self._user_context is not None:
                     self.fill_current_page_with_ai(self._ai_client, self._user_context)
                elif self._form_data is not None:
                    self.fill_current_page_with_dsl(self._form_data)
                time.sleep(1.0)

                if self._output_dir:
                    self.save_page_as_pdf(f"Page_{self._current_page + 1}_Filled")

                if self._navigate_to_next_page():
                    time.sleep(1.0)
                    continue
                elif self.submit():
                    time.sleep(1.0)
                    self.save_page_as_pdf(f"Page_after_submittion")
                    success = True
                    break
                
                else:
                    if not self._should_submit:
                        logger.info("Form filling successful (stopped after the last page, submission skipped).")
                        success = True
                        break
                    else:
                        logger.error(f"Process halted on page {self._current_page + 1}. Could not find 'Next' or 'Submit' button.")
                        self._take_screenshot("FAIL_HALTED")
                        break
        except Exception as e:
             logger.critical(f"UNHANDLED CRITICAL ERROR during form filling: {e}", exc_info=True)
             self._take_screenshot("FAIL_CRITICAL_UNHANDLED")
             success = False
             
        logger.info("Form filling process finished.")
        return success