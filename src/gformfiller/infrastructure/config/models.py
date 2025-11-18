# infrastructure/config/models.py

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Literal
from datetime import datetime
from pathlib import Path

class MetaConfig(BaseModel):
    """Configuration metadata"""
    config_version: str = "1.0.0"
    created_at: datetime = Field(default_factory=datetime.now)
    last_modified: datetime = Field(default_factory=datetime.now)
    
    class Config:
        frozen = True


class TimeoutsConfig(BaseModel):
    """Timeout configurations"""
    page_load: int = Field(default=30, ge=5, le=120, description="Page load timeout in seconds")
    element_wait: int = Field(default=10, ge=1, le=60, description="Element wait timeout in seconds")
    script_execution: int = Field(default=5, ge=1, le=30, description="Script execution timeout in seconds")
    ai_response: int = Field(default=60, ge=10, le=300, description="AI response timeout in seconds")
    form_submission: int = Field(default=15, ge=5, le=60, description="Form submission timeout in seconds")
    
    class Config:
        frozen = True


class RetryConfig(BaseModel):
    """Retry mechanism configurations"""
    max_attempts: int = Field(default=3, ge=1, le=10, description="Maximum retry attempts")
    backoff_factor: float = Field(default=2.0, ge=1.0, le=5.0, description="Exponential backoff multiplier")
    initial_delay: float = Field(default=1.0, ge=0.1, le=10.0, description="Initial retry delay in seconds")
    
    class Config:
        frozen = True


class BrowserConfig(BaseModel):
    """Browser configurations"""
    implicit_wait: int = Field(default=0, ge=0, le=30, description="Selenium implicit wait")
    window_width: int = Field(default=1920, ge=800, description="Browser window width")
    window_height: int = Field(default=1080, ge=600, description="Browser window height")
    user_agent: str = Field(default="", description="Custom user agent")
    page_load_strategy: Literal["normal", "eager", "none"] = Field(default="normal")
    
    @field_validator("window_width", "window_height")
    @classmethod
    def validate_dimensions(cls, v: int, info) -> int:
        """Ensure reasonable window dimensions"""
        if v > 7680:  # 8K resolution
            return 1920 if info.field_name == "window_width" else 1080
        return v
    
    class Config:
        frozen = True


class AIConfig(BaseModel):
    """AI provider configurations"""
    max_tokens: int = Field(default=2000, ge=100, le=8000, description="Maximum tokens for responses")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Response temperature")
    default_provider: Literal["gemini", "claude", "openai", "deepseek", "copilot"] = "gemini"
    stream_timeout: int = Field(default=120, ge=30, le=300, description="Streaming timeout")

    class Config:
        frozen = True


class DSLConfig(BaseModel):
    """DSL parser configurations"""
    cache_parsed_expressions: bool = Field(default=True, description="Cache parsed DSL expressions")
    max_expression_length: int = Field(default=500, ge=10, le=5000, description="Max DSL expression length")
    case_sensitive: bool = Field(default=False, description="Case-sensitive matching")
    
    class Config:
        frozen = True


class LoggingConfig(BaseModel):
    """Logging configurations"""
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    format: Literal["structured", "simple"] = "structured"
    max_file_size_mb: int = Field(default=10, ge=1, le=100, description="Max log file size in MB")
    backup_count: int = Field(default=5, ge=1, le=20, description="Number of backup log files")
    console_timestamps: bool = Field(default=True, description="Include timestamps in console")
    file_name: str = Field(default="gformfiller.log", description="Log file name")
    
    class Config:
        frozen = True


class PerformanceConfig(BaseModel):
    """Performance optimization configurations"""
    parallel_ai_calls: bool = Field(default=False, description="Enable parallel AI calls")
    cache_ai_responses: bool = Field(default=False, description="Cache AI responses")
    cache_ttl: int = Field(default=3600, ge=60, le=86400, description="Cache TTL in seconds")
    
    class Config:
        frozen = True


class ValidationConfig(BaseModel):
    """Form validation configurations"""
    check_required_fields: bool = Field(default=True, description="Verify required fields")
    validate_email_format: bool = Field(default=True, description="Validate email format")
    validate_phone_format: bool = Field(default=True, description="Validate phone format")
    phone_format: Literal["international", "national", "any"] = "any"
    
    class Config:
        frozen = True


class SecurityConfig(BaseModel):
    """Security configurations"""
    mask_sensitive_data: bool = Field(default=True, description="Mask sensitive data in logs")
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")
    
    class Config:
        frozen = True


class ConstantsConfig(BaseModel):
    """Main configuration container"""
    meta: MetaConfig = Field(default_factory=MetaConfig)
    timeouts: TimeoutsConfig = Field(default_factory=TimeoutsConfig)
    retry: RetryConfig = Field(default_factory=RetryConfig)
    browser: BrowserConfig = Field(default_factory=BrowserConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    dsl: DSLConfig = Field(default_factory=DSLConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    
    class Config:
        frozen = True
        extra = "forbid"  # Reject unknown fields
    
    @model_validator(mode="after")
    def validate_cross_dependencies(self) -> "ConstantsConfig":
        """Validate cross-field dependencies"""
        # AI timeout should be >= element wait timeout
        if self.timeouts.ai_response < self.timeouts.element_wait:
            # This is permissive mode, so we just log warning (handled in loader)
            pass
        
        return self