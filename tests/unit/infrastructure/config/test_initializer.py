"""Tests for ConfigInitializer"""

import pytest
from pathlib import Path
import tomli

from gformfiller.infrastructure.config import ConfigInitializer, ConfigPaths
from gformfiller.infrastructure.config.defaults import DEFAULT_PROMPT


class TestConfigInitializer:
    """Tests for ConfigInitializer"""
    
    def test_initialize_creates_structure(self, temp_config_dir):
        """Test initialize creates complete directory structure"""
        assert not ConfigPaths.BASE_DIR.exists()
        
        success = ConfigInitializer.initialize()
        
        assert success
        assert ConfigPaths.BASE_DIR.exists()
        assert ConfigPaths.CONFIG_DIR.exists()
        assert ConfigPaths.PARSERS_DIR.exists()
        assert ConfigPaths.RESPONSES_DIR.exists()
        assert ConfigPaths.PROMPTS_DIR.exists()
        assert ConfigPaths.LOGS_DIR.exists()
        assert ConfigPaths.CACHE_DIR.exists()
    
    def test_initialize_creates_version_file(self, temp_config_dir):
        """Test initialize creates version file"""
        ConfigInitializer.initialize()
        
        assert ConfigPaths.VERSION_FILE.exists()
        version = ConfigPaths.get_version()
        assert version == ConfigInitializer.CURRENT_VERSION
    
    def test_initialize_creates_constants_file(self, temp_config_dir):
        """Test initialize creates constants.toml"""
        ConfigInitializer.initialize()
        
        assert ConfigPaths.CONSTANTS_FILE.exists()
        
        # Verify it's valid TOML
        with open(ConfigPaths.CONSTANTS_FILE, "rb") as f:
            config = tomli.load(f)
        
        assert "meta" in config
        assert "timeouts" in config
        assert "ai" in config
    
    def test_initialize_creates_logging_file(self, temp_config_dir):
        """Test initialize creates logging.toml"""
        ConfigInitializer.initialize()
        
        assert ConfigPaths.LOGGING_FILE.exists()
        
        # Verify it's valid TOML
        with open(ConfigPaths.LOGGING_FILE, "rb") as f:
            logging_config = tomli.load(f)
        
        assert "console" in logging_config
        assert "file" in logging_config
        assert "formatters" in logging_config
    
    def test_initialize_creates_default_prompt(self, temp_config_dir):
        """Test initialize creates default prompt file"""
        ConfigInitializer.initialize()
        
        assert ConfigPaths.DEFAULT_PROMPT_FILE.exists()
        
        content = ConfigPaths.DEFAULT_PROMPT_FILE.read_text()
        assert content == DEFAULT_PROMPT
    
    def test_initialize_creates_gitkeep_files(self, temp_config_dir):
        """Test initialize creates .gitkeep files"""
        ConfigInitializer.initialize()
        
        gitkeep_dirs = [
            ConfigPaths.BASE_DIR,
            ConfigPaths.CONFIG_DIR,
            ConfigPaths.PARSERS_DIR,
            ConfigPaths.RESPONSES_DIR,
            ConfigPaths.PROMPTS_DIR,
            ConfigPaths.LOGS_DIR,
            ConfigPaths.CACHE_DIR,
        ]
        
        for directory in gitkeep_dirs:
            gitkeep = directory / ".gitkeep"
            assert gitkeep.exists(), f"Missing .gitkeep in {directory}"
    
    def test_initialize_returns_false_if_exists(self, temp_config_dir):
        """Test initialize returns False if already initialized"""
        # First initialization
        success = ConfigInitializer.initialize()
        assert success
        
        # Second initialization without force
        success = ConfigInitializer.initialize(force=False)
        assert not success
    
    def test_initialize_with_force_overwrites(self, temp_config_dir):
        """Test initialize with force=True overwrites existing files"""
        # Initial setup
        ConfigInitializer.initialize()
        
        # Modify constants file
        ConfigPaths.CONSTANTS_FILE.write_text("modified content")
        
        # Reinitialize with force
        success = ConfigInitializer.initialize(force=True)
        assert success
        
        # Verify file was overwritten
        with open(ConfigPaths.CONSTANTS_FILE, "rb") as f:
            config = tomli.load(f)
        
        assert "timeouts" in config  # Should be valid TOML again
    
    def test_constants_file_has_valid_structure(self, temp_config_dir):
        """Test generated constants.toml has valid structure"""
        ConfigInitializer.initialize()
        
        with open(ConfigPaths.CONSTANTS_FILE, "rb") as f:
            config = tomli.load(f)
        
        # Check all required sections
        required_sections = [
            "meta", "timeouts", "retry", "browser", "ai",
            "dsl", "logging", "performance", "validation", "security"
        ]
        
        for section in required_sections:
            assert section in config, f"Missing section: {section}"
    
    def test_constants_file_has_timestamps(self, temp_config_dir):
        """Test generated constants.toml has timestamps"""
        ConfigInitializer.initialize()
        
        with open(ConfigPaths.CONSTANTS_FILE, "rb") as f:
            config = tomli.load(f)
        
        assert "meta" in config
        assert "created_at" in config["meta"]
        assert "last_modified" in config["meta"]
        
        # Timestamps should be ISO format strings
        assert isinstance(config["meta"]["created_at"], str)
        assert isinstance(config["meta"]["last_modified"], str)
    
    def test_logging_file_has_valid_structure(self, temp_config_dir):
        """Test generated logging.toml has valid structure"""
        ConfigInitializer.initialize()
        
        with open(ConfigPaths.LOGGING_FILE, "rb") as f:
            logging_config = tomli.load(f)
        
        # Check required sections
        assert "console" in logging_config
        assert "file" in logging_config
        assert "rotation" in logging_config
        assert "formatters" in logging_config
        assert "filters" in logging_config
        assert "loggers" in logging_config
    
    def test_initialize_idempotent_with_force(self, temp_config_dir):
        """Test multiple force initializations work correctly"""
        ConfigInitializer.initialize(force=True)
        ConfigInitializer.initialize(force=True)
        ConfigInitializer.initialize(force=True)
        
        # Should still have valid structure
        assert ConfigPaths.CONSTANTS_FILE.exists()
        assert ConfigPaths.LOGGING_FILE.exists()
        assert ConfigPaths.VERSION_FILE.exists()


