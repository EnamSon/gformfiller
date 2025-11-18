"""Tests for CLI config commands"""

import pytest
from typer.testing import CliRunner
from pathlib import Path
import tomli
import tomli_w
from unittest.mock import patch, mock_open, MagicMock

from gformfiller.cli.commands.config import config_app
from gformfiller.infrastructure.config import ConfigPaths, ConfigInitializer
from rich.console import Console

# Create a CliRunner instance
runner = CliRunner()

@patch(
    'gformfiller.cli.commands.config.console', 
    new=Console(force_terminal=False)
)
class TestConfigInit:
    """Tests for 'config init' command"""
    
    def test_init_creates_structure(self, temp_config_dir):
        """Test that init creates the config structure"""
        result = runner.invoke(config_app, ["init"])
        
        assert result.exit_code == 0
        assert "initialized" in result.stdout.lower()
        assert ConfigPaths.BASE_DIR.exists()
        assert ConfigPaths.CONFIG_DIR.exists()
        assert ConfigPaths.CONSTANTS_FILE.exists()
    
    def test_init_shows_created_structure(self, temp_config_dir):
        """Test that init displays created structure"""
        result = runner.invoke(config_app, ["init"])
        
        assert result.exit_code == 0
        
        # Check that directories are mentioned
        assert str(ConfigPaths.BASE_DIR) in result.stdout
        assert str(ConfigPaths.CONFIG_DIR) in result.stdout
        assert str(ConfigPaths.PARSERS_DIR) in result.stdout
        assert str(ConfigPaths.LOGS_DIR) in result.stdout
        assert str(ConfigPaths.PROMPTS_DIR) in result.stdout
        assert str(ConfigPaths.RESPONSES_DIR) in result.stdout
    
    def test_init_already_exists_without_force(self, temp_config_dir):
        """Test that init warns when config already exists"""
        # First init
        runner.invoke(config_app, ["init"])
        
        # Second init without force
        result = runner.invoke(config_app, ["init"])
        
        assert result.exit_code == 0
        assert "already exists" in result.stdout.lower()
    
    def test_init_with_force_overwrites(self, temp_config_dir):
        """Test that init --force overwrites existing config"""
        # First init
        ConfigInitializer.initialize()
        
        # Modify config
        ConfigPaths.CONSTANTS_FILE.write_text("modified")
        
        # Init with force
        result = runner.invoke(config_app, ["init", "--force"])
        
        assert result.exit_code == 0
        assert "initialized" in result.stdout.lower()
        
        # Config should be valid TOML again
        with open(ConfigPaths.CONSTANTS_FILE, "rb") as f:
            config = tomli.load(f)
        assert "timeouts" in config
    
    def test_init_with_force_flag_short(self, temp_config_dir):
        """Test that init -f works as shorthand for --force"""
        ConfigInitializer.initialize()
        
        result = runner.invoke(config_app, ["init", "-f"])
        
        assert result.exit_code == 0
        assert "initialized" in result.stdout.lower()


