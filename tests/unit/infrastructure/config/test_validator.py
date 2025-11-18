"""Tests for ConfigValidator"""

import pytest
import os
import tomli_w
from pathlib import Path

from gformfiller.infrastructure.config import (
    ConfigValidator,
    ConfigPaths,
    ConfigInitializer,
)
from gformfiller.infrastructure.config.models import ConstantsConfig
from gformfiller.infrastructure.config.defaults import API_KEY_ENV_VARS


class TestConfigValidator:
    """Tests for ConfigValidator"""
    
    def test_validate_config_file_success(self, temp_config_dir, sample_config_dict, write_config_file):
        """Test validation of valid config file"""
        write_config_file(sample_config_dict)
        
        is_valid, errors = ConfigValidator.validate_config_file()
        
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_config_file_not_found(self, temp_config_dir):
        """Test validation when config file doesn't exist"""
        is_valid, errors = ConfigValidator.validate_config_file()
        
        assert not is_valid
        assert len(errors) > 0
        assert "not found" in errors[0].lower()
    
    def test_validate_config_file_invalid_toml(self, temp_config_dir):
        """Test validation with invalid TOML syntax"""
        ConfigPaths.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        ConfigPaths.CONSTANTS_FILE.write_text("invalid { toml syntax")
        
        is_valid, errors = ConfigValidator.validate_config_file()
        
        assert not is_valid
        assert len(errors) > 0
    
    def test_validate_config_file_invalid_values(self, temp_config_dir, write_config_file):
        """Test validation with invalid config values"""
        invalid_config = {
            "meta": {"config_version": "1.0.0"},
            "timeouts": {"page_load": -10},  # Invalid negative value
            "ai": {"temperature": 5.0},  # Invalid (max is 2.0)
        }
        
        write_config_file(invalid_config)
        
        is_valid, errors = ConfigValidator.validate_config_file()
        
        assert not is_valid
        assert len(errors) > 0
    
    def test_validate_config_file_missing_required_fields(self, temp_config_dir, write_config_file):
        """Test validation with incomplete config"""
        incomplete_config = {
            "meta": {"config_version": "1.0.0"},
            # Missing other required sections
        }
        
        write_config_file(incomplete_config)
        
        # Should still be valid because Pydantic uses defaults
        is_valid, errors = ConfigValidator.validate_config_file()
        
        assert is_valid  # Pydantic fills in defaults
    
    def test_validate_config_file_extra_fields(self, temp_config_dir, write_config_file, sample_config_dict):
        """Test validation with extra unknown fields"""
        sample_config_dict["unknown_section"] = {"field": "value"}
        
        write_config_file(sample_config_dict)
        
        is_valid, errors = ConfigValidator.validate_config_file()
        
        # Should fail because extra="forbid" in ConstantsConfig
        assert not is_valid
        assert len(errors) > 0


class TestConfigValidatorAPIKeys:
    """Tests for API key validation"""
    
    def test_check_api_keys_all_present(self, monkeypatch):
        """Test when all API keys are present"""
        for provider, env_var in API_KEY_ENV_VARS.items():
            monkeypatch.setenv(env_var, f"test_key_{provider}")
        
        all_present, missing = ConfigValidator.check_api_keys()
        
        assert all_present
        assert len(missing) == 0
    
    def test_check_api_keys_all_missing(self, clean_env):
        """Test when all API keys are missing"""
        all_present, missing = ConfigValidator.check_api_keys()
        
        assert not all_present
        assert len(missing) == len(API_KEY_ENV_VARS)
    
    def test_check_api_keys_specific_provider_present(self, monkeypatch, clean_env):
        """Test checking specific provider with key present"""
        monkeypatch.setenv("GEMINI_API_KEY", "test_key")
        
        all_present, missing = ConfigValidator.check_api_keys(provider="gemini")
        
        assert all_present
        assert len(missing) == 0
    
    def test_check_api_keys_specific_provider_missing(self, clean_env):
        """Test checking specific provider with key missing"""
        all_present, missing = ConfigValidator.check_api_keys(provider="gemini")
        
        assert not all_present
        assert len(missing) == 1
        assert "GEMINI_API_KEY" in missing[0]
    
    def test_check_api_keys_some_present(self, monkeypatch, clean_env):
        """Test when some API keys are present, others missing"""
        monkeypatch.setenv("GEMINI_API_KEY", "test_key_1")
        monkeypatch.setenv("CLAUDE_API_KEY", "test_key_2")
        # OPENAI_API_KEY, DEEPSEEK_API_KEY, COPILOT_API_KEY missing
        
        all_present, missing = ConfigValidator.check_api_keys()
        
        assert not all_present
        assert len(missing) == 3
    
    def test_check_api_keys_invalid_provider(self, clean_env):
        """Test checking invalid provider"""
        all_present, missing = ConfigValidator.check_api_keys(provider="invalid_provider")
        
        # Should handle gracefully
        assert all_present  # No keys to check for invalid provider
        assert len(missing) == 0
    
    def test_check_api_keys_empty_value(self, monkeypatch, clean_env):
        """Test API key set but empty"""
        monkeypatch.setenv("GEMINI_API_KEY", "")
        
        # Empty string is still considered "present"
        all_present, missing = ConfigValidator.check_api_keys(provider="gemini")
        
        # This depends on implementation - adjust if needed
        # Currently, os.getenv returns "" which is truthy for "if env_var"
        # but we might want to check for non-empty
        assert not all_present  # Empty string still counts as present
        assert len(missing) == 1
        assert "GEMINI_API_KEY" in missing[0]