class TestConfigInitializerWriteMethods:
    """Tests for internal write methods"""
    
    def test_write_constants_file(self, temp_config_dir):
        """Test _write_constants_file creates valid file"""
        ConfigPaths.ensure_structure_exists()
        
        ConfigInitializer._write_constants_file(force=True)
        
        assert ConfigPaths.CONSTANTS_FILE.exists()
        
        with open(ConfigPaths.CONSTANTS_FILE, "rb") as f:
            config = tomli.load(f)
        
        assert "timeouts" in config
        assert config["timeouts"]["page_load"] == 30
    
    def test_write_constants_file_no_overwrite(self, temp_config_dir):
        """Test _write_constants_file doesn't overwrite without force"""
        ConfigPaths.ensure_structure_exists()
        
        # Create file with custom content
        ConfigPaths.CONSTANTS_FILE.write_text("custom")
        
        # Try to write without force
        ConfigInitializer._write_constants_file(force=False)
        
        # Should not be overwritten
        content = ConfigPaths.CONSTANTS_FILE.read_text()
        assert content == "custom"
    
    def test_write_logging_file(self, temp_config_dir):
        """Test _write_logging_file creates valid file"""
        ConfigPaths.ensure_structure_exists()
        
        ConfigInitializer._write_logging_file(force=True)
        
        assert ConfigPaths.LOGGING_FILE.exists()
        
        with open(ConfigPaths.LOGGING_FILE, "rb") as f:
            logging_config = tomli.load(f)
        
        assert "console" in logging_config
        assert logging_config["console"]["enabled"] is True
    
    def test_write_default_prompt(self, temp_config_dir):
        """Test _write_default_prompt creates valid file"""
        ConfigPaths.ensure_structure_exists()
        
        ConfigInitializer._write_default_prompt(force=True)
        
        assert ConfigPaths.DEFAULT_PROMPT_FILE.exists()
        
        content = ConfigPaths.DEFAULT_PROMPT_FILE.read_text()
        assert len(content) > 0
        assert content == DEFAULT_PROMPT