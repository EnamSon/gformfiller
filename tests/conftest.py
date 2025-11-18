"""Shared pytest fixtures"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock
import os


@pytest.fixture
def temp_home(tmp_path, monkeypatch):
    """Create temporary home directory"""
    temp_home_dir = tmp_path / "home"
    temp_home_dir.mkdir()
    monkeypatch.setenv("HOME", str(temp_home_dir))
    return temp_home_dir


@pytest.fixture
def temp_config_dir(tmp_path, monkeypatch):
    """
    Create temporary config directory and patch ConfigPaths
    This is the most commonly used fixture
    """
    from gformfiller.infrastructure.config import ConfigPaths
    
    config_dir = tmp_path / ".gformfiller"
    
    # Patch all ConfigPaths attributes
    monkeypatch.setattr(ConfigPaths, "BASE_DIR", config_dir)
    monkeypatch.setattr(ConfigPaths, "CONFIG_DIR", config_dir / "config")
    monkeypatch.setattr(ConfigPaths, "PARSERS_DIR", config_dir / "parsers")
    monkeypatch.setattr(ConfigPaths, "RESPONSES_DIR", config_dir / "responses")
    monkeypatch.setattr(ConfigPaths, "PROMPTS_DIR", config_dir / "prompts")
    monkeypatch.setattr(ConfigPaths, "LOGS_DIR", config_dir / "logs")
    monkeypatch.setattr(ConfigPaths, "CACHE_DIR", config_dir / "cache")
    monkeypatch.setattr(ConfigPaths, "CONSTANTS_FILE", config_dir / "config" / "constants.toml")
    monkeypatch.setattr(ConfigPaths, "LOGGING_FILE", config_dir / "config" / "logging.toml")
    monkeypatch.setattr(ConfigPaths, "VERSION_FILE", config_dir / ".gformfiller_version")
    monkeypatch.setattr(ConfigPaths, "DEFAULT_PROMPT_FILE", config_dir / "prompts" / "default.txt")
    
    return config_dir


@pytest.fixture(autouse=False)  # Not autouse - must be explicitly requested
def clean_env(monkeypatch):
    """
    Clean environment variables with GFORMFILLER_ prefix
    This fixture must be requested explicitly in tests that need it
    """
    # Get all GFORMFILLER_ env vars
    env_vars_to_remove = [key for key in os.environ.keys() if key.startswith("GFORMFILLER_")]
    
    # Remove them using monkeypatch (this ensures they're restored after test)
    for var in env_vars_to_remove:
        monkeypatch.delenv(var, raising=False)
    
    # Also clean API keys
    api_keys = [
        "GEMINI_API_KEY", 
        "CLAUDE_API_KEY", 
        "OPENAI_API_KEY", 
        "DEEPSEEK_API_KEY", 
        "COPILOT_API_KEY"
    ]
    for key in api_keys:
        monkeypatch.delenv(key, raising=False)
    
    return monkeypatch


@pytest.fixture
def sample_config_dict():
    """Sample valid configuration dictionary"""
    return {
        "meta": {
            "config_version": "1.0.0",
            "created_at": "2025-01-01T00:00:00",
            "last_modified": "2025-01-01T00:00:00",
        },
        "timeouts": {
            "page_load": 30,
            "element_wait": 10,
            "script_execution": 5,
            "ai_response": 60,
            "form_submission": 15,
        },
        "retry": {
            "max_attempts": 3,
            "backoff_factor": 2.0,
            "initial_delay": 1.0,
        },
        "browser": {
            "implicit_wait": 0,
            "window_width": 1920,
            "window_height": 1080,
            "user_agent": "",
            "page_load_strategy": "normal",
        },
        "ai": {
            "max_tokens": 2000,
            "temperature": 0.7,
            "default_provider": "gemini",
            "stream_timeout": 120,
        },
        "dsl": {
            "cache_parsed_expressions": True,
            "max_expression_length": 500,
            "case_sensitive": False,
        },
        "logging": {
            "level": "INFO",
            "format": "structured",
            "max_file_size_mb": 10,
            "backup_count": 5,
            "console_timestamps": True,
            "file_name": "gformfiller.log",
        },
        "performance": {
            "parallel_ai_calls": False,
            "cache_ai_responses": False,
            "cache_ttl": 3600,
        },
        "validation": {
            "check_required_fields": True,
            "validate_email_format": True,
            "validate_phone_format": True,
            "phone_format": "any",
        },
        "security": {
            "mask_sensitive_data": True,
            "verify_ssl": True,
        },
    }


@pytest.fixture
def write_config_file(temp_config_dir):
    """Factory fixture to write config files"""
    import tomli_w
    from gformfiller.infrastructure.config import ConfigPaths
    
    def _write(config_dict: dict, file_path: Path | None = None):
        if file_path is None:
            file_path = ConfigPaths.CONSTANTS_FILE
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "wb") as f:
            tomli_w.dump(config_dict, f)
        
        return file_path
    
    return _write


@pytest.fixture
def cli_runner():
    """CLI test runner"""
    from typer.testing import CliRunner
    return CliRunner()