class TestConfigValidatorPaths:
    """Tests for path validation"""
    
    def test_validate_paths_all_exist(self, temp_config_dir):
        """Test when all required paths exist"""
        ConfigInitializer.initialize()
        
        all_exist, missing = ConfigValidator.validate_paths()
        
        assert all_exist
        assert len(missing) == 0
    
    def test_validate_paths_none_exist(self, temp_config_dir):
        """Test when no paths exist"""
        all_exist, missing = ConfigValidator.validate_paths()
        
        assert not all_exist
        assert len(missing) > 0
    
    def test_validate_paths_some_exist(self, temp_config_dir):
        """Test when some paths exist"""
        # Create only BASE_DIR and CONFIG_DIR
        ConfigPaths.BASE_DIR.mkdir(parents=True, exist_ok=True)
        ConfigPaths.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        # LOGS_DIR missing
        
        all_exist, missing = ConfigValidator.validate_paths()
        
        assert not all_exist
        assert len(missing) > 0
        assert str(ConfigPaths.LOGS_DIR) in missing
    
    def test_validate_paths_returns_correct_missing(self, temp_config_dir):
        """Test that validate_paths returns correct list of missing paths"""
        # Don't create any directories
        
        all_exist, missing = ConfigValidator.validate_paths()
        
        assert not all_exist
        
        # Check that required paths are in missing list
        required_paths = [
            ConfigPaths.BASE_DIR,
            ConfigPaths.CONFIG_DIR,
            ConfigPaths.LOGS_DIR,
        ]
        
        missing_paths = [Path(p) for p in missing]
        for required_path in required_paths:
            assert required_path in missing_paths


class TestConfigValidatorIntegration:
    """Integration tests for ConfigValidator"""
    
    def test_validate_fresh_installation(self, temp_config_dir):
        """Test validation of freshly initialized config"""
        ConfigInitializer.initialize()
        
        # Config file should be valid
        is_valid, errors = ConfigValidator.validate_config_file()
        assert is_valid
        
        # Paths should exist
        all_exist, missing = ConfigValidator.validate_paths()
        assert all_exist
    
    def test_validate_modified_config(self, temp_config_dir, write_config_file, sample_config_dict):
        """Test validation after config modification"""
        ConfigInitializer.initialize()
        
        # Modify config with valid values
        sample_config_dict["timeouts"]["page_load"] = 60
        write_config_file(sample_config_dict)
        
        is_valid, errors = ConfigValidator.validate_config_file()
        assert is_valid
    
    def test_validate_corrupted_config(self, temp_config_dir):
        """Test validation of corrupted config"""
        ConfigInitializer.initialize()
        
        # Corrupt the config file
        ConfigPaths.CONSTANTS_FILE.write_text("corrupted data")
        
        is_valid, errors = ConfigValidator.validate_config_file()
        assert not is_valid
    
    def test_full_validation_workflow(self, temp_config_dir, monkeypatch, clean_env):
        """Test complete validation workflow"""
        # Initialize
        ConfigInitializer.initialize()
        
        # Set API key
        monkeypatch.setenv("GEMINI_API_KEY", "test_key")
        
        # Validate config file
        config_valid, config_errors = ConfigValidator.validate_config_file()
        assert config_valid
        
        # Validate paths
        paths_valid, path_errors = ConfigValidator.validate_paths()
        assert paths_valid
        
        # Check API keys
        keys_present, missing_keys = ConfigValidator.check_api_keys(provider="gemini")
        assert keys_present


