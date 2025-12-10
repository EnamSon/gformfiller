# gformfiller/infrastructure/driver/exceptions.py

"""driver-specific exceptions"""


class DriverError(Exception):
    """Base exception for browser-related errors"""
    pass


class DriverCreationError(DriverError):
    """Raised when WebDriver creation fails"""
    
    def __init__(self, browser_type: str, reason: str):
        self.browser_type = browser_type
        self.reason = reason
        super().__init__(f"Failed to create {browser_type} driver: {reason}")


class DriverNotFoundError(DriverCreationError):
    """Raised when WebDriver binary is not found"""
    
    def __init__(self, browser_type: str, driver_path: str | None = None):
        self.driver_path = driver_path
        message = f"WebDriver for {browser_type} not found"
        if driver_path:
            message += f" at {driver_path}"
        super().__init__(browser_type, message)


class BrowserNotFoundError(DriverCreationError):
    """Raised when browser binary is not found."""

    def __init__(self, browser_type: str, binary_location: str | None = None):
        self.binary_path = binary_location
        message = f"{browser_type.capitalize()} not found"
        if binary_location:
            message += f" at {binary_location}"
        super().__init__(browser_type, message)


class RemoteConnectionError(DriverError):
    """Raised when remote WebDriver connection fails"""
    
    def __init__(self, host: str, port: int, reason: str | None = None):
        self.host = host
        self.port = port
        self.reason = reason
        message = f"Failed to connect to remote browser at {host}:{port}"
        if reason:
            message += f": {reason}"
        super().__init__(message)


class UnsupportedBrowserError(DriverError):
    """Raised when browser type is not supported"""
    
    def __init__(self, browser_type: str, supported_browsers: list):
        self.browser_type = browser_type
        self.supported_browsers = supported_browsers
        super().__init__(
            f"Browser '{browser_type}' is not supported. "
            f"Supported browsers: {', '.join(supported_browsers)}"
        )