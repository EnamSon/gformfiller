"""Tests for Pydantic configuration models"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from gformfiller.infrastructure.config.models import (
    ConstantsConfig,
    TimeoutsConfig,
    RetryConfig,
    BrowserConfig,
    AIConfig,
    DSLConfig,
    LoggingConfig,
    PerformanceConfig,
    ValidationConfig,
    SecurityConfig,
    MetaConfig,
)


class TestMetaConfig:
    """Tests for MetaConfig"""
    
    def test_default_values(self):
        """Test default values are set correctly"""
        meta = MetaConfig()
        
        assert meta.config_version == "1.0.0"
        assert isinstance(meta.created_at, datetime)
        assert isinstance(meta.last_modified, datetime)
    
    def test_frozen(self):
        """Test config is frozen (immutable)"""
        meta = MetaConfig()
        
        with pytest.raises(ValidationError):
            meta.config_version = "2.0.0"


class TestTimeoutsConfig:
    """Tests for TimeoutsConfig"""
    
    def test_default_values(self):
        """Test default timeout values"""
        timeouts = TimeoutsConfig()
        
        assert timeouts.page_load == 30
        assert timeouts.element_wait == 10
        assert timeouts.script_execution == 5
        assert timeouts.ai_response == 60
        assert timeouts.form_submission == 15
    
    def test_valid_custom_values(self):
        """Test valid custom values"""
        timeouts = TimeoutsConfig(
            page_load=60,
            element_wait=20,
            ai_response=120,
        )
        
        assert timeouts.page_load == 60
        assert timeouts.element_wait == 20
        assert timeouts.ai_response == 120
    
    def test_validation_min_values(self):
        """Test minimum value validation"""
        with pytest.raises(ValidationError):
            TimeoutsConfig(page_load=1)  # Min is 5
        
        with pytest.raises(ValidationError):
            TimeoutsConfig(element_wait=0)  # Min is 1
    
    def test_validation_max_values(self):
        """Test maximum value validation"""
        with pytest.raises(ValidationError):
            TimeoutsConfig(page_load=150)  # Max is 120
        
        with pytest.raises(ValidationError):
            TimeoutsConfig(ai_response=500)  # Max is 300
    
    def test_frozen(self):
        """Test config is immutable"""
        timeouts = TimeoutsConfig()
        
        with pytest.raises(ValidationError):
            timeouts.page_load = 60


class TestRetryConfig:
    """Tests for RetryConfig"""
    
    def test_default_values(self):
        """Test default retry values"""
        retry = RetryConfig()
        
        assert retry.max_attempts == 3
        assert retry.backoff_factor == 2.0
        assert retry.initial_delay == 1.0
    
    def test_valid_custom_values(self):
        """Test valid custom retry values"""
        retry = RetryConfig(
            max_attempts=5,
            backoff_factor=1.5,
            initial_delay=0.5,
        )
        
        assert retry.max_attempts == 5
        assert retry.backoff_factor == 1.5
        assert retry.initial_delay == 0.5
    
    def test_validation_max_attempts(self):
        """Test max_attempts validation"""
        with pytest.raises(ValidationError):
            RetryConfig(max_attempts=0)  # Min is 1
        
        with pytest.raises(ValidationError):
            RetryConfig(max_attempts=15)  # Max is 10
    
    def test_validation_backoff_factor(self):
        """Test backoff_factor validation"""
        with pytest.raises(ValidationError):
            RetryConfig(backoff_factor=0.5)  # Min is 1.0
        
        with pytest.raises(ValidationError):
            RetryConfig(backoff_factor=6.0)  # Max is 5.0


class TestBrowserConfig:
    """Tests for BrowserConfig"""
    
    def test_default_values(self):
        """Test default browser values"""
        browser = BrowserConfig()
        
        assert browser.implicit_wait == 0
        assert browser.window_width == 1920
        assert browser.window_height == 1080
        assert browser.user_agent == ""
        assert browser.page_load_strategy == "normal"
    
    def test_valid_custom_values(self):
        """Test valid custom browser values"""
        browser = BrowserConfig(
            window_width=1280,
            window_height=720,
            user_agent="CustomAgent",
            page_load_strategy="eager",
        )
        
        assert browser.window_width == 1280
        assert browser.window_height == 720
        assert browser.user_agent == "CustomAgent"
        assert browser.page_load_strategy == "eager"
    
    def test_validate_dimensions_clamp(self):
        """Test dimension clamping for extreme values"""
        # Very large dimensions should be clamped
        browser = BrowserConfig(window_width=10000, window_height=10000)
        
        assert browser.window_width == 1920  # Clamped to default
        assert browser.window_height == 1080  # Clamped to default
    
    def test_validate_page_load_strategy(self):
        """Test page load strategy validation"""
        with pytest.raises(ValidationError):
            BrowserConfig(page_load_strategy="invalid")
        
        # Valid values
        for strategy in ["normal", "eager", "none"]:
            browser = BrowserConfig(page_load_strategy=strategy)
            assert browser.page_load_strategy == strategy


class TestAIConfig:
    """Tests for AIConfig"""
    
    def test_default_values(self):
        """Test default AI values"""
        ai = AIConfig()
        
        assert ai.max_tokens == 2000
        assert ai.temperature == 0.7
        assert ai.default_provider == "gemini"
        assert ai.stream_timeout == 120
    
    def test_valid_custom_values(self):
        """Test valid custom AI values"""
        ai = AIConfig(
            max_tokens=4000,
            temperature=0.5,
            default_provider="claude",
            stream_timeout=180,
        )
        
        assert ai.max_tokens == 4000
        assert ai.temperature == 0.5
        assert ai.default_provider == "claude"
        assert ai.stream_timeout == 180
    
    def test_temperature_validation_min(self):
        """Test temperature minimum validation"""
        with pytest.raises(ValidationError):
            AIConfig(temperature=-0.5)
    
    def test_temperature_validation_max(self):
        """Test temperature maximum validation"""
        with pytest.raises(ValidationError):
            AIConfig(temperature=3.0)
    
    def test_temperature_edge_cases(self):
        """Test temperature at boundary values"""
        # Minimum valid
        ai = AIConfig(temperature=0.0)
        assert ai.temperature == 0.0
        
        # Maximum valid
        ai = AIConfig(temperature=2.0)
        assert ai.temperature == 2.0
        
        # Valid middle value
        ai = AIConfig(temperature=1.0)
        assert ai.temperature == 1.0
    
    def test_max_tokens_validation(self):
        """Test max_tokens validation"""
        with pytest.raises(ValidationError):
            AIConfig(max_tokens=50)  # Below minimum
        
        with pytest.raises(ValidationError):
            AIConfig(max_tokens=10000)  # Above maximum
        
        # Valid values
        ai = AIConfig(max_tokens=100)  # Minimum
        assert ai.max_tokens == 100
        
        ai = AIConfig(max_tokens=8000)  # Maximum
        assert ai.max_tokens == 8000
    
    def test_valid_providers(self):
        """Test all valid AI providers"""
        providers = ["gemini", "claude", "openai", "deepseek", "copilot"]
        
        for provider in providers:
            ai = AIConfig(default_provider=provider)
            assert ai.default_provider == provider
    
    def test_invalid_provider(self):
        """Test invalid provider raises error"""
        with pytest.raises(ValidationError):
            AIConfig(default_provider="invalid_provider")
    
    def test_stream_timeout_validation(self):
        """Test stream_timeout validation"""
        with pytest.raises(ValidationError):
            AIConfig(stream_timeout=20)  # Below minimum
        
        with pytest.raises(ValidationError):
            AIConfig(stream_timeout=500)  # Above maximum
        
        # Valid values
        ai = AIConfig(stream_timeout=30)  # Minimum
        assert ai.stream_timeout == 30
        
        ai = AIConfig(stream_timeout=300)  # Maximum
        assert ai.stream_timeout == 300


class TestDSLConfig:
    """Tests for DSLConfig"""
    
    def test_default_values(self):
        """Test default DSL values"""
        dsl = DSLConfig()
        
        assert dsl.cache_parsed_expressions is True
        assert dsl.max_expression_length == 500
        assert dsl.case_sensitive is False
    
    def test_valid_custom_values(self):
        """Test valid custom DSL values"""
        dsl = DSLConfig(
            cache_parsed_expressions=False,
            max_expression_length=1000,
            case_sensitive=True,
        )
        
        assert dsl.cache_parsed_expressions is False
        assert dsl.max_expression_length == 1000
        assert dsl.case_sensitive is True
    
    def test_max_expression_length_validation(self):
        """Test max_expression_length validation"""
        with pytest.raises(ValidationError):
            DSLConfig(max_expression_length=5)  # Min is 10
        
        with pytest.raises(ValidationError):
            DSLConfig(max_expression_length=6000)  # Max is 5000


class TestLoggingConfig:
    """Tests for LoggingConfig"""
    
    def test_default_values(self):
        """Test default logging values"""
        logging = LoggingConfig()
        
        assert logging.level == "INFO"
        assert logging.format == "structured"
        assert logging.max_file_size_mb == 10
        assert logging.backup_count == 5
        assert logging.console_timestamps is True
        assert logging.file_name == "gformfiller.log"
    
    def test_valid_log_levels(self):
        """Test all valid log levels"""
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        for level in levels:
            logging = LoggingConfig(level=level)
            assert logging.level == level
    
    def test_invalid_log_level(self):
        """Test invalid log level raises error"""
        with pytest.raises(ValidationError):
            LoggingConfig(level="INVALID")
    
    def test_valid_formats(self):
        """Test valid log formats"""
        for fmt in ["structured", "simple"]:
            logging = LoggingConfig(format=fmt)
            assert logging.format == fmt
    
    def test_invalid_format(self):
        """Test invalid format raises error"""
        with pytest.raises(ValidationError):
            LoggingConfig(format="invalid")


class TestPerformanceConfig:
    """Tests for PerformanceConfig"""
    
    def test_default_values(self):
        """Test default performance values"""
        perf = PerformanceConfig()
        
        assert perf.parallel_ai_calls is False
        assert perf.cache_ai_responses is False
        assert perf.cache_ttl == 3600
    
    def test_valid_custom_values(self):
        """Test valid custom performance values"""
        perf = PerformanceConfig(
            parallel_ai_calls=True,
            cache_ai_responses=True,
            cache_ttl=7200,
        )
        
        assert perf.parallel_ai_calls is True
        assert perf.cache_ai_responses is True
        assert perf.cache_ttl == 7200


class TestValidationConfig:
    """Tests for ValidationConfig"""
    
    def test_default_values(self):
        """Test default validation values"""
        validation = ValidationConfig()
        
        assert validation.check_required_fields is True
        assert validation.validate_email_format is True
        assert validation.validate_phone_format is True
        assert validation.phone_format == "any"
    
    def test_valid_phone_formats(self):
        """Test valid phone formats"""
        for fmt in ["international", "national", "any"]:
            validation = ValidationConfig(phone_format=fmt)
            assert validation.phone_format == fmt
    
    def test_invalid_phone_format(self):
        """Test invalid phone format raises error"""
        with pytest.raises(ValidationError):
            ValidationConfig(phone_format="invalid")


class TestSecurityConfig:
    """Tests for SecurityConfig"""
    
    def test_default_values(self):
        """Test default security values"""
        security = SecurityConfig()
        
        assert security.mask_sensitive_data is True
        assert security.verify_ssl is True
    
    def test_custom_values(self):
        """Test custom security values"""
        security = SecurityConfig(
            mask_sensitive_data=False,
            verify_ssl=False,
        )
        
        assert security.mask_sensitive_data is False
        assert security.verify_ssl is False


class TestConstantsConfig:
    """Tests for main ConstantsConfig container"""
    
    def test_default_values(self):
        """Test default ConstantsConfig with all defaults"""
        config = ConstantsConfig()
        
        assert isinstance(config.meta, MetaConfig)
        assert isinstance(config.timeouts, TimeoutsConfig)
        assert isinstance(config.retry, RetryConfig)
        assert isinstance(config.browser, BrowserConfig)
        assert isinstance(config.ai, AIConfig)
        assert isinstance(config.dsl, DSLConfig)
        assert isinstance(config.logging, LoggingConfig)
        assert isinstance(config.performance, PerformanceConfig)
        assert isinstance(config.validation, ValidationConfig)
        assert isinstance(config.security, SecurityConfig)
    
    def test_custom_nested_values(self):
        """Test custom nested configuration values"""
        config = ConstantsConfig(
            timeouts={"page_load": 60},
            ai={"default_provider": "claude", "temperature": 0.5},
        )
        
        assert config.timeouts.page_load == 60
        assert config.timeouts.element_wait == 10  # Default preserved
        assert config.ai.default_provider == "claude"
        assert config.ai.temperature == 0.5
    
    def test_frozen(self):
        """Test entire config is frozen"""
        config = ConstantsConfig()
        
        with pytest.raises(ValidationError):
            config.timeouts = TimeoutsConfig(page_load=60)
    
    def test_extra_fields_forbidden(self):
        """Test that extra fields are rejected"""
        with pytest.raises(ValidationError):
            ConstantsConfig(extra_field="not_allowed")
    
    def test_model_dump(self):
        """Test model_dump returns complete dictionary"""
        config = ConstantsConfig()
        config_dict = config.model_dump()
        
        assert "meta" in config_dict
        assert "timeouts" in config_dict
        assert "retry" in config_dict
        assert "browser" in config_dict
        assert "ai" in config_dict
        assert "dsl" in config_dict
        assert "logging" in config_dict
        assert "performance" in config_dict
        assert "validation" in config_dict
        assert "security" in config_dict
    
    def test_from_dict(self, sample_config_dict):
        """Test creating config from dictionary"""
        config = ConstantsConfig(**sample_config_dict)
        
        assert config.timeouts.page_load == 30
        assert config.ai.default_provider == "gemini"
        assert config.logging.level == "INFO"