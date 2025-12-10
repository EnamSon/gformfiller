# tests/unit/infrastructure/driver/test_chromedriver.py

import pytest
from unittest.mock import MagicMock, patch, call
from pathlib import Path

# Import exceptions and functions from the module under test
from gformfiller.infrastructure.driver.chromedriver import (
    get_chromedriver,
    _get_chromeoptions,
    _get_chromeservice,
    quit_chromedriver,
)
from gformfiller.infrastructure.driver.exceptions import (
    DriverNotFoundError,
    BrowserNotFoundError,
    DriverCreationError,
)
from gformfiller.infrastructure.driver.constants import (
    DEFAULT_PAGE_LOAD_STRATEGY,
    DEFAULT_REMOTE_HOST,
    DEFAULT_REMOTE_PORT,
    DEFAULT_USER_AGENTS,
)


# --- Fixtures for Mocks ---

@pytest.fixture
def mock_path_exists():
    """Mock Path.exists() to simulate file existence checks."""
    with patch("gformfiller.infrastructure.driver.chromedriver.Path.exists") as mock_exists:
        yield mock_exists

@pytest.fixture
def mock_webdriver_chrome():
    """Mock selenium.webdriver.Chrome to simulate driver creation."""
    with patch("gformfiller.infrastructure.driver.chromedriver.webdriver.Chrome") as mock_chrome:
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        yield mock_chrome

@pytest.fixture
def mock_configure_timeouts():
    """Mock configure_timeouts to isolate timeout setup."""
    with patch("gformfiller.infrastructure.driver.chromedriver.configure_timeouts") as mock_timeouts:
        yield mock_timeouts

@pytest.fixture
def mock_chromeservice():
    """Mock ChromeService."""
    with patch("gformfiller.infrastructure.driver.chromedriver.ChromeService") as mock_service:
        yield mock_service

@pytest.fixture
def mock_chromeoptions():
    """Mock ChromeOptions."""
    with patch("gformfiller.infrastructure.driver.chromedriver.ChromeOptions") as mock_options_class:
        mock_options_instance = MagicMock()
        mock_options_class.return_value = mock_options_instance
        yield mock_options_instance


# --- Tests for _get_chromeservice ---

def test_get_chromeservice_success(mock_path_exists, mock_chromeservice):
    """Test _get_chromeservice when a valid driver path is provided."""
    mock_path_exists.return_value = True
    driver_path = "/path/to/chromedriver"
    
    service = _get_chromeservice(driver_path)
    
    mock_path_exists.assert_called_once_with()
    mock_chromeservice.assert_called_once_with(executable_path=driver_path)

def test_get_chromeservice_driver_not_found(mock_path_exists):
    """Test _get_chromeservice raises DriverNotFoundError if path does not exist."""
    mock_path_exists.return_value = False
    driver_path = "/path/to/missing/chromedriver"
    
    with pytest.raises(DriverNotFoundError):
        _get_chromeservice(driver_path)
    
    mock_path_exists.assert_called_once_with()


# --- Tests for _get_chromeoptions ---

def test_get_chromeoptions_remote_mode(mock_chromeoptions):
    """Test _get_chromeoptions configuration in remote mode."""
    options = _get_chromeoptions(
        binary_location=None, user_data_dir=None, remote=True,
        remote_host="192.168.1.1", remote_port=4444, headless=False,
        user_agent=None, disable_images=False, no_sandbox=False,
        disable_gpu=False, disable_dev_shm=False,
        page_load_strategy=DEFAULT_PAGE_LOAD_STRATEGY
    )
    
    assert options.debugger_address == "192.168.1.1:4444"
    # Ensure no other options are set (fix for MagicMock truthiness issue)
    options.add_argument.assert_not_called()

