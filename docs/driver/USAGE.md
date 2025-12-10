# 🚀 Driver Module Usage Guide

This guide explains how to import and use the key functions of the `driver` module to initialize and manage a Chrome driver instance.

## 1. Importing

The most important functions and exceptions are directly available from the package:

```python
from gformfiller.infrastructure.driver import (
    get_chromedriver,
    quit_chromedriver,
    DriverNotFoundError,
    BrowserNotFoundError,
)
```

## 2. Driver Creation

Use the get_chromedriver function to create and configure a WebDriver instance.

### Basic Example

To create a driver in headless mode with standard timeouts:

```python
DRIVER_PATH = "/usr/local/bin/chromedriver" # Replace with your actual path

# Initialize driver variable for use in 'finally' block
driver = None

try:
    # Create and configure the driver
    driver = get_chromedriver(
        driver_path=DRIVER_PATH,
        headless=True,
        page_load_timeout=30,
        implicit_wait=5
    )
    print("Chrome Driver successfully initialized in headless mode.")

    # Driver usage...
    driver.get("[https://example.com](https://example.com)")

except DriverNotFoundError as e:
    print(f"Error: The driver binary was not found. {e}")
except BrowserNotFoundError as e:
    print(f"Error: The Chrome browser binary was not found. {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    # Essential step: safe shutdown
    quit_chromedriver(driver)
```

### Key Configuration Options

The get_chromedriver function accepts several arguments for precise control:

| Argument | Type | Description |
| :--- | :--- | :--- |
| `driver_path` | `str` | Path to the chromedriver binary |
| `binary_location` | `str` | `None` |
| `headless` | `bool` | Run the browser without a GUI (default: `False`) |
| `user_data_dir` | `str` | `None` |
| `disable_images` | `bool` | Disables image loading for performance (default: `False`) |
| `no_sandbox` | `bool` | Enables the `--no-sandbox` option (useful in Docker/CI environments) |
| `page_load_strategy` | `str` | Page loading strategy (`"normal"`, `"eager"`, `"none"`) |
| `page_load_timeout` | `int` | Maximum time to wait for a page to load (in seconds) |
| `implicit_wait` | `int` | Implicit wait time for searching elements (in seconds) |

## 3. Shutting Down the Driver

It is crucial to call quit_chromedriver() to release system resources and terminate the browser process:

```python
quit_chromedriver(driver)
```

The function safely handles cases where the driver object is None or if an error occurs during the shutdown process.

## 4. Error Handling

Custom exceptions help in quickly diagnosing driver creation failures:

| Exception | Trigger |
| :--- | :--- |
| `DriverNotFoundError` | The chromedriver file specified by driver_path does not exist. |
| `BrowserNotFoundError` | The Chrome browser binary specified by binary_location does not exist. |
| `DriverCreationError`	| Failure during webdriver.Chrome instantiation for any other reason (e.g., version incompatibility). |