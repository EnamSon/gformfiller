"""Tests for configuration exceptions"""

import pytest

from gformfiller.infrastructure.config.exceptions import (
    ConfigError,
    ConfigValidationError,
    ConfigNotFoundError,
    ConfigParseError,
    APIKeyMissingError,
)


class TestConfigError:
    """Tests for base ConfigError"""
    
    def test_config_error_creation(self):
        """Test creating ConfigError"""
        error = ConfigError("Test error message")
        
        assert isinstance(error, Exception)
        assert str(error) == "Test error message"
    
    def test_config_error_inheritance(self):
        """Test ConfigError is base for other exceptions"""
        validation_error = ConfigValidationError("test")
        not_found_error = ConfigNotFoundError("/path/to/file")
        parse_error = ConfigParseError("/path/to/file", "bad syntax")
        api_key_error = APIKeyMissingError("gemini", "GEMINI_API_KEY")
        
        assert isinstance(validation_error, ConfigError)
        assert isinstance(not_found_error, ConfigError)
        assert isinstance(parse_error, ConfigError)
        assert isinstance(api_key_error, ConfigError)
    
    def test_config_error_raise(self):
        """Test raising ConfigError"""
        with pytest.raises(ConfigError) as exc_info:
            raise ConfigError("Test error")
        
        assert "Test error" in str(exc_info.value)


class TestConfigValidationError:
    """Tests for ConfigValidationError"""
    
    def test_validation_error_with_message_only(self):
        """Test ConfigValidationError with message only"""
        error = ConfigValidationError("Validation failed")
        
        assert str(error) == "Validation failed"
        assert error.errors == []
    
    def test_validation_error_with_errors_list(self):
        """Test ConfigValidationError with errors list"""
        errors = [
            "Field 'timeout' must be positive",
            "Field 'temperature' out of range",
        ]
        
        error = ConfigValidationError("Validation failed", errors=errors)
        
        assert str(error) == "Validation failed"
        assert error.errors == errors
        assert len(error.errors) == 2
    
    def test_validation_error_raise(self):
        """Test raising ConfigValidationError"""
        with pytest.raises(ConfigValidationError) as exc_info:
            raise ConfigValidationError("Invalid config", errors=["error1", "error2"])
        
        assert "Invalid config" in str(exc_info.value)
        assert exc_info.value.errors == ["error1", "error2"]
    
    def test_validation_error_is_config_error(self):
        """Test ConfigValidationError is a ConfigError"""
        error = ConfigValidationError("test")
        
        assert isinstance(error, ConfigError)


class TestConfigNotFoundError:
    """Tests for ConfigNotFoundError"""
    
    def test_not_found_error_creation(self):
        """Test creating ConfigNotFoundError"""
        path = "/home/user/.gformfiller/config/constants.toml"
        error = ConfigNotFoundError(path)
        
        assert str(error) == f"Configuration not found: {path}"
        assert error.path == path
    
    def test_not_found_error_with_relative_path(self):
        """Test ConfigNotFoundError with relative path"""
        path = "config/constants.toml"
        error = ConfigNotFoundError(path)
        
        assert path in str(error)
        assert error.path == path
    
    def test_not_found_error_raise(self):
        """Test raising ConfigNotFoundError"""
        with pytest.raises(ConfigNotFoundError) as exc_info:
            raise ConfigNotFoundError("/path/to/file")
        
        assert "/path/to/file" in str(exc_info.value)
        assert exc_info.value.path == "/path/to/file"
    
    def test_not_found_error_is_config_error(self):
        """Test ConfigNotFoundError is a ConfigError"""
        error = ConfigNotFoundError("/path")
        
        assert isinstance(error, ConfigError)


class TestConfigParseError:
    """Tests for ConfigParseError"""
    
    def test_parse_error_creation(self):
        """Test creating ConfigParseError"""
        path = "/home/user/.gformfiller/config/constants.toml"
        reason = "Invalid TOML syntax at line 5"
        error = ConfigParseError(path, reason)
        
        assert f"Failed to parse {path}" in str(error)
        assert reason in str(error)
        assert error.path == path
        assert error.reason == reason
    
    def test_parse_error_with_simple_reason(self):
        """Test ConfigParseError with simple reason"""
        error = ConfigParseError("config.toml", "Unexpected token")
        
        assert "config.toml" in str(error)
        assert "Unexpected token" in str(error)
    
    def test_parse_error_raise(self):
        """Test raising ConfigParseError"""
        with pytest.raises(ConfigParseError) as exc_info:
            raise ConfigParseError("/path/to/file", "bad syntax")
        
        assert "/path/to/file" in str(exc_info.value)
        assert "bad syntax" in str(exc_info.value)
        assert exc_info.value.path == "/path/to/file"
        assert exc_info.value.reason == "bad syntax"
    
    def test_parse_error_is_config_error(self):
        """Test ConfigParseError is a ConfigError"""
        error = ConfigParseError("/path", "reason")
        
        assert isinstance(error, ConfigError)


