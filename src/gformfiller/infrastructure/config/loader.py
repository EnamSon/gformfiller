# infrastructure/config/loader.py

"""Configuration loader with priority system"""

import os
import tomli
from pathlib import Path
from typing import Optional, Dict, Any
import logging
from pydantic import ValidationError

from .models import ConstantsConfig
from .defaults import DEFAULT_CONFIG, ENV_PREFIX
from .paths import ConfigPaths
from .initializer import ConfigInitializer

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Load and merge configuration from multiple sources"""
    
    # Map of environment variable section prefixes to config sections
    ENV_SECTION_MAP = {
        "TIMEOUTS": "timeouts",
        "RETRY": "retry",
        "BROWSER": "browser",
        "AI": "ai",
        "DSL": "dsl",
        "LOGGING": "logging",
        "PERFORMANCE": "performance",
        "VALIDATION": "validation",
        "SECURITY": "security",
        "META": "meta",
    }
    
    @classmethod
    def load(cls, cli_overrides: Optional[Dict[str, Any]] = None) -> ConstantsConfig:
        """
        Load configuration with priority: CLI > ENV > File > Default
        
        Args:
            cli_overrides: Dictionary of CLI argument overrides
            
        Returns:
            Merged ConstantsConfig instance
        """
        # Ensure config exists
        if not ConfigPaths.exists():
            logger.info("Configuration not found, initializing...")
            ConfigInitializer.initialize()
        
        # Start with defaults
        config_dict = DEFAULT_CONFIG.model_dump()
        
        # Load from file
        file_config = cls._load_from_file()
        if file_config:
            config_dict = cls._deep_merge(config_dict, file_config)
        
        # Load from environment variables
        env_config = cls._load_from_env()
        if env_config:
            config_dict = cls._deep_merge(config_dict, env_config)
        
        # Apply CLI overrides
        if cli_overrides:
            config_dict = cls._deep_merge(config_dict, cli_overrides)
        
        # Validate and create config instance
        try:
            config = ConstantsConfig(**config_dict)
            cls._log_loaded_config(config)
            return config
        except ValidationError as e:
            logger.error(f"Configuration validation failed: {e}")
            logger.warning("Falling back to default configuration")
            return DEFAULT_CONFIG
    
    @classmethod
    def _load_from_file(cls) -> Optional[Dict[str, Any]]:
        """Load configuration from constants.toml"""
        try:
            with open(ConfigPaths.CONSTANTS_FILE, "rb") as f:
                return tomli.load(f)
        except FileNotFoundError:
            logger.warning(f"Configuration file not found: {ConfigPaths.CONSTANTS_FILE}")
            return None
        except Exception as e:
            logger.error(f"Error loading configuration file: {e}")
            return None
    
    @classmethod
    def _load_from_env(cls) -> Dict[str, Any]:
        """
        Load configuration from environment variables
        
        Convention: GFORMFILLER_SECTION_FIELD_NAME=value
        Where SECTION is one of: TIMEOUTS, RETRY, BROWSER, AI, etc.
        
        Examples:
            GFORMFILLER_TIMEOUTS_PAGE_LOAD=30 -> timeouts.page_load
            GFORMFILLER_AI_DEFAULT_PROVIDER=claude -> ai.default_provider
            GFORMFILLER_BROWSER_WINDOW_WIDTH=1280 -> browser.window_width
        """
        env_config: Dict[str, Any] = {}
        
        for key, value in os.environ.items():
            if not key.startswith(ENV_PREFIX):
                continue
            
            # Remove prefix: GFORMFILLER_TIMEOUTS_PAGE_LOAD -> TIMEOUTS_PAGE_LOAD
            config_key = key[len(ENV_PREFIX):]
            
            # Find matching section
            section = None
            field_name = None
            
            for section_prefix, section_name in cls.ENV_SECTION_MAP.items():
                if config_key.startswith(section_prefix + "_"):
                    section = section_name
                    # Everything after SECTION_ is the field name (converted to lowercase)
                    field_name = config_key[len(section_prefix) + 1:].lower()
                    break
            
            if section is None:
                logger.warning(f"Unknown section in env key: {key}")
                continue
            
            # Create section if needed
            if section not in env_config:
                env_config[section] = {}
            
            # Set value with type conversion
            env_config[section][field_name] = cls._parse_env_value(value)
        
        return env_config
    
    @staticmethod
    def _parse_env_value(value: str) -> Any:
        """Parse environment variable value to appropriate type"""
        # Boolean
        if value.lower() in ("true", "1", "yes"):
            return True
        if value.lower() in ("false", "0", "no"):
            return False
        
        # Integer
        try:
            return int(value)
        except ValueError:
            pass
        
        # Float
        try:
            return float(value)
        except ValueError:
            pass
        
        # String
        return value
    
    @staticmethod
    def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ConfigLoader._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    @staticmethod
    def _log_loaded_config(config: ConstantsConfig) -> None:
        """Log loaded configuration with sources"""
        logger.info("Configuration loaded successfully")
        logger.info(f"  Config version: {config.meta.config_version}")
        logger.info(f"  Page load timeout: {config.timeouts.page_load}s")
        logger.info(f"  AI response timeout: {config.timeouts.ai_response}s")
        logger.info(f"  Default AI provider: {config.ai.default_provider}")
        logger.info(f"  Log level: {config.logging.level}")
        logger.debug(f"  Full config: {config.model_dump()}")