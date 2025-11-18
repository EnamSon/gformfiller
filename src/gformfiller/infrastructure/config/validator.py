# infrastructure/config/validator.py

"""Configuration validation utilities"""

import os
from typing import List, Tuple, Optional
from pathlib import Path
import tomli

from .models import ConstantsConfig
from .defaults import API_KEY_ENV_VARS, SUPPORTED_AI_PROVIDERS
from .paths import ConfigPaths
from .exceptions import (
    ConfigNotFoundError,
    ConfigParseError,
    ConfigValidationError,
    APIKeyMissingError,
)


class ConfigValidator:
    """Validate configuration"""
    
    @staticmethod
    def validate_config_file() -> Tuple[bool, List[str]]:
        """
        Validate constants.toml file
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check if file exists
        if not ConfigPaths.CONSTANTS_FILE.exists():
            errors.append(f"Configuration file not found: {ConfigPaths.CONSTANTS_FILE}")
            return False, errors
        
        # Try to load and validate
        try:
            with open(ConfigPaths.CONSTANTS_FILE, "rb") as f:
                config_dict = tomli.load(f)
            
            # Check if file is empty or has no meaningful content
            if not config_dict or len(config_dict) == 0:
                errors.append("Configuration file is empty")
                return False, errors
            
            # Validate with Pydantic
            ConstantsConfig(**config_dict)
            
        except tomli.TOMLDecodeError as e:
            errors.append(f"TOML parsing error: {str(e)}")
            return False, errors
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            return False, errors
        
        return True, []
    
    @staticmethod
    def validate_config_file_strict() -> ConstantsConfig:
        """
        Validate constants.toml file (strict version that raises exceptions)
        
        Returns:
            ConstantsConfig instance
            
        Raises:
            ConfigNotFoundError: If config file doesn't exist
            ConfigParseError: If config file has invalid TOML
            ConfigValidationError: If config values are invalid
        """
        # Check if file exists
        if not ConfigPaths.CONSTANTS_FILE.exists():
            raise ConfigNotFoundError(str(ConfigPaths.CONSTANTS_FILE))
        
        # Try to load
        try:
            with open(ConfigPaths.CONSTANTS_FILE, "rb") as f:
                config_dict = tomli.load(f)
        except tomli.TOMLDecodeError as e:
            raise ConfigParseError(str(ConfigPaths.CONSTANTS_FILE), str(e))
        
        # Check if empty
        if not config_dict or len(config_dict) == 0:
            raise ConfigParseError(
                str(ConfigPaths.CONSTANTS_FILE),
                "Configuration file is empty"
            )
        
        # Validate with Pydantic
        try:
            return ConstantsConfig(**config_dict)
        except Exception as e:
            raise ConfigValidationError(
                f"Configuration validation failed: {str(e)}",
                errors=[str(e)]
            )
    
    @staticmethod
    def check_api_keys(provider: Optional[str] = None) -> Tuple[bool, List[str]]:
        """
        Check if required API keys are present and non-empty
        
        Args:
            provider: Specific provider to check, or None to check all
            
        Returns:
            Tuple of (all_present, list_of_missing_keys)
        """
        missing = []
        
        providers_to_check = [provider] if provider else SUPPORTED_AI_PROVIDERS
        
        for prov in providers_to_check:
            env_var = API_KEY_ENV_VARS.get(prov)
            if env_var:
                key_value = os.getenv(env_var)
                # Check if key is missing OR empty
                if not key_value or key_value.strip() == "":
                    missing.append(f"{env_var} (for {prov})")
        
        return len(missing) == 0, missing
    
    @staticmethod
    def check_api_key_strict(provider: str) -> str:
        """
        Check if API key for provider is present (strict version)
        
        Args:
            provider: Provider name
            
        Returns:
            API key value
            
        Raises:
            APIKeyMissingError: If API key is not set or empty
        """
        env_var = API_KEY_ENV_VARS.get(provider)
        if not env_var:
            raise ValueError(f"Unknown provider: {provider}")
        
        key_value = os.getenv(env_var)
        if not key_value or key_value.strip() == "":
            raise APIKeyMissingError(provider, env_var)
        
        return key_value
    
    @staticmethod
    def validate_paths() -> Tuple[bool, List[str]]:
        """
        Validate that all required paths exist
        
        Returns:
            Tuple of (all_exist, list_of_missing_paths)
        """
        missing = []
        
        required_paths = [
            ConfigPaths.BASE_DIR,
            ConfigPaths.CONFIG_DIR,
            ConfigPaths.LOGS_DIR,
        ]
        
        for path in required_paths:
            if not path.exists():
                missing.append(str(path))
        
        return len(missing) == 0, missing