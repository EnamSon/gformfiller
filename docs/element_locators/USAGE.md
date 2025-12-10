# 🚀 Element Locator Usage

This guide demonstrates how to use the `ElementLocator` class to find elements within a Google Form.

## 1. Initialization

The `ElementLocator` can be initialized with a Selenium `WebDriver` instance as the search context, and optionally, a specific `LocalizationStrategy`.

```python
from selenium.webdriver.chrome.webdriver import WebDriver # Assuming Chrome
from gformfiller.infrastructure.element_locators import (
    ElementLocator,
    LocalizationStrategy,
    GoogleFormElement,
    ElementNotFoundError
)

# Assume 'driver' is an initialized Selenium WebDriver instance
# driver: WebDriver = ...

# Initialize the locator, using XPATH as the default strategy
locator = ElementLocator(context=driver, strategy=LocalizationStrategy.XPATH)
```

## 2. Locating a Single Element

Use the locate method to find the first matching element. This method raises an ElementNotFoundError if the element is not found.

```python
try:
    # 🎯 Locate the main Submit button
    submit_button_element = locator.locate(GoogleFormElement.SUBMIT_BUTTON)
    
    # Example action: Click the button
    submit_button_element.click()
    print("Submit button clicked successfully.")

except ElementNotFoundError:
    print("Could not find the Submit button on the current page.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
```

## 3. Locating Multiple Elements

Use the locate_all method to find all matching elements. This method returns an empty list if no elements are found, and does not raise an exception.

```python
# 🎯 Locate all Question containers on the page
question_elements = locator.locate_all(GoogleFormElement.QUESTION)

if question_elements:
    print(f"Found {len(question_elements)} questions.")
    
    # You can now iterate over the question elements
    for i, question in enumerate(question_elements):
        print(f"Processing Question #{i+1}...")
        
        # Example: Locate a text input field *within* this specific question
        # Note: We create a new locator for the contextual search
        question_locator = ElementLocator(context=question)
        
        try:
            text_input = question_locator.locate(GoogleFormElement.TEXT_INPUT)
            print(f"  -> Found a Text Input field for Question #{i+1}.")
            # text_input.send_keys("My Answer")
        except ElementNotFoundError:
            # The question might be a radio or checkbox type
            print(f"  -> No Text Input found for Question #{i+1}.")

else:
    print("No question elements found.")
```

## 4. Changing the Strategy

You can change the localization strategy at any time using the set_strategy method. This is useful if you want to switch from XPATH (default/primary) to CSS_LOCATOR (secondary).

```python
# Check if the desired element has a CSS selector defined
if GoogleFormElement.SUBMIT_BUTTON.value.css_selector:
    print("Switching strategy to CSS_LOCATOR...")
    locator.set_strategy(LocalizationStrategy.CSS_LOCATOR)

    try:
        submit_button_css = locator.locate(GoogleFormElement.SUBMIT_BUTTON)
        print("Submit button located using CSS selector.")
    except ElementNotFoundError as e:
        # Note: If the selector is explicitly empty for a given Element,
        # locate() will raise an error before attempting to find the element.
        print(f"Error: {e}")

# Switch back to XPATH
locator.set_strategy(LocalizationStrategy.XPATH)
```