class TestConfigValidatorEdgeCases:
    """Edge case tests for ConfigValidator"""
    
    def test_validate_config_with_unicode(self, temp_config_dir, write_config_file, sample_config_dict):
        """Test validation with unicode characters"""
        sample_config_dict["browser"]["user_agent"] = "Mozilla/5.0 (特殊字符)"
        
        write_config_file(sample_config_dict)
        
        is_valid, errors = ConfigValidator.validate_config_file()
        assert is_valid
    
    def test_validate_config_with_very_large_values(self, temp_config_dir, write_config_file, sample_config_dict):
        """Test validation with boundary values"""
        sample_config_dict["timeouts"]["page_load"] = 120  # Max value
        sample_config_dict["ai"]["max_tokens"] = 8000  # Max value
        
        write_config_file(sample_config_dict)
        
        is_valid, errors = ConfigValidator.validate_config_file()
        assert is_valid
    
    def test_validate_config_with_minimal_values(self, temp_config_dir, write_config_file, sample_config_dict):
        """Test validation with minimum boundary values"""
        sample_config_dict["timeouts"]["page_load"] = 5  # Min value
        sample_config_dict["ai"]["temperature"] = 0.0  # Min value
        
        write_config_file(sample_config_dict)
        
        is_valid, errors = ConfigValidator.validate_config_file()
        assert is_valid
    
    def test_validate_empty_config_file(self, temp_config_dir):
        """Test validation of empty config file"""
        ConfigPaths.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        ConfigPaths.CONSTANTS_FILE.write_text("")
        
        is_valid, errors = ConfigValidator.validate_config_file()
        
        # Empty file should be invalid
        assert not is_valid
    
    def test_validate_config_with_comments(self, temp_config_dir):
        """Test validation of config with TOML comments"""
        ConfigPaths.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        config_with_comments = """
# This is a comment
[meta]
config_version = "1.0.0"

# Timeout settings
[timeouts]
page_load = 30  # Page load timeout
element_wait = 10
script_execution = 5
ai_response = 60
form_submission = 15
"""
        
        ConfigPaths.CONSTANTS_FILE.write_text(config_with_comments)
        
        is_valid, errors = ConfigValidator.validate_config_file()
        # Should be valid (uses defaults for missing sections)
        assert is_valid


class TestConfigValidatorStrictMethods:
    """Tests for strict validation methods that raise exceptions"""
    
    def test_validate_config_file_strict_success(self, temp_config_dir, write_config_file, sample_config_dict):
        """Test strict validation with valid config"""
        write_config_file(sample_config_dict)
        
        config = ConfigValidator.validate_config_file_strict()
        
        assert isinstance(config, ConstantsConfig)
        assert config.timeouts.page_load == 30
    
    def test_validate_config_file_strict_not_found(self, temp_config_dir):
        """Test strict validation raises ConfigNotFoundError"""
        from gformfiller.infrastructure.config.exceptions import ConfigNotFoundError
        
        with pytest.raises(ConfigNotFoundError) as exc_info:
            ConfigValidator.validate_config_file_strict()
        
        assert str(ConfigPaths.CONSTANTS_FILE) in str(exc_info.value)
    
    def test_validate_config_file_strict_invalid_toml(self, temp_config_dir):
        """Test strict validation raises ConfigParseError for invalid TOML"""
        from gformfiller.infrastructure.config.exceptions import ConfigParseError
        
        ConfigPaths.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        ConfigPaths.CONSTANTS_FILE.write_text("invalid { toml")
        
        with pytest.raises(ConfigParseError) as exc_info:
            ConfigValidator.validate_config_file_strict()
        
        assert str(ConfigPaths.CONSTANTS_FILE) in str(exc_info.value)
    
    def test_validate_config_file_strict_empty_file(self, temp_config_dir):
        """Test strict validation raises ConfigParseError for empty file"""
        from gformfiller.infrastructure.config.exceptions import ConfigParseError
        
        ConfigPaths.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        ConfigPaths.CONSTANTS_FILE.write_text("")
        
        with pytest.raises(ConfigParseError) as exc_info:
            ConfigValidator.validate_config_file_strict()
        
        assert "empty" in str(exc_info.value).lower()
    
    def test_validate_config_file_strict_invalid_values(self, temp_config_dir, write_config_file):
        """Test strict validation raises ConfigValidationError for invalid values"""
        from gformfiller.infrastructure.config.exceptions import ConfigValidationError
        
        invalid_config = {
            "timeouts": {"page_load": -10},  # Invalid
        }
        
        write_config_file(invalid_config)
        
        with pytest.raises(ConfigValidationError):
            ConfigValidator.validate_config_file_strict()
    
    def test_check_api_key_strict_success(self, monkeypatch, clean_env):
        """Test strict API key check with valid key"""
        monkeypatch.setenv("GEMINI_API_KEY", "test_key_123")
        
        key = ConfigValidator.check_api_key_strict("gemini")
        
        assert key == "test_key_123"
    
    def test_check_api_key_strict_missing(self, clean_env):
        """Test strict API key check raises APIKeyMissingError"""
        from gformfiller.infrastructure.config.exceptions import APIKeyMissingError
        
        with pytest.raises(APIKeyMissingError) as exc_info:
            ConfigValidator.check_api_key_strict("gemini")
        
        assert exc_info.value.provider == "gemini"
        assert exc_info.value.env_var == "GEMINI_API_KEY"
    
    def test_check_api_key_strict_empty(self, monkeypatch, clean_env):
        """Test strict API key check raises error for empty key"""
        from gformfiller.infrastructure.config.exceptions import APIKeyMissingError
        
        monkeypatch.setenv("GEMINI_API_KEY", "")
        
        with pytest.raises(APIKeyMissingError):
            ConfigValidator.check_api_key_strict("gemini")
    
    def test_check_api_key_strict_invalid_provider(self):
        """Test strict API key check raises ValueError for unknown provider"""
        with pytest.raises(ValueError) as exc_info:
            ConfigValidator.check_api_key_strict("unknown_provider")
        
        assert "unknown provider" in str(exc_info.value).lower()