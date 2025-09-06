"""
Configuration Management

This module handles all application configuration including environment variables,
API keys, database settings, and feature flags.
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    
    All settings can be configured via environment variables with the prefix 'TRAVVY_'.
    For example: TRAVVY_ENVIRONMENT=production
    """
    
    # Application Settings
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    API_VERSION: str = "v1"
    PROJECT_NAME: str = "AI Trip Planner"
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    ALLOWED_HOSTS: str = "*"
    
    # Google Cloud Settings
    GCP_PROJECT_ID: str = ""
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_AI_API_KEY: str = ""
    
    # Database Settings
    FIRESTORE_DATABASE_ID: str = "ai-trip-planner"
    FIRESTORE_COLLECTION_PREFIX: str = ""
    
    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    
    # Celery Settings
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: List[str] = ["json"]
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_TIMEZONE: str = "UTC"
    
    # Security Settings
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_HOURS: int = 24
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # API Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    RATE_LIMIT_PER_DAY: int = 10000
    
    # AI Service Settings
    AI_MODEL_NAME: str = "gemini-1.5-pro"
    AI_TEMPERATURE: float = 0.7
    AI_MAX_OUTPUT_TOKENS: int = 4096
    AI_REQUEST_TIMEOUT: int = 30
    
    # External API Settings
    GOOGLE_MAPS_API_KEY: str = ""
    GOOGLE_PLACES_API_KEY: str = ""
    
    # File Upload Settings
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_FILE_TYPES: List[str] = ["jpg", "jpeg", "png", "webp", "mp3", "wav"]
    UPLOAD_FOLDER: str = "/tmp/uploads"
    
    # Monitoring and Logging
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    ENABLE_METRICS: bool = True
    
    # Feature Flags
    ENABLE_VOICE_INPUT: bool = True
    ENABLE_IMAGE_ANALYSIS: bool = True
    ENABLE_REAL_TIME_COLLABORATION: bool = True
    ENABLE_PUSH_NOTIFICATIONS: bool = False
    
    # Email Settings (for notifications)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[str] = None
    
    def get_allowed_origins(self) -> List[str]:
        """Parse ALLOWED_ORIGINS string to list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    def get_allowed_hosts(self) -> List[str]:
        """Parse ALLOWED_HOSTS string to list."""
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",")]
    
    class Config:
        env_prefix = "AI_TRIP_"
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings with caching.
    
    Returns:
        Settings: Application configuration instance
    """
    return Settings()


# Environment-specific configurations
class DevelopmentConfig(Settings):
    """Development environment configuration."""
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"


class ProductionConfig(Settings):
    """Production environment configuration."""
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"


class TestingConfig(Settings):
    """Testing environment configuration."""
    ENVIRONMENT: str = "testing"
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    REDIS_DB: int = 1  # Use different Redis DB for tests
