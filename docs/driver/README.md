# ⚙️ Driver Module (`gformfiller.infrastructure.driver`)

This module is part of the infrastructure for managing browser drivers (WebDriver) within the project. It provides robust and configurable functions for initializing, configuring, and safely managing the **ChromeDriver** using Selenium, along with handling specific exceptions related to drivers and browsers.

## Core Features

* **Driver Creation:** Centralized function (`get_chromedriver`) for instantiating a driver, handling binary paths, and applying advanced configuration options.
* **Flexible Configuration:** Supports `headless` mode, custom user profiles (`user-data-dir`), custom binary locations, and specific configurations for CI/Docker environments (`no-sandbox`, GPU disabling).
* **Timeout Management:** Dedicated function (`configure_timeouts`) for simple control over page load, script execution, and implicit wait times.
* **Error Handling:** Custom exceptions (`DriverNotFoundError`, `BrowserNotFoundError`, `DriverCreationError`) to clearly identify and diagnose creation failures.
* **Safe Shutdown:** The `quit_chromedriver` function ensures the driver instance is closed cleanly, even when faced with potential errors.

## Module Structure

The module is structured as follows:

| File | Description |
| :--- | :--- |
| `chromedriver.py` | Core functions (`get_chromedriver`, `quit_chromedriver`) and handling of `ChromeOptions` and `ChromeService`. |
| `generics.py` | Generic functions applicable to any WebDriver (`configure_timeouts`, `quit_webdriver`). |
| `constants.py` | Enums (`BrowserType`, `PageLoadStrategy`) and default constants (timeouts, User-Agents). |
| `exceptions.py` | Custom exception classes (`DriverNotFoundError`, `BrowserNotFoundError`, `DriverCreationError`, etc.). |
| `__init__.py` | Exposes all key functions and exceptions for simplified imports. |