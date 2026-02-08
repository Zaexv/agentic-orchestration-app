"""Production configuration settings."""

from typing import List
from pydantic import Field
from app.config.settings import Settings


class ProductionSettings(Settings):
    """
    Production-specific settings with enhanced security and performance.
    
    Usage:
        Set ENVIRONMENT=production in your .env file to use these settings.
    """
    
    # Environment
    environment: str = Field(default="production", description="Deployment environment")
    
    # Security
    cors_origins: List[str] = Field(
        default=["https://yourdomain.com"],
        description="Allowed CORS origins for production"
    )
    api_reload: bool = Field(default=False, description="Disable auto-reload in production")
    
    # Logging
    log_level: str = Field(default="INFO", description="Production log level")
    log_format: str = Field(default="json", description="Use JSON logging for production")
    
    # Performance
    database_pool_size: int = Field(default=20, description="Database connection pool size")
    database_max_overflow: int = Field(default=10, description="Max connections beyond pool size")
    
    # Rate Limiting (to be implemented)
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_per_minute: int = Field(default=60, description="Max requests per minute per user")
    
    # Monitoring
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")
    enable_tracing: bool = Field(default=True, description="Enable request tracing")
    
    # Security Headers
    enable_security_headers: bool = Field(default=True, description="Enable security headers")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


def get_production_settings() -> ProductionSettings:
    """Get production settings instance."""
    return ProductionSettings()