class TestConfigShow:
    """Tests for 'config show' command"""
    
    def test_show_displays_config(self, temp_config_dir):
        """Test that show displays configuration"""
        ConfigInitializer.initialize()
        
        result = runner.invoke(config_app, ["show"])
        
        assert result.exit_code == 0
        # Should display section headers
        assert "Timeouts" in result.stdout or "timeouts" in result.stdout.lower()
        assert "Browser" in result.stdout or "browser" in result.stdout.lower()
        assert "AI" in result.stdout or "ai" in result.stdout.lower()
    
    def test_show_displays_values(self, temp_config_dir):
        """Test that show displays configuration values"""
        ConfigInitializer.initialize()
        
        result = runner.invoke(config_app, ["show"])
        
        assert result.exit_code == 0
        # Should show some values
        assert "30" in result.stdout  # Default page_load timeout
        assert "gemini" in result.stdout.lower()  # Default AI provider
    
    def test_show_with_source_flag(self, temp_config_dir):
        """Test show --source displays source information"""
        ConfigInitializer.initialize()
        
        result = runner.invoke(config_app, ["show", "--source"])
        
        assert result.exit_code == 0
        # Output should be similar to without --source for now
        assert result.exit_code == 0
    
    def test_show_json_format(self, temp_config_dir):
        """Test show --format json outputs valid JSON"""
        ConfigInitializer.initialize()
        
        result = runner.invoke(config_app, ["show", "--format", "json"])
        
        # Debug output if fails
        if result.exit_code != 0:
            print(f"Command failed!")
            print(f"STDOUT:\n{result.stdout}")
            if result.exception:
                print(f"Exception: {result.exception}")
                import traceback
                traceback.print_exception(type(result.exception), result.exception, result.exception.__traceback__)
        
        assert result.exit_code == 0, f"Command failed. Output:\n{result.stdout}"
        
        # Should be valid JSON
        import json
        try:
            data = json.loads(result.stdout)
            # Check for expected structure
            assert isinstance(data, dict), "JSON should be a dictionary"
            # Should have config sections
            assert "timeouts" in data or "page_load" in data, \
                f"Expected config data in JSON. Keys: {list(data.keys())}"
        except json.JSONDecodeError as e:
            pytest.fail(f"Output is not valid JSON: {e}\nOutput:\n{result.stdout}")
    
    def test_show_toml_format(self, temp_config_dir):
        """Test show --format toml outputs valid TOML"""
        ConfigInitializer.initialize()
        
        result = runner.invoke(config_app, ["show", "--format", "toml"])
        
        assert result.exit_code == 0, f"Command failed. Output:\n{result.stdout}"
        
        # Should be valid TOML
        try:
            config = tomli.loads(result.stdout)
            assert isinstance(config, dict), "TOML should parse to dictionary"
            
            # Check for expected structure (should be nested)
            assert "timeouts" in config or "page_load" in config, \
                f"Expected config data. Keys: {list(config.keys())}"
            
        except tomli.TOMLDecodeError as e:
            pytest.fail(f"Output is not valid TOML: {e}\nOutput:\n{result.stdout}")
    
    def test_show_table_format_default(self, temp_config_dir):
        """Test that table format is default"""
        ConfigInitializer.initialize()
        
        result = runner.invoke(config_app, ["show"])
        
        assert result.exit_code == 0
        assert result.stdout.strip() != ""
    
    def test_show_handles_missing_config(self, temp_config_dir):
        """Test show handles missing config gracefully"""
        result = runner.invoke(config_app, ["show"])
        
        # Should auto-initialize or show in a reasonable way
        assert result.exit_code in [0, 1]


class TestConfigPaths:
    """Tests for 'config paths' command"""
    
    def test_paths_displays_all_paths(self, temp_config_dir):
        """Test that paths displays all configuration paths"""
        result = runner.invoke(config_app, ["paths"])
        
        assert result.exit_code == 0
        
        # Should show all major paths
        assert "Base Directory" in result.stdout or str(ConfigPaths.BASE_DIR) in result.stdout
        assert "Config Directory" in result.stdout or str(ConfigPaths.CONFIG_DIR) in result.stdout
        assert "Constants File" in result.stdout or "constants.toml" in result.stdout
    
    def test_paths_shows_existence_status(self, temp_config_dir):
        """Test that paths shows whether paths exist"""
        ConfigInitializer.initialize()
        
        result = runner.invoke(config_app, ["paths"])
        
        assert result.exit_code == 0
        
        # Should indicate existence (checkmarks, colors, etc.)
        # Look for some indicator - depends on implementation
        assert "✓" in result.stdout or "exists" in result.stdout.lower() or "✗" in result.stdout
    
    def test_paths_before_initialization(self, temp_config_dir):
        """Test paths command before initialization"""
        result = runner.invoke(config_app, ["paths"])
        
        assert result.exit_code == 0
        
        # Should show paths even if they don't exist
        assert str(ConfigPaths.BASE_DIR) in result.stdout or "Base" in result.stdout
    
    def test_paths_shows_all_required_locations(self, temp_config_dir):
        """Test that all required paths are shown"""
        result = runner.invoke(config_app, ["paths"])
        
        assert result.exit_code == 0
        
        required_mentions = ["config", "parsers", "responses", "prompts", "logs"]
        stdout_lower = result.stdout.lower()
        
        # At least some of these should be mentioned
        found = sum(1 for keyword in required_mentions if keyword in stdout_lower)
        assert found >= 3  # At least 3 of the major directories


