# tests/unit/infrastructure/element_locators/test_element_locator.py

import pytest
from unittest.mock import Mock, patch
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from gformfiller.infrastructure.element_locators.constants import GoogleFormElement, LocalizationStrategy
from gformfiller.infrastructure.element_locators.element_locator import (
    ElementLocator, 
    ElementNotFoundError, 
    InvalidStrategyError
)

# --- Mocks for simulating Selenium ---

@pytest.fixture
def mock_context():
    """Mocks a WebDriver or WebElement instance for testing."""
    return Mock()

@pytest.fixture
def locator(mock_context):
    """Initializes ElementLocator with a mock context."""
    return ElementLocator(mock_context)

# --- Core Locator Tests ---

# Test 1: Verify that find_element is called with the correct XPATH for various elements
@pytest.mark.parametrize("element_enum, expected_xpath", [
    (GoogleFormElement.SUBMIT_BUTTON, "//div[@role='button' and @aria-label='Submit']"),
    (GoogleFormElement.TEXT_INPUT, ".//input[@type='text' or @type='email' or @type='url' or @type='date'] | .//textarea"),
    (GoogleFormElement.QUESTION_DESCRIPTION, ".//div[@role='heading']/following-sibling::div[1]"),
    (GoogleFormElement.NEXT_BUTTON, "(//div[@role='list']/following-sibling::div[1]//div[@role='button' and not(@aria-label='Submit')])[2]")
])
def test_locate_calls_find_element_with_correct_xpath(locator, mock_context, element_enum, expected_xpath):
    # Configure the mock to return a simulated result
    mock_element = Mock()
    mock_context.find_element.return_value = mock_element

    # Call the method under test
    found_element = locator.locate(element_enum)

    # Assertions: Check if Selenium's method was called correctly
    mock_context.find_element.assert_called_once_with(By.XPATH, expected_xpath)
    assert found_element == mock_element

# Test 2: Verify that locate_all is called with the correct XPATH and returns all elements
def test_locate_all_calls_find_elements(locator, mock_context):
    expected_xpath = "//div[@role='button' and @aria-label='Submit']"
    
    # Configure the mock to return a list of simulated results
    mock_elements = [Mock(), Mock(), Mock()]
    mock_context.find_elements.return_value = mock_elements

    found_elements = locator.locate_all(GoogleFormElement.SUBMIT_BUTTON)

    # Assertions
    mock_context.find_elements.assert_called_once_with(By.XPATH, expected_xpath)
    assert found_elements == mock_elements
    assert len(found_elements) == 3

# Test 3: Verify that locate raises ElementNotFoundError if Selenium fails
def test_locate_raises_element_not_found_error(locator, mock_context):
    # Configure the mock to simulate a Selenium search failure
    mock_context.find_element.side_effect = NoSuchElementException("Element not found")

    with pytest.raises(ElementNotFoundError) as excinfo:
        locator.locate(GoogleFormElement.QUESTION)
    
    # Assert that the error message contains the element name and strategy
    assert "QUESTION" in str(excinfo.value)
    assert "XPATH" in str(excinfo.value)

# --- Strategy and Edge Case Tests ---

# Test 4: Verify locating an element when switching to a strategy with an empty selector
def test_locate_raises_error_for_empty_selector(mock_context):
    # Initialize locator with CSS strategy
    locator = ElementLocator(mock_context, strategy=LocalizationStrategy.CSS_LOCATOR)

    # Since SUBMIT_BUTTON has no CSS selector in constants.py, it should fail before calling Selenium
    with pytest.raises(ElementNotFoundError) as excinfo:
        locator.locate(GoogleFormElement.SUBMIT_BUTTON)
    
    # Assertions
    assert "SUBMIT_BUTTON" in str(excinfo.value)
    assert "CSS_LOCATOR" in str(excinfo.value)
    mock_context.find_element.assert_not_called()

# Test 5: Verify locate_all returns an empty list if the selector is empty
def test_locate_all_returns_empty_list_for_empty_selector(locator, mock_context):
    # Change the strategy to CSS (which is empty for most of your elements)
    locator.set_strategy(LocalizationStrategy.CSS_LOCATOR)
    
    result = locator.locate_all(GoogleFormElement.SUBMIT_BUTTON)
    
    # Assertions
    assert result == []
    # Check that find_elements was not called unnecessarily
    mock_context.find_elements.assert_not_called()

# Test 6: Verify locate_all returns an empty list if Selenium finds nothing
def test_locate_all_returns_empty_list_when_no_elements_are_found(locator, mock_context):
    # Configure the mock to return an empty list
    mock_context.find_elements.return_value = []
    
    result = locator.locate_all(GoogleFormElement.QUESTION)
    
    # Assertions
    assert result == []
    mock_context.find_elements.assert_called_once()