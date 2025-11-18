"""Configuration initialization"""

from pathlib import Path
import tomli_w
from datetime import datetime
from .paths import ConfigPaths
from .defaults import DEFAULT_CONFIG, DEFAULT_PROMPT
from .models import ConstantsConfig

class ConfigInitializer:
    """Initialize configuration structure"""
    
    CURRENT_VERSION = "1.0.0"
    
    @classmethod
    def initialize(cls, force: bool = False) -> bool:
        """
        Initialize configuration structure
        
        Args:
            force: If True, overwrite existing files
            
        Returns:
            True if initialization successful, False if already exists and not forced
        """
        if ConfigPaths.exists() and not force:
            return False
        
        # Create directory structure
        ConfigPaths.ensure_structure_exists()
        
        # Write version file
        ConfigPaths.set_version(cls.CURRENT_VERSION)
        
        # Write constants.toml
        cls._write_constants_file(force)
        
        # Write logging.toml
        cls._write_logging_file(force)
        
        # Write default prompt
        cls._write_default_prompt(force)
        
        return True
    
    @classmethod
    def _write_constants_file(cls, force: bool) -> None:
        """Write constants.toml file"""
        if ConfigPaths.CONSTANTS_FILE.exists() and not force:
            return
        
        # Convert Pydantic model to dict
        config_dict = DEFAULT_CONFIG.model_dump()
        
        # Update meta timestamps
        config_dict["meta"]["created_at"] = datetime.now().isoformat()
        config_dict["meta"]["last_modified"] = datetime.now().isoformat()
        
        # Write TOML file
        with open(ConfigPaths.CONSTANTS_FILE, "wb") as f:
            tomli_w.dump(config_dict, f)
    
    @classmethod
    def _write_logging_file(cls, force: bool) -> None:
        """Write logging.toml file"""
        if ConfigPaths.LOGGING_FILE.exists() and not force:
            return
        
        logging_config = {
            "console": {
                "enabled": True,
                "level": "INFO",
                "format": "simple",
                "colored": True,
            },
            "file": {
                "enabled": True,
                "level": "DEBUG",
                "format": "structured",
                "path": "logs/gformfiller.log",
            },
            "rotation": {
                "max_bytes": 10485760,
                "backup_count": 5,
                "when": "midnight",
            },
            "formatters": {
                "simple": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
                "structured": {
                    "include_timestamp": True,
                    "include_level": True,
                    "include_logger_name": True,
                    "include_function_name": True,
                    "include_line_number": True,
                },
            },
            "filters": {
                "mask_patterns": [
                    "api_key",
                    "password",
                    "token",
                    "secret",
                    "authorization",
                ],
            },
            "loggers": {
                "selenium": {
                    "level": "WARNING",
                    "propagate": False,
                },
                "urllib3": {
                    "level": "WARNING",
                    "propagate": False,
                },
            },
        }
        
        with open(ConfigPaths.LOGGING_FILE, "wb") as f:
            tomli_w.dump(logging_config, f)
    
    @classmethod
    def _write_default_prompt(cls, force: bool) -> None:
        """Write default prompt file"""
        if ConfigPaths.DEFAULT_PROMPT_FILE.exists() and not force:
            return
        
        ConfigPaths.DEFAULT_PROMPT_FILE.write_text(DEFAULT_PROMPT)