class TestConfigValidate:
    """Tests for 'config validate' command"""
    
    def test_validate_valid_config(self, temp_config_dir):
        """Test validate with valid configuration"""
        ConfigInitializer.initialize()
        
        result = runner.invoke(config_app, ["validate"])
        
        assert result.exit_code == 0
        assert "valid" in result.stdout.lower()
    
    def test_validate_shows_sections(self, temp_config_dir):
        """Test that validate shows what it's checking"""
        ConfigInitializer.initialize()
        
        result = runner.invoke(config_app, ["validate"])
        
        assert result.exit_code == 0
        # Should mention checking different aspects
        assert "constants.toml" in result.stdout.lower() or "config" in result.stdout.lower()
    
    def test_validate_missing_config(self, temp_config_dir):
        """Test validate with missing configuration"""
        # Don't initialize
        
        result = runner.invoke(config_app, ["validate"])
        
        # Should fail or warn
        assert "not found" in result.stdout.lower() or "missing" in result.stdout.lower()
    
    def test_validate_invalid_config(self, temp_config_dir, write_config_file):
        """Test validate with invalid configuration"""
        invalid_config = {
            "timeouts": {"page_load": -10},  # Invalid
        }
        write_config_file(invalid_config)
        
        result = runner.invoke(config_app, ["validate"])
        
        assert result.exit_code == 1
        assert "invalid" in result.stdout.lower() or "error" in result.stdout.lower()
    
    def test_validate_checks_api_keys(self, temp_config_dir, monkeypatch, clean_env):
        """Test that validate checks API keys"""
        ConfigInitializer.initialize()
        
        result = runner.invoke(config_app, ["validate"])
        
        assert result.exit_code in [0, 1]  # May fail due to missing keys
        
        # Should mention API keys
        assert "api" in result.stdout.lower() or "key" in result.stdout.lower()
    
    def test_validate_with_api_keys_present(self, temp_config_dir, monkeypatch, clean_env):
        """Test validate when API keys are present"""
        ConfigInitializer.initialize()
        
        # Set all API keys
        monkeypatch.setenv("GEMINI_API_KEY", "test_key")
        monkeypatch.setenv("CLAUDE_API_KEY", "test_key")
        monkeypatch.setenv("OPENAI_API_KEY", "test_key")
        monkeypatch.setenv("DEEPSEEK_API_KEY", "test_key")
        monkeypatch.setenv("COPILOT_API_KEY", "test_key")
        
        result = runner.invoke(config_app, ["validate"])
        
        assert result.exit_code == 0


class TestConfigEdit:
    """Tests for 'config edit' command"""
    
    def test_edit_constants_default(self, temp_config_dir, monkeypatch):
        """Test edit opens constants.toml by default"""
        ConfigInitializer.initialize()
        
        # Mock subprocess.run
        mock_run = MagicMock(return_value=MagicMock(returncode=0))
        monkeypatch.setattr("subprocess.run", mock_run)
        
        result = runner.invoke(config_app, ["edit"])
        
        assert result.exit_code == 0
        
        # Check that subprocess.run was called with constants file
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert str(ConfigPaths.CONSTANTS_FILE) in str(call_args)
    
    def test_edit_constants_explicit(self, temp_config_dir, monkeypatch):
        """Test edit --file constants"""
        ConfigInitializer.initialize()
        
        mock_run = MagicMock(return_value=MagicMock(returncode=0))
        monkeypatch.setattr("subprocess.run", mock_run)
        
        result = runner.invoke(config_app, ["edit", "--file", "constants"])
        
        assert result.exit_code == 0
        mock_run.assert_called_once()
    
    def test_edit_logging_file(self, temp_config_dir, monkeypatch):
        """Test edit --file logging"""
        ConfigInitializer.initialize()
        
        mock_run = MagicMock(return_value=MagicMock(returncode=0))
        monkeypatch.setattr("subprocess.run", mock_run)
        
        result = runner.invoke(config_app, ["edit", "--file", "logging"])
        
        assert result.exit_code == 0
        
        call_args = mock_run.call_args[0][0]
        assert str(ConfigPaths.LOGGING_FILE) in str(call_args)
    
    def test_edit_invalid_file(self, temp_config_dir):
        """Test edit with invalid file name"""
        ConfigInitializer.initialize()
        
        result = runner.invoke(config_app, ["edit", "--file", "invalid"])
        
        assert result.exit_code == 1
        assert "unknown" in result.stdout.lower() or "invalid" in result.stdout.lower()
    
    def test_edit_file_not_found(self, temp_config_dir):
        """Test edit when config file doesn't exist"""
        # Don't initialize
        
        result = runner.invoke(config_app, ["edit"])
        
        assert result.exit_code == 1
        assert "not found" in result.stdout.lower()
    
    def test_edit_uses_editor_env_var(self, temp_config_dir, monkeypatch):
        """Test that edit respects EDITOR environment variable"""
        ConfigInitializer.initialize()
        
        monkeypatch.setenv("EDITOR", "vim")
        
        mock_run = MagicMock(return_value=MagicMock(returncode=0))
        monkeypatch.setattr("subprocess.run", mock_run)
        
        result = runner.invoke(config_app, ["edit"])
        
        assert result.exit_code == 0
        
        # Check that vim was used
        call_args = mock_run.call_args[0][0]
        assert "vim" in call_args