def test_get_chromeoptions_binary_location_not_found(mock_chromeoptions, mock_path_exists):
    """Test _get_chromeoptions raises BrowserNotFoundError if binary is missing."""
    mock_path_exists.return_value = False
    binary_path = "/path/to/missing/chrome"

    with pytest.raises(BrowserNotFoundError):
        _get_chromeoptions(
            binary_location=binary_path, user_data_dir=None, remote=False,
            remote_host=DEFAULT_REMOTE_HOST, remote_port=DEFAULT_REMOTE_PORT,
            headless=False, user_agent=None, disable_images=False,
            no_sandbox=False, disable_gpu=False, disable_dev_shm=False,
            page_load_strategy=DEFAULT_PAGE_LOAD_STRATEGY
        )
    
    mock_path_exists.assert_called_once_with()

def test_get_chromeoptions_standard_config(mock_chromeoptions, mock_path_exists):
    """Test _get_chromeoptions applies common configurations (headless, user-data, images, etc.)."""
    mock_path_exists.return_value = True 
    binary_path = "/path/to/chrome"
    user_data_dir = "/path/to/profile"
    custom_user_agent = "Custom/Agent"
    
    options = _get_chromeoptions(
        binary_location=binary_path,
        user_data_dir=user_data_dir,
        remote=False,
        remote_host=DEFAULT_REMOTE_HOST,
        remote_port=DEFAULT_REMOTE_PORT,
        headless=True,
        user_agent=custom_user_agent,
        disable_images=True,
        no_sandbox=True,
        disable_gpu=True,
        disable_dev_shm=False,
        page_load_strategy="eager"
    )

    assert options.binary_location == binary_path
    assert options.page_load_strategy == "eager"
    mock_path_exists.assert_called_once()
    
    # Check added arguments
    expected_calls = [
        call(f"user-data-dir={user_data_dir}"),
        call("--headless=new"),
        call(f"user-agent={custom_user_agent}"),
        call("--no-sandbox"),
        call("--disable-gpu"),
        call("--disable-blink-features=AutomationControlled"),
        call("--disable-extensions"),
        call("--disable-popup-blocking"),
        call("--disable-notifications"),
    ]
    options.add_argument.assert_has_calls(expected_calls, any_order=True)

    # Check experimental options
    options.add_experimental_option.assert_has_calls([
        call("prefs", {"profile.managed_default_content_settings.images": 2}),
        call("excludeSwitches", ["enable-automation"]),
        call("useAutomationExtension", False),
    ], any_order=True)


def test_get_chromeoptions_headless_default_user_agent(mock_chromeoptions, mock_path_exists):
    """Test that the default user agent is used when headless and no user_agent is specified."""
    mock_path_exists.return_value = True
    
    options = _get_chromeoptions(
        binary_location=None, user_data_dir=None, remote=False,
        remote_host=DEFAULT_REMOTE_HOST, remote_port=DEFAULT_REMOTE_PORT,
        headless=True,
        user_agent=None,
        disable_images=False, no_sandbox=False, disable_gpu=False,
        disable_dev_shm=False, page_load_strategy=DEFAULT_PAGE_LOAD_STRATEGY
    )
    
    options.add_argument.assert_any_call(f"user-agent={DEFAULT_USER_AGENTS['chrome']}")


def test_get_chromeoptions_docker_config(mock_chromeoptions):
    """Test that Docker/CI specific options are correctly added (no-sandbox, disable-gpu, disable-dev-shm-usage)."""
    
    _get_chromeoptions(
        binary_location=None, user_data_dir=None, remote=False,
        remote_host=DEFAULT_REMOTE_HOST, remote_port=DEFAULT_REMOTE_PORT,
        headless=False, user_agent=None, disable_images=False,
        no_sandbox=True,
        disable_gpu=True,
        disable_dev_shm=True,
        page_load_strategy=DEFAULT_PAGE_LOAD_STRATEGY
    )

    options_instance = mock_chromeoptions
    options_instance.add_argument.assert_any_call("--no-sandbox")
    options_instance.add_argument.assert_any_call("--disable-gpu")
    options_instance.add_argument.assert_any_call("--disable-dev-shm-usage")


