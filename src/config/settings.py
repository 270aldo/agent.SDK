"""
Centralized configuration management for NGX Voice Sales Agent.

This module provides a single source of truth for all configuration
settings, with proper validation, type safety, and environment support.
"""

import os
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from pydantic import Field, validator, SecretStr
from pydantic_settings import BaseSettings
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


class Environment(str, Enum):
    """Application environments."""
    DEVELOPMENT = "development"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    """
    Application settings with validation and type safety.
    
    All settings can be overridden via environment variables.
    """
    
    # Application
    app_name: str = Field(default="NGX Voice Sales Agent", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    environment: Environment = Field(default=Environment.DEVELOPMENT, env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # API Configuration
    api_v1_prefix: str = Field(default="/api/v1", env="API_V1_PREFIX")
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT", ge=1, le=65535)
    api_workers: int = Field(default=1, env="API_WORKERS", ge=1)
    
    # Security
    jwt_secret: Optional[SecretStr] = Field(default=None, env="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_refresh_token_expire_days: int = Field(default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    
    # CORS
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        env="ALLOWED_ORIGINS"
    )
    allow_credentials: bool = Field(default=True, env="ALLOW_CREDENTIALS")
    allow_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        env="ALLOW_METHODS"
    )
    allow_headers: List[str] = Field(
        default=["Authorization", "Content-Type", "Accept"],
        env="ALLOW_HEADERS"
    )
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_per_hour: int = Field(default=1000, env="RATE_LIMIT_PER_HOUR")
    rate_limit_whitelist_ips: List[str] = Field(default=[], env="RATE_LIMIT_WHITELIST_IPS")
    
    # Database
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL")
    database_pool_size: int = Field(default=20, env="DATABASE_POOL_SIZE", ge=1)
    database_max_overflow: int = Field(default=10, env="DATABASE_MAX_OVERFLOW", ge=0)
    database_pool_timeout: int = Field(default=30, env="DATABASE_POOL_TIMEOUT")
    
    # Supabase
    supabase_url: Optional[str] = Field(default=None, env="SUPABASE_URL")
    supabase_anon_key: Optional[SecretStr] = Field(default=None, env="SUPABASE_ANON_KEY")
    supabase_service_role_key: Optional[SecretStr] = Field(default=None, env="SUPABASE_SERVICE_ROLE_KEY")
    
    # Redis
    redis_url: Optional[str] = Field(default="redis://localhost:6379", env="REDIS_URL")
    redis_pool_size: int = Field(default=10, env="REDIS_POOL_SIZE")
    redis_decode_responses: bool = Field(default=True, env="REDIS_DECODE_RESPONSES")
    
    # External APIs
    openai_api_key: Optional[SecretStr] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4-turbo-preview", env="OPENAI_MODEL")
    openai_temperature: float = Field(default=0.7, env="OPENAI_TEMPERATURE", ge=0, le=2)
    openai_max_tokens: int = Field(default=2000, env="OPENAI_MAX_TOKENS", ge=1)
    
    elevenlabs_api_key: Optional[SecretStr] = Field(default=None, env="ELEVENLABS_API_KEY")
    elevenlabs_voice_id: str = Field(default="21m00Tcm4TlvDq8ikWAM", env="ELEVENLABS_VOICE_ID")
    
    # Logging
    log_level: LogLevel = Field(default=LogLevel.INFO, env="LOG_LEVEL")
    log_file: Optional[str] = Field(default="logs/api.log", env="LOG_FILE")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    log_include_stack_info: bool = Field(default=False, env="LOG_INCLUDE_STACK_INFO")
    
    # Monitoring
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    enable_tracing: bool = Field(default=True, env="ENABLE_TRACING")
    jaeger_agent_host: str = Field(default="localhost", env="JAEGER_AGENT_HOST")
    jaeger_agent_port: int = Field(default=6831, env="JAEGER_AGENT_PORT")
    
    # Business Logic
    max_conversation_duration_minutes: int = Field(default=30, env="MAX_CONVERSATION_DURATION_MINUTES")
    max_messages_per_conversation: int = Field(default=100, env="MAX_MESSAGES_PER_CONVERSATION")
    conversation_cooldown_hours: int = Field(default=48, env="CONVERSATION_COOLDOWN_HOURS")
    
    # ML/AI Settings
    ml_model_cache_ttl: int = Field(default=3600, env="ML_MODEL_CACHE_TTL")
    ml_experiment_sample_rate: float = Field(default=0.1, env="ML_EXPERIMENT_SAMPLE_RATE", ge=0, le=1)
    ml_learning_enabled: bool = Field(default=True, env="ML_LEARNING_ENABLED")
    
    # Feature Flags
    feature_voice_synthesis: bool = Field(default=True, env="FEATURE_VOICE_SYNTHESIS")
    feature_ml_optimization: bool = Field(default=True, env="FEATURE_ML_OPTIMIZATION")
    feature_ab_testing: bool = Field(default=True, env="FEATURE_AB_TESTING")
    feature_trial_system: bool = Field(default=True, env="FEATURE_TRIAL_SYSTEM")
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    @validator("allowed_origins", pre=True)
    def parse_allowed_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse comma-separated string to list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("rate_limit_whitelist_ips", pre=True)
    def parse_whitelist_ips(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse comma-separated string to list."""
        if isinstance(v, str):
            return [ip.strip() for ip in v.split(",") if ip.strip()]
        return v
    
    @validator("jwt_secret")
    def validate_jwt_secret(cls, v: Optional[SecretStr], values: Dict[str, Any]) -> Optional[SecretStr]:
        """Validate JWT secret is set in production."""
        env = values.get("environment")
        if env == Environment.PRODUCTION and not v:
            raise ValueError("JWT_SECRET must be set in production environment")
        return v
    
    @validator("database_url")
    def validate_database_url(cls, v: Optional[str], values: Dict[str, Any]) -> Optional[str]:
        """Validate database URL is set in production."""
        env = values.get("environment")
        if env == Environment.PRODUCTION and not v:
            raise ValueError("DATABASE_URL must be set in production environment")
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == Environment.PRODUCTION
    
    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == Environment.DEVELOPMENT
    
    @property
    def is_test(self) -> bool:
        """Check if running in test."""
        return self.environment == Environment.TEST
    
    def get_database_url(self, masked: bool = False) -> str:
        """
        Get database URL with optional masking.
        
        Args:
            masked: Whether to mask sensitive parts
            
        Returns:
            Database URL
        """
        if not self.database_url:
            return ""
        
        if masked and self.is_production:
            # Mask password in production
            from urllib.parse import urlparse, urlunparse
            parsed = urlparse(self.database_url)
            if parsed.password:
                masked_password = f"{parsed.password[:2]}{'*' * 6}"
                netloc = f"{parsed.username}:{masked_password}@{parsed.hostname}"
                if parsed.port:
                    netloc += f":{parsed.port}"
                return urlunparse((
                    parsed.scheme,
                    netloc,
                    parsed.path,
                    parsed.params,
                    parsed.query,
                    parsed.fragment
                ))
        
        return self.database_url or ""
    
    def get_redis_url(self, masked: bool = False) -> str:
        """Get Redis URL with optional masking."""
        if not self.redis_url:
            return ""
        
        if masked and self.is_production:
            # Mask password if present
            from urllib.parse import urlparse, urlunparse
            parsed = urlparse(self.redis_url)
            if parsed.password:
                masked_password = f"{parsed.password[:2]}{'*' * 6}"
                netloc = f"{parsed.username}:{masked_password}@{parsed.hostname}"
                if parsed.port:
                    netloc += f":{parsed.port}"
                return urlunparse((
                    parsed.scheme,
                    netloc,
                    parsed.path,
                    parsed.params,
                    parsed.query,
                    parsed.fragment
                ))
        
        return self.redis_url or ""
    
    def dict_safe(self) -> Dict[str, Any]:
        """
        Get settings as dictionary with secrets masked.
        
        Returns:
            Settings dict with sensitive values replaced
        """
        data = self.dict()
        
        # Mask sensitive fields
        sensitive_fields = [
            "jwt_secret",
            "supabase_anon_key",
            "supabase_service_role_key",
            "openai_api_key",
            "elevenlabs_api_key",
        ]
        
        for field in sensitive_fields:
            if field in data and data[field]:
                data[field] = "***configured***"
        
        # Mask URLs
        if data.get("database_url"):
            data["database_url"] = self.get_database_url(masked=True)
        
        if data.get("redis_url"):
            data["redis_url"] = self.get_redis_url(masked=True)
        
        return data


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Returns:
        Settings instance
    """
    return Settings()


# Global settings instance
settings = get_settings()