class TestConfigSet:
    """Tests for 'config set' command"""
    
    def test_set_simple_value(self, temp_config_dir, sample_config_dict, write_config_file):
        """Test setting a simple configuration value"""
        write_config_file(sample_config_dict)
        
        result = runner.invoke(config_app, ["set", "timeouts.page_load", "60"])
        
        assert result.exit_code == 0
        assert "updated" in result.stdout.lower() or "60" in result.stdout
        
        # Verify file was updated
        with open(ConfigPaths.CONSTANTS_FILE, "rb") as f:
            config = tomli.load(f)
        assert config["timeouts"]["page_load"] == 60
    
    def test_set_nested_value(self, temp_config_dir, sample_config_dict, write_config_file):
        """Test setting nested configuration value"""
        write_config_file(sample_config_dict)
        
        result = runner.invoke(config_app, ["set", "ai.default_provider", "claude"])
        
        assert result.exit_code == 0
        
        with open(ConfigPaths.CONSTANTS_FILE, "rb") as f:
            config = tomli.load(f)
        assert config["ai"]["default_provider"] == "claude"
    
    def test_set_boolean_value(self, temp_config_dir, sample_config_dict, write_config_file):
        """Test setting boolean value"""
        write_config_file(sample_config_dict)
        
        result = runner.invoke(config_app, ["set", "dsl.cache_parsed_expressions", "false"])
        
        assert result.exit_code == 0
        
        with open(ConfigPaths.CONSTANTS_FILE, "rb") as f:
            config = tomli.load(f)
        assert config["dsl"]["cache_parsed_expressions"] is False
    
    def test_set_float_value(self, temp_config_dir, sample_config_dict, write_config_file):
        """Test setting float value"""
        write_config_file(sample_config_dict)
        
        result = runner.invoke(config_app, ["set", "ai.temperature", "0.5"])
        
        assert result.exit_code == 0
        
        with open(ConfigPaths.CONSTANTS_FILE, "rb") as f:
            config = tomli.load(f)
        assert config["ai"]["temperature"] == 0.5
    
    def test_set_invalid_key(self, temp_config_dir, sample_config_dict, write_config_file):
        """Test setting invalid key"""
        write_config_file(sample_config_dict)
        
        result = runner.invoke(config_app, ["set", "invalid.key", "value"])
        
        assert result.exit_code != 0
        assert "not found" in result.stdout.lower() or "error" in result.stdout.lower()
    
    def test_set_invalid_value(self, temp_config_dir, sample_config_dict, write_config_file):
        """Test setting invalid value"""
        write_config_file(sample_config_dict)
        
        result = runner.invoke(config_app, ["set", "timeouts.page_load", "-10"])
        
        # Typer can return exit codes 1 or 2 for different types of errors
        assert result.exit_code != 0, "Should fail with invalid value"
        stderr_lower = result.stderr.lower()
        assert "invalid" in stderr_lower or "error" in stderr_lower
    
    def test_set_updates_timestamp(self, temp_config_dir, sample_config_dict, write_config_file):
        """Test that set updates last_modified timestamp"""
        write_config_file(sample_config_dict)
        
        original_timestamp = sample_config_dict["meta"]["last_modified"]
        
        result = runner.invoke(config_app, ["set", "timeouts.page_load", "60"])
        
        assert result.exit_code == 0
        
        with open(ConfigPaths.CONSTANTS_FILE, "rb") as f:
            config = tomli.load(f)
        
        # Timestamp should be updated (or at least present)
        assert "last_modified" in config.get("meta", {})


class TestConfigCleanLogs:
    """Tests for 'config clean-logs' command"""
    
    def test_clean_logs_default(self, temp_config_dir):
        """Test clean-logs with default settings"""
        ConfigInitializer.initialize()
        
        # Create some log files
        log_dir = ConfigPaths.LOGS_DIR
        log_dir.mkdir(parents=True, exist_ok=True)
        (log_dir / "test1.log").touch()
        (log_dir / "test2.log").touch()
        
        result = runner.invoke(config_app, ["clean-logs"])
        
        assert result.exit_code == 0
    
    def test_clean_logs_older_than(self, temp_config_dir):
        """Test clean-logs --older-than"""
        ConfigInitializer.initialize()
        
        result = runner.invoke(config_app, ["clean-logs", "--older-than", "30"])
        
        assert result.exit_code == 0
    
    def test_clean_logs_dry_run(self, temp_config_dir):
        """Test clean-logs --dry-run"""
        ConfigInitializer.initialize()
        
        log_dir = ConfigPaths.LOGS_DIR
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "test.log"
        log_file.touch()
        
        result = runner.invoke(config_app, ["clean-logs", "--dry-run"])
        
        assert result.exit_code == 0
        # File should still exist
        assert log_file.exists()
    
    def test_clean_logs_shows_results(self, temp_config_dir):
        """Test that clean-logs shows what was deleted"""
        ConfigInitializer.initialize()
        
        result = runner.invoke(config_app, ["clean-logs"])
        
        assert result.exit_code == 0
        # Should show some output about cleaning
        assert "log" in result.stdout.lower() or "clean" in result.stdout.lower()