class TestAPIKeyMissingError:
    """Tests for APIKeyMissingError"""
    
    def test_api_key_missing_error_creation(self):
        """Test creating APIKeyMissingError"""
        error = APIKeyMissingError("gemini", "GEMINI_API_KEY")
        
        error_message = str(error)
        assert "gemini" in error_message
        assert "GEMINI_API_KEY" in error_message
        assert error.provider == "gemini"
        assert error.env_var == "GEMINI_API_KEY"
    
    def test_api_key_missing_error_different_providers(self):
        """Test APIKeyMissingError with different providers"""
        providers = [
            ("claude", "CLAUDE_API_KEY"),
            ("openai", "OPENAI_API_KEY"),
            ("deepseek", "DEEPSEEK_API_KEY"),
            ("copilot", "COPILOT_API_KEY"),
        ]
        
        for provider, env_var in providers:
            error = APIKeyMissingError(provider, env_var)
            
            assert provider in str(error)
            assert env_var in str(error)
            assert error.provider == provider
            assert error.env_var == env_var
    
    def test_api_key_missing_error_raise(self):
        """Test raising APIKeyMissingError"""
        with pytest.raises(APIKeyMissingError) as exc_info:
            raise APIKeyMissingError("gemini", "GEMINI_API_KEY")
        
        assert "gemini" in str(exc_info.value)
        assert "GEMINI_API_KEY" in str(exc_info.value)
        assert exc_info.value.provider == "gemini"
        assert exc_info.value.env_var == "GEMINI_API_KEY"
    
    def test_api_key_missing_error_is_config_error(self):
        """Test APIKeyMissingError is a ConfigError"""
        error = APIKeyMissingError("gemini", "GEMINI_API_KEY")
        
        assert isinstance(error, ConfigError)
    
    def test_api_key_missing_error_message_helpful(self):
        """Test error message provides helpful information"""
        error = APIKeyMissingError("claude", "CLAUDE_API_KEY")
        
        message = str(error).lower()
        # Should mention how to fix
        assert "not found" in message or "missing" in message
        assert "claude_api_key" in message


class TestExceptionUsage:
    """Tests for practical exception usage"""
    
    def test_catch_specific_exception(self):
        """Test catching specific config exception"""
        def raise_validation_error():
            raise ConfigValidationError("Invalid config")
        
        with pytest.raises(ConfigValidationError):
            raise_validation_error()
    
    def test_catch_base_exception(self):
        """Test catching base ConfigError catches all config exceptions"""
        def raise_specific_error():
            raise ConfigNotFoundError("/path/to/file")
        
        with pytest.raises(ConfigError):
            raise_specific_error()
    
    def test_exception_in_try_except(self):
        """Test using exceptions in try-except blocks"""
        try:
            raise APIKeyMissingError("gemini", "GEMINI_API_KEY")
        except ConfigError as e:
            assert isinstance(e, APIKeyMissingError)
            assert e.provider == "gemini"
        else:
            pytest.fail("Exception not raised")
    
    def test_multiple_exception_handling(self):
        """Test handling multiple config exception types"""
        def risky_operation(error_type):
            if error_type == "validation":
                raise ConfigValidationError("Invalid")
            elif error_type == "not_found":
                raise ConfigNotFoundError("/path")
            elif error_type == "parse":
                raise ConfigParseError("/path", "reason")
        
        # Test each exception type
        with pytest.raises(ConfigValidationError):
            risky_operation("validation")
        
        with pytest.raises(ConfigNotFoundError):
            risky_operation("not_found")
        
        with pytest.raises(ConfigParseError):
            risky_operation("parse")
    
    def test_exception_attributes_accessible(self):
        """Test that exception attributes are accessible after catching"""
        try:
            raise ConfigParseError("/my/path", "my reason")
        except ConfigParseError as e:
            assert e.path == "/my/path"
            assert e.reason == "my reason"
        
        try:
            raise APIKeyMissingError("test_provider", "TEST_KEY")
        except APIKeyMissingError as e:
            assert e.provider == "test_provider"
            assert e.env_var == "TEST_KEY"