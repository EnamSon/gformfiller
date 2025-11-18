"""Tests for default configuration values"""

import pytest

from gformfiller.infrastructure.config.defaults import (
    DEFAULT_CONFIG,
    DEFAULT_PROMPT,
    ENV_PREFIX,
    SUPPORTED_AI_PROVIDERS,
    API_KEY_ENV_VARS,
)
from gformfiller.infrastructure.config.models import ConstantsConfig


class TestDefaultConfig:
    """Tests for DEFAULT_CONFIG"""
    
    def test_default_config_is_valid_instance(self):
        """Test DEFAULT_CONFIG is a valid ConstantsConfig instance"""
        assert isinstance(DEFAULT_CONFIG, ConstantsConfig)
    
    def test_default_config_has_all_sections(self):
        """Test DEFAULT_CONFIG contains all required sections"""
        config_dict = DEFAULT_CONFIG.model_dump()
        
        required_sections = [
            "meta", "timeouts", "retry", "browser", "ai",
            "dsl", "logging", "performance", "validation", "security"
        ]
        
        for section in required_sections:
            assert section in config_dict, f"Missing section: {section}"
    
    def test_default_timeout_values(self):
        """Test default timeout values are reasonable"""
        assert DEFAULT_CONFIG.timeouts.page_load == 30
        assert DEFAULT_CONFIG.timeouts.element_wait == 10
        assert DEFAULT_CONFIG.timeouts.script_execution == 5
        assert DEFAULT_CONFIG.timeouts.ai_response == 60
        assert DEFAULT_CONFIG.timeouts.form_submission == 15
    
    def test_default_retry_values(self):
        """Test default retry values are reasonable"""
        assert DEFAULT_CONFIG.retry.max_attempts == 3
        assert DEFAULT_CONFIG.retry.backoff_factor == 2.0
        assert DEFAULT_CONFIG.retry.initial_delay == 1.0
    
    def test_default_browser_values(self):
        """Test default browser values"""
        assert DEFAULT_CONFIG.browser.implicit_wait == 0
        assert DEFAULT_CONFIG.browser.window_width == 1920
        assert DEFAULT_CONFIG.browser.window_height == 1080
        assert DEFAULT_CONFIG.browser.user_agent == ""
        assert DEFAULT_CONFIG.browser.page_load_strategy == "normal"
    
    def test_default_ai_values(self):
        """Test default AI values"""
        assert DEFAULT_CONFIG.ai.max_tokens == 2000
        assert DEFAULT_CONFIG.ai.temperature == 0.7
        assert DEFAULT_CONFIG.ai.default_provider == "gemini"
        assert DEFAULT_CONFIG.ai.stream_timeout == 120
    
    def test_default_dsl_values(self):
        """Test default DSL values"""
        assert DEFAULT_CONFIG.dsl.cache_parsed_expressions is True
        assert DEFAULT_CONFIG.dsl.max_expression_length == 500
        assert DEFAULT_CONFIG.dsl.case_sensitive is False
    
    def test_default_logging_values(self):
        """Test default logging values"""
        assert DEFAULT_CONFIG.logging.level == "INFO"
        assert DEFAULT_CONFIG.logging.format == "structured"
        assert DEFAULT_CONFIG.logging.max_file_size_mb == 10
        assert DEFAULT_CONFIG.logging.backup_count == 5
        assert DEFAULT_CONFIG.logging.console_timestamps is True
        assert DEFAULT_CONFIG.logging.file_name == "gformfiller.log"
    
    def test_default_performance_values(self):
        """Test default performance values"""
        assert DEFAULT_CONFIG.performance.parallel_ai_calls is False
        assert DEFAULT_CONFIG.performance.cache_ai_responses is False
        assert DEFAULT_CONFIG.performance.cache_ttl == 3600
    
    def test_default_validation_values(self):
        """Test default validation values"""
        assert DEFAULT_CONFIG.validation.check_required_fields is True
        assert DEFAULT_CONFIG.validation.validate_email_format is True
        assert DEFAULT_CONFIG.validation.validate_phone_format is True
        assert DEFAULT_CONFIG.validation.phone_format == "any"
    
    def test_default_security_values(self):
        """Test default security values"""
        assert DEFAULT_CONFIG.security.mask_sensitive_data is True
        assert DEFAULT_CONFIG.security.verify_ssl is True
    
    def test_default_config_is_frozen(self):
        """Test DEFAULT_CONFIG is immutable"""
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            DEFAULT_CONFIG.timeouts.page_load = 60


