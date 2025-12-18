# gformfiller/infrastructure/config_manager.py

import json
import logging
from typing import Any, Dict
import tomllib
from .folder_manager import FolderManager
from .folder_manager.constants import DEFAULT_TOML, CONFIG_FILE

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
        path = self._fm.root / DEFAULT_TOML
        if not path.exists():
            logger.warning(f"Global config {DEFAULT_TOML} not found. Using empty defaults.")
            return {}
        
        try:
            with open(path, "rb") as f:
                return tomllib.load(f).get("default", {})
        except Exception as e:
            logger.error(f"Error reading {DEFAULT_TOML}: {e}")
            return {}

    def get_filler_config(self, filler_name: str) -> Dict[str, Any]:
        """Loads the specific config.json for a given filler."""
        try:
            return self._fm.get_filler_file_content(filler_name, "config")
        except Exception:
            return {}

    def get_resolved_config(self, filler_name: str) -> FillerConfig:
        defaults = self.get_default_config()
        overrides = self.get_filler_config(filler_name)
        
        merged_data = {**defaults, **overrides}
        
        return FillerConfig.model_validate(merged_data)

    def save_filler_config(self, filler_name: str, config_data: Dict[str, Any]):
        """Persists new configuration data to the filler's config.json."""
        self._fm.update_filler_file_content(filler_name, "config", config_data)