# --- Tests for get_chromedriver ---

# Mock internal dependencies to isolate get_chromedriver
@patch("gformfiller.infrastructure.driver.chromedriver._get_chromeoptions")
@patch("gformfiller.infrastructure.driver.chromedriver._get_chromeservice")
def test_get_chromedriver_success(
    mock_get_service, mock_get_options, mock_webdriver_chrome, mock_configure_timeouts
):
    """Test successful creation and configuration of the Chromedriver instance."""
    
    mock_options = MagicMock()
    mock_service = MagicMock()
    mock_get_options.return_value = mock_options
    mock_get_service.return_value = mock_service

    driver_path = "/path/to/driver"
    page_load_timeout = 60
    script_timeout = 15
    implicit_wait = 5
    
    driver = get_chromedriver(
        driver_path=driver_path,
        page_load_timeout=page_load_timeout,
        script_timeout=script_timeout,
        implicit_wait=implicit_wait
    )

    mock_get_options.assert_called_once()
    mock_get_service.assert_called_once_with(driver_path)
    mock_webdriver_chrome.assert_called_once_with(options=mock_options, service=mock_service)
    
    # Verify timeouts are configured
    mock_configure_timeouts.assert_called_once_with(
        driver, page_load_timeout, script_timeout, implicit_wait
    )


@patch("gformfiller.infrastructure.driver.chromedriver._get_chromeoptions")
@patch("gformfiller.infrastructure.driver.chromedriver._get_chromeservice")
def test_get_chromedriver_driver_not_found_re_raised(mock_get_service, mock_get_options):
    """Test that DriverNotFoundError from service creation is propagated."""
    mock_get_service.side_effect = DriverNotFoundError("chrome", "/bad/path")
    
    with pytest.raises(DriverNotFoundError):
        get_chromedriver(driver_path="/bad/path")

@patch("gformfiller.infrastructure.driver.chromedriver._get_chromeoptions")
@patch("gformfiller.infrastructure.driver.chromedriver._get_chromeservice")
def test_get_chromedriver_browser_not_found_re_raised(mock_get_service, mock_get_options):
    """Test that BrowserNotFoundError from options creation is propagated."""
    mock_get_options.side_effect = BrowserNotFoundError("chrome", "/bad/binary")
    
    with pytest.raises(BrowserNotFoundError):
        get_chromedriver(driver_path="/path/to/driver", binary_location="/bad/binary")

@patch("gformfiller.infrastructure.driver.chromedriver._get_chromeoptions")
@patch("gformfiller.infrastructure.driver.chromedriver._get_chromeservice")
def test_get_chromedriver_creation_failure_caught(mock_get_service, mock_get_options, mock_webdriver_chrome):
    """Test that any other Exception during WebDriver instantiation is caught and wrapped in DriverCreationError."""
    
    mock_get_options.return_value = MagicMock()
    mock_get_service.return_value = MagicMock()
    
    # Simulate an error during WebDriver instantiation
    test_exception = Exception("Connection failed")
    mock_webdriver_chrome.side_effect = test_exception
    
    with pytest.raises(DriverCreationError):
        get_chromedriver(driver_path="/path/to/driver")


# --- Tests for quit_chromedriver ---

@patch("gformfiller.infrastructure.driver.chromedriver.quit_webdriver")
def test_quit_chromedriver_calls_generic(mock_quit_webdriver):
    """Test that quit_chromedriver calls the generic quit_webdriver function."""
    mock_driver = MagicMock()
    quit_chromedriver(mock_driver)
    
    mock_quit_webdriver.assert_called_once_with(mock_driver)

@patch("gformfiller.infrastructure.driver.chromedriver.quit_webdriver")
def test_quit_chromedriver_with_none(mock_quit_webdriver):
    """Test that quit_chromedriver handles None input."""
    quit_chromedriver(None)
    
    mock_quit_webdriver.assert_called_once_with(None)