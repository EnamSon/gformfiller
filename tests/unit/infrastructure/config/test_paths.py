"""Tests for ConfigPaths"""

import pytest
from pathlib import Path

from gformfiller.infrastructure.config.paths import ConfigPaths


class TestConfigPaths:
    """Tests for ConfigPaths"""
    
    def test_base_dir_default(self, temp_home):
        """Test default base directory is in user home"""
        # Note: This test uses actual home, so we need to reset after
        from gformfiller.infrastructure.config import ConfigPaths as OriginalPaths
        
        assert str(OriginalPaths.BASE_DIR).endswith(".gformfiller")
    
    def test_all_paths_defined(self, temp_config_dir):
        """Test all required paths are defined"""
        assert ConfigPaths.BASE_DIR == temp_config_dir
        assert ConfigPaths.CONFIG_DIR == temp_config_dir / "config"
        assert ConfigPaths.PARSERS_DIR == temp_config_dir / "parsers"
        assert ConfigPaths.RESPONSES_DIR == temp_config_dir / "responses"
        assert ConfigPaths.PROMPTS_DIR == temp_config_dir / "prompts"
        assert ConfigPaths.LOGS_DIR == temp_config_dir / "logs"
        assert ConfigPaths.CACHE_DIR == temp_config_dir / "cache"
    
    def test_file_paths_defined(self, temp_config_dir):
        """Test all file paths are defined"""
        assert ConfigPaths.CONSTANTS_FILE == temp_config_dir / "config" / "constants.toml"
        assert ConfigPaths.LOGGING_FILE == temp_config_dir / "config" / "logging.toml"
        assert ConfigPaths.VERSION_FILE == temp_config_dir / ".gformfiller_version"
        assert ConfigPaths.DEFAULT_PROMPT_FILE == temp_config_dir / "prompts" / "default.txt"
    
    def test_get_log_file_default(self, temp_config_dir):
        """Test get_log_file with default filename"""
        log_file = ConfigPaths.get_log_file()
        
        assert log_file == temp_config_dir / "logs" / "gformfiller.log"
    
    def test_get_log_file_custom(self, temp_config_dir):
        """Test get_log_file with custom filename"""
        log_file = ConfigPaths.get_log_file("custom.log")
        
        assert log_file == temp_config_dir / "logs" / "custom.log"
    
    def test_ensure_structure_exists(self, temp_config_dir):
        """Test ensure_structure_exists creates all directories"""
        # Initially doesn't exist
        assert not temp_config_dir.exists()
        
        ConfigPaths.ensure_structure_exists()
        
        # All directories created
        assert ConfigPaths.BASE_DIR.exists()
        assert ConfigPaths.CONFIG_DIR.exists()
        assert ConfigPaths.PARSERS_DIR.exists()
        assert ConfigPaths.RESPONSES_DIR.exists()
        assert ConfigPaths.PROMPTS_DIR.exists()
        assert ConfigPaths.LOGS_DIR.exists()
        assert ConfigPaths.CACHE_DIR.exists()
        
        # .gitkeep files created
        assert (ConfigPaths.BASE_DIR / ".gitkeep").exists()
        assert (ConfigPaths.CONFIG_DIR / ".gitkeep").exists()
        assert (ConfigPaths.PARSERS_DIR / ".gitkeep").exists()
    
    def test_ensure_structure_exists_idempotent(self, temp_config_dir):
        """Test ensure_structure_exists can be called multiple times"""
        ConfigPaths.ensure_structure_exists()
        ConfigPaths.ensure_structure_exists()  # Second call should not fail
        
        assert ConfigPaths.BASE_DIR.exists()
    
    def test_exists_false_when_not_initialized(self, temp_config_dir):
        """Test exists returns False when structure doesn't exist"""
        assert not ConfigPaths.exists()
    
    def test_exists_true_when_initialized(self, temp_config_dir):
        """Test exists returns True when structure exists"""
        ConfigPaths.ensure_structure_exists()
        ConfigPaths.CONSTANTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        ConfigPaths.CONSTANTS_FILE.touch()
        
        assert ConfigPaths.exists()
    
    def test_get_version_none_when_not_set(self, temp_config_dir):
        """Test get_version returns None when version file doesn't exist"""
        assert ConfigPaths.get_version() is None
    
    def test_get_version_returns_content(self, temp_config_dir):
        """Test get_version returns file content"""
        ConfigPaths.BASE_DIR.mkdir(parents=True, exist_ok=True)
        ConfigPaths.VERSION_FILE.write_text("1.0.0")
        
        assert ConfigPaths.get_version() == "1.0.0"
    
    def test_set_version(self, temp_config_dir):
        """Test set_version writes version file"""
        ConfigPaths.BASE_DIR.mkdir(parents=True, exist_ok=True)
        ConfigPaths.set_version("2.0.0")
        
        assert ConfigPaths.VERSION_FILE.exists()
        assert ConfigPaths.get_version() == "2.0.0"