class TestDefaultPrompt:
    """Tests for DEFAULT_PROMPT"""
    
    def test_default_prompt_is_string(self):
        """Test DEFAULT_PROMPT is a string"""
        assert isinstance(DEFAULT_PROMPT, str)
    
    def test_default_prompt_not_empty(self):
        """Test DEFAULT_PROMPT is not empty"""
        assert len(DEFAULT_PROMPT) > 0
    
    def test_default_prompt_contains_guidelines(self):
        """Test DEFAULT_PROMPT contains key guidelines"""
        assert "form-filling assistant" in DEFAULT_PROMPT.lower()
        assert "guidelines" in DEFAULT_PROMPT.lower()
    
    def test_default_prompt_mentions_context(self):
        """Test DEFAULT_PROMPT mentions user context"""
        assert "context" in DEFAULT_PROMPT.lower()


class TestEnvPrefix:
    """Tests for ENV_PREFIX"""
    
    def test_env_prefix_is_correct(self):
        """Test ENV_PREFIX is set correctly"""
        assert ENV_PREFIX == "GFORMFILLER_"
    
    def test_env_prefix_ends_with_underscore(self):
        """Test ENV_PREFIX ends with underscore for proper variable naming"""
        assert ENV_PREFIX.endswith("_")


class TestSupportedAIProviders:
    """Tests for SUPPORTED_AI_PROVIDERS"""
    
    def test_supported_providers_is_list(self):
        """Test SUPPORTED_AI_PROVIDERS is a list"""
        assert isinstance(SUPPORTED_AI_PROVIDERS, list)
    
    def test_supported_providers_not_empty(self):
        """Test SUPPORTED_AI_PROVIDERS contains providers"""
        assert len(SUPPORTED_AI_PROVIDERS) > 0
    
    def test_supported_providers_contains_expected(self):
        """Test SUPPORTED_AI_PROVIDERS contains expected providers"""
        expected = ["gemini", "claude", "openai", "deepseek", "copilot"]
        
        for provider in expected:
            assert provider in SUPPORTED_AI_PROVIDERS, f"Missing provider: {provider}"
    
    def test_supported_providers_all_lowercase(self):
        """Test all provider names are lowercase"""
        for provider in SUPPORTED_AI_PROVIDERS:
            assert provider == provider.lower(), f"Provider not lowercase: {provider}"
    
    def test_supported_providers_no_duplicates(self):
        """Test no duplicate providers"""
        assert len(SUPPORTED_AI_PROVIDERS) == len(set(SUPPORTED_AI_PROVIDERS))


class TestAPIKeyEnvVars:
    """Tests for API_KEY_ENV_VARS"""
    
    def test_api_key_env_vars_is_dict(self):
        """Test API_KEY_ENV_VARS is a dictionary"""
        assert isinstance(API_KEY_ENV_VARS, dict)
    
    def test_api_key_env_vars_not_empty(self):
        """Test API_KEY_ENV_VARS contains mappings"""
        assert len(API_KEY_ENV_VARS) > 0
    
    def test_all_providers_have_env_var(self):
        """Test all supported providers have env var mapping"""
        for provider in SUPPORTED_AI_PROVIDERS:
            assert provider in API_KEY_ENV_VARS, f"Missing env var for: {provider}"
    
    def test_env_var_names_format(self):
        """Test env var names follow correct format"""
        for provider, env_var in API_KEY_ENV_VARS.items():
            # Should be uppercase
            assert env_var == env_var.upper(), f"Env var not uppercase: {env_var}"
            
            # Should end with _API_KEY
            assert env_var.endswith("_API_KEY"), f"Env var doesn't end with _API_KEY: {env_var}"
    
    def test_expected_env_vars(self):
        """Test expected env var mappings"""
        expected = {
            "gemini": "GEMINI_API_KEY",
            "claude": "CLAUDE_API_KEY",
            "openai": "OPENAI_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
            "copilot": "COPILOT_API_KEY",
        }
        
        for provider, env_var in expected.items():
            assert API_KEY_ENV_VARS.get(provider) == env_var
    
    def test_no_duplicate_env_vars(self):
        """Test no duplicate env var names"""
        env_vars = list(API_KEY_ENV_VARS.values())
        assert len(env_vars) == len(set(env_vars))