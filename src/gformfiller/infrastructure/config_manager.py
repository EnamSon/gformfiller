# gformfiller/infrastructure/config_manager.py

import json
import logging
from typing import Any, Dict
import tomllib
import tomli_w
from .folder_manager import FolderManager
from .folder_manager.constants import DEFAULT_CONFIG, CONFIG_FILE
from .folder_manager.constants import FileKeys
from gformfiller.domain.schemas.config import FillerConfig

logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Manages the merging logic between global defaults and filler-specific settings.
    """

    def __init__(self, folder_manager: FolderManager):
        self._fm = folder_manager

    def get_default_config(self) -> Dict[str, Any]:
        """Loads the global configuration from .gformfiller/default.toml."""
        path = self._fm.default_config
        if not path.exists():
            logger.warning(f"Global config {DEFAULT_CONFIG} not found. Using empty defaults.")
            return {
                "profile": "default",
                "headless": False,
                "remote": False,
                "wait_time": 5.0,
                "submit": True
            }
        
        try:
            with open(path, "rb") as f:
                return tomllib.load(f).get("default", {})
        except Exception as e:
            logger.error(f"Error reading {DEFAULT_CONFIG}: {e}")
            return {}

    def update_default_config(self, data: Dict[str, Any]):
        """Update default config."""
        if not self._fm.default_config.exists():
            logger.warning(f"{DEFAULT_CONFIG} not found. Creating...")
            self._fm.default_config.touch()

        current_config = self.get_default_config()
        for key, val in data.items():
            current_config[key] = val
    
        with open(self._fm.default_config, "wb") as f:
            tomli_w.dump({"default": current_config}, f)


    def get_filler_config(self, user_id: str, filler_name: str) -> Dict[str, Any]:
        """Loads the specific config.json for a given filler."""
        try:
            return self._fm.get_filler_file_content(user_id, filler_name, FileKeys.CONFIG)
        except Exception:
            return {}

    def get_resolved_config(self, user_id: str, filler_name: str) -> FillerConfig:
        defaults = self.get_default_config()
        overrides = self.get_filler_config(user_id, filler_name)
        
        merged_data = {**defaults, **overrides}
        
        return FillerConfig.model_validate(merged_data)

    def save_filler_config(self, user_id: str, filler_name: str, config_data: Dict[str, Any]):
        """Persists new configuration data to the filler's config.json."""
        self._fm.update_filler_file_content(user_id, filler_name, FileKeys.CONFIG, config_data)