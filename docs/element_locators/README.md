# 🧭 Element Locators Infrastructure Module

This module, located at `gformfiller/infrastructure/element_locators`, provides a robust, strategy-based system for locating specific web elements within a Google Form structure using Selenium WebDriver.

## 🌟 Features

* **Strategy-Based Localization:** Uses a defined `LocalizationStrategy` (e.g., XPATH, CSS_LOCATOR) to find elements.
* **Predefined Form Elements:** Contains an enumeration (`GoogleFormElement`) of common Google Form UI components (like `SUBMIT_BUTTON`, `RADIO`, `TEXT_INPUT`) with stable, pre-tested selectors.
* **Contextual Search:** Allows searching for elements from either the root WebDriver or a specific parent WebElement.
* **Clear Exception Handling:** Defines custom exceptions for scenarios like invalid strategies or element not found errors.

## 📦 Contents

| File | Description |
| :--- | :--- |
| `element_locator.py` | Contains the core `ElementLocator` class for element searching. |
| `constants.py` | Defines enumerations for strategies, element types, and concrete `GoogleFormElement` instances with their selectors. |
| `exceptions.py` | Defines custom exceptions for the module. |
| `__init__.py` | Makes key classes and constants easily importable. |

## 💡 Core Components

### `ElementLocator`
The main class used to perform the element search. It is initialized with a search context (WebDriver or WebElement) and a localization strategy.

### `LocalizationStrategy` (Enum)
Defines the mechanism for locating the element (`XPATH`, `CSS_LOCATOR`).

### `GoogleFormElement` (Enum)
A collection of pre-defined `Element` objects, each holding the specific selectors for a known Google Form UI component. This acts as the source of truth for all selectors.

### Custom Exceptions
* `InvalidStrategyError`: Raised if an unsupported strategy is passed.
* `ElementNotFoundError`: Raised if `locate` fails to find the specified element.