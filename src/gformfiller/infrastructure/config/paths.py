"""Path management for configuration files"""

from pathlib import Path
from typing import Optional
import os

class ConfigPaths:
    """Centralized path management"""
    
    # Base directory
    BASE_DIR = Path.home() / ".gformfiller"
    
    # Subdirectories
    CONFIG_DIR = BASE_DIR / "config"
    PARSERS_DIR = BASE_DIR / "parsers"
    RESPONSES_DIR = BASE_DIR / "responses"
    PROMPTS_DIR = BASE_DIR / "prompts"
    LOGS_DIR = BASE_DIR / "logs"
    CACHE_DIR = BASE_DIR / "cache"
    
    # Configuration files
    CONSTANTS_FILE = CONFIG_DIR / "constants.toml"
    LOGGING_FILE = CONFIG_DIR / "logging.toml"
    VERSION_FILE = BASE_DIR / ".gformfiller_version"
    DEFAULT_PROMPT_FILE = PROMPTS_DIR / "default.txt"
    
    @classmethod
    def get_log_file(cls, filename: Optional[str] = None) -> Path:
        """Get log file path"""
        if filename:
            return cls.LOGS_DIR / filename
        return cls.LOGS_DIR / "gformfiller.log"
    
    @classmethod
    def ensure_structure_exists(cls) -> None:
        """Create directory structure if it doesn't exist"""
        directories = [
            cls.BASE_DIR,
            cls.CONFIG_DIR,
            cls.PARSERS_DIR,
            cls.RESPONSES_DIR,
            cls.PROMPTS_DIR,
            cls.LOGS_DIR,
            cls.CACHE_DIR,
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
            # Create .gitkeep files
            gitkeep = directory / ".gitkeep"
            if not gitkeep.exists():
                gitkeep.touch()
    
    @classmethod
    def exists(cls) -> bool:
        """Check if configuration structure exists"""
        return cls.BASE_DIR.exists() and cls.CONSTANTS_FILE.exists()
    
    @classmethod
    def get_version(cls) -> Optional[str]:
        """Read current configuration version"""
        if cls.VERSION_FILE.exists():
            return cls.VERSION_FILE.read_text().strip()
        return None
    
    @classmethod
    def set_version(cls, version: str) -> None:
        """Write configuration version"""
        cls.VERSION_FILE.write_text(version)