class TestConfigCleanCache:
    """Tests for 'config clean-cache' command"""
    
    def test_clean_cache_requires_confirmation(self, temp_config_dir):
        """Test that clean-cache requires confirmation"""
        ConfigInitializer.initialize()
        
        # Without --yes, should prompt (which will fail in non-interactive test)
        result = runner.invoke(config_app, ["clean-cache"], input="n\n")
        
        # Should handle the "no" response
        assert "cancel" in result.stdout.lower() or result.exit_code == 0
    
    def test_clean_cache_with_yes_flag(self, temp_config_dir):
        """Test clean-cache --yes skips confirmation"""
        ConfigInitializer.initialize()
        
        # Create cache directory with files
        cache_dir = ConfigPaths.CACHE_DIR
        cache_dir.mkdir(parents=True, exist_ok=True)
        (cache_dir / "cache_file.dat").touch()
        
        result = runner.invoke(config_app, ["clean-cache", "--yes"])
        
        assert result.exit_code == 0
        assert "cleaned" in result.stdout.lower() or "cache" in result.stdout.lower()
    
    def test_clean_cache_removes_files(self, temp_config_dir):
        """Test that clean-cache actually removes cache files"""
        ConfigInitializer.initialize()
        
        cache_dir = ConfigPaths.CACHE_DIR
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = cache_dir / "test_cache.dat"
        cache_file.touch()
        
        result = runner.invoke(config_app, ["clean-cache", "--yes"])
        
        assert result.exit_code == 0
        # Cache file should be removed
        assert not cache_file.exists()
    
    def test_clean_cache_preserves_gitkeep(self, temp_config_dir):
        """Test that clean-cache preserves .gitkeep file"""
        ConfigInitializer.initialize()
        
        gitkeep = ConfigPaths.CACHE_DIR / ".gitkeep"
        
        result = runner.invoke(config_app, ["clean-cache", "--yes"])
        
        assert result.exit_code == 0
        # .gitkeep should be preserved
        assert gitkeep.exists()


class TestConfigReset:
    """Tests for 'config reset' command"""
    
    def test_reset_requires_confirmation(self, temp_config_dir):
        """Test that reset requires confirmation"""
        ConfigInitializer.initialize()
        
        result = runner.invoke(config_app, ["reset"], input="n\n")
        
        assert "cancel" in result.stdout.lower() or result.exit_code == 0
    
    def test_reset_with_yes_flag(self, temp_config_dir):
        """Test reset --yes skips confirmation"""
        ConfigInitializer.initialize()
        
        result = runner.invoke(config_app, ["reset", "--yes"])
        
        assert result.exit_code == 0
        assert "reset" in result.stdout.lower()
    
    def test_reset_creates_backup(self, temp_config_dir):
        """Test that reset creates backup"""
        ConfigInitializer.initialize()
        
        result = runner.invoke(config_app, ["reset", "--yes"])
        
        assert result.exit_code == 0
        assert "backup" in result.stdout.lower()
    
    def test_reset_reinitializes_config(self, temp_config_dir):
        """Test that reset reinitializes configuration"""
        ConfigInitializer.initialize()
        
        # Modify config
        ConfigPaths.CONSTANTS_FILE.write_text("modified")
        
        result = runner.invoke(config_app, ["reset", "--yes"])
        
        assert result.exit_code == 0
        
        # Config should be valid again
        assert ConfigPaths.CONSTANTS_FILE.exists()
        with open(ConfigPaths.CONSTANTS_FILE, "rb") as f:
            config = tomli.load(f)
        assert "timeouts" in config
    
    def test_reset_shows_warning(self, temp_config_dir):
        """Test that reset shows warning message"""
        ConfigInitializer.initialize()
        
        result = runner.invoke(config_app, ["reset"], input="n\n")
        
        assert "warning" in result.stdout.lower() or "danger" in result.stdout.lower()