"""Configuration-specific exceptions"""


class ConfigError(Exception):
    """Base exception for configuration errors"""
    pass


class ConfigValidationError(ConfigError):
    """Raised when configuration validation fails"""
    
    def __init__(self, message: str, errors: list | None = None):
        super().__init__(message)
        self.errors = errors or []


class ConfigNotFoundError(ConfigError):
    """Raised when configuration file is not found"""
    
    def __init__(self, path: str):
        super().__init__(f"Configuration not found: {path}")
        self.path = path


class ConfigParseError(ConfigError):
    """Raised when configuration file cannot be parsed"""
    
    def __init__(self, path: str, reason: str):
        super().__init__(f"Failed to parse {path}: {reason}")
        self.path = path
        self.reason = reason


class APIKeyMissingError(ConfigError):
    """Raised when required API key is missing"""
    
    def __init__(self, provider: str, env_var: str):
        super().__init__(
            f"API key for {provider} not found. "
            f"Please set {env_var} environment variable."
        )
        self.provider = provider
        self.env_var = env_var