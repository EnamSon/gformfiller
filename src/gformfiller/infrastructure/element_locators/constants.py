# gformfiller/infrastructure/element_locators/constants.py

from enum import Enum, auto
from typing import NamedTuple

# 1. Enumeration of Localization Strategies
class LocalizationStrategy(Enum):
    """Strategies for locating web elements."""
    XPATH = "xpath"
    CSS_LOCATOR = "css selector"

# 2. Enumeration of Element Types
class ElementType(Enum):
    """Common element types found on a Google Form."""
    RADIO = auto()
    CHECKBOX = auto()
    TEXT_INPUT = auto()
    DATE = auto()
    BUTTON = auto()
    SUBMIT_BUTTON = auto()
    NEXT_BUTTON = auto()
    NEXT_BUTTON_ON_FIRST_SECTION = auto()
    FILE_INPUT = auto()
    PICKER = auto() # Used when loading a file
    LISTBOX = auto()
    LISTBOX_OPTION = auto()
    QUESTION = auto()
    QUESTION_HEADING = auto()
    QUESTION_DESCRIPTION = auto()
    LIST = auto()
    NO_EMPTY_LIST = auto() # Used to check if a file has finished uploading
    TIME = auto()
    TIME_HOUR = auto()
    TIME_MINUTE = auto()

# 3. NamedTuple for Element Definition
class Element(NamedTuple):
    """Representation of an element with its localization strategies."""
    type: ElementType
    xpath: str
    css_selector: str = "" # Optional if XPATH is prioritized

# 4. Enumeration of Specific Element Instances
# This is where you define the concrete selectors for Google Forms
class GoogleFormElement(Enum):
    """Predefined instances of Google Form elements."""

    # Generic clickable buttons (often includes icons or secondary buttons)
    BUTTON = Element(
        type=ElementType.BUTTON,
        # Targets elements with role='button' or native <button> tags
        xpath=".//div[@role='button'] | .//button"
    )

    CHECKBOX = Element(
        type=ElementType.CHECKBOX,
        # Targets the input element OR the container with the ARIA role
        xpath=".//input[@type='checkbox'] | .//div[@role='checkbox']"
    )

    FILE_INPUT = Element(
        type=ElementType.FILE_INPUT,
        # Targets the native file input element
        xpath=".//input[@type='file']"
    )

    # Main submission button (Robust anchor based on ARIA label)
    SUBMIT_BUTTON = Element(
        type=ElementType.SUBMIT_BUTTON,
        # Targets the button with the stable 'Submit' ARIA label
        xpath="//div[@role='button' and @aria-label='Submit']"
    )

    # Radio button
    RADIO = Element(
        type=ElementType.RADIO,
        # Targets the container with the ARIA role OR the native input element
        xpath=".//div[@role='radio'] | .//input[@type='radio']"
    )

    # Text input field (short answer, paragraph, email)
    TEXT_INPUT = Element(
        type=ElementType.TEXT_INPUT,
        # Targets various text input types and the textarea element
        xpath=".//input[@type='text' or @type='email' or @type='url'] | .//textarea"
    )

    DATE = Element(
        type=ElementType.DATE,
        xpath=".//input[@type='date']"
    )

    # Google Picker iframe (for file upload dialog)
    PICKER = Element(
        type=ElementType.PICKER,
        # Targets the iframe containing the file picker interface
        xpath=".//iframe[contains (@src, 'picker')]"
    )

    # Dropdown list control
    LISTBOX = Element(
        type=ElementType.LISTBOX,
        # Targets the main listbox control element
        xpath=".//div[@role='listbox']"
    )

    # Option within the opened dropdown list
    LISTBOX_OPTION = Element(
        type=ElementType.LISTBOX_OPTION,
        # Targets an individual option in the opened dropdown menu
        xpath=".//div[@role='option']"
    )

    # Question container (best anchor for a question block)
    QUESTION = Element(
        type=ElementType.QUESTION,
        # Targets the list item element that wraps a single question
        xpath=".//div[@role='listitem' and .//div[@role='heading']/following-sibling::div[1]]"
    )

    # Question title (heading)
    QUESTION_HEADING = Element(
        type=ElementType.QUESTION_HEADING,
        # Targets the element designated as a heading for the question
        xpath=".//div[@role='heading']"
    )

    # Question description (sibling immediately following the heading)
    QUESTION_DESCRIPTION = Element(
        type=ElementType.QUESTION_DESCRIPTION,
        # Targets the first sibling div element after the question heading
        xpath=".//div[@role='heading']/following-sibling::div[1]"
    )

    # --- Navigation Buttons ---

    # Next button when 'Previous' is also present (Section 2 to N-1)
    # The 'Next' button is the SECOND non-Submit button in the action bar.
    NEXT_BUTTON = Element(
        type=ElementType.NEXT_BUTTON,
        xpath="(//div[@role='list']/following-sibling::div[1]//div[@role='button' and not(@aria-label='Submit')])[2]"
    )

    # Next button for the first section (Section 1)
    # The 'Next' button is the ONLY non-Submit button present.
    NEXT_BUTTON_ON_FIRST_SECTION = Element(
        type=ElementType.NEXT_BUTTON_ON_FIRST_SECTION,
        xpath="(//div[@role='list']/following-sibling::div[1]//div[@role='button' and not(@aria-label='Submit')])[1]"
    )

    # Note: In the last section, NEXT_BUTTON also represents the submission button
    # Which allows for an iterative approach during form filling:
    #   While NEXT_BUTTON is present; fill the current section

    # Previous button (Back) - Added for completeness
    PREVIOUS_BUTTON = Element(
        type=ElementType.BUTTON,
        # If present, it is always the FIRST non-Submit button in the action bar.
        xpath="(//div[@role='list']/following-sibling::div[1]//div[@role='button' and not(@aria-label='Submit')])[1]"
    )

    TIME = Element(
        type=ElementType.TIME,
        xpath=".//div[.//input[@type='number' and @max='23'] and .//input[@type='number' and @max='59']]"
    )

    TIME_HOUR = Element(
        type=ElementType.TIME_HOUR,
        xpath=".//input[@type='number' and @max='23']"
    )

    TIME_MINUTE = Element(
        type=ElementType.TIME_MINUTE,
        xpath=".//input[@type='number' and @max='59']"
    )