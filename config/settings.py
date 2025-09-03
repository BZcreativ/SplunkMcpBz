
"""
Configuration management for Splunk MCP Server
Consolidates all configuration settings in one place
"""

import os
from typing import Optional, Dict, Any
from pydantic import BaseSettings, Field
from functools import lru_cache

class SecuritySettings(BaseSettings):
    """Security configuration settings"""
    
    secret_key: str = Field(..., env="SECRET_KEY")
    token_expiry_hours: int = Field(default=24, env="TOKEN_EXPIRY_HOURS")
    max_requests_per_minute: int = Field(default=100, env="MAX_REQUESTS_PER_MINUTE")
    allowed_origins: str = Field(default="*", env="ALLOWED_ORIGINS")
    verify_ssl: bool = Field(default=False, env="VERIFY_SSL")
    
    # SSL Configuration
    ssl_keyfile: Optional[str] = Field(default=None, env="SSL_KEYFILE")
    ssl_certfile: Optional[str] = Field(default=None, env="SSL_CERTFILE")
    
    # User credentials (environment variables only)
    admin_username: str = Field(default="admin", env="ADMIN_USERNAME")
    admin_password: str = Field(..., env="ADMIN_PASSWORD")
    user_username: str = Field(default="user", env="USER_USERNAME")
    user_password: str = Field(..., env="USER_PASSWORD")
    readonly_username: str = Field(default="readonly", env="READONLY_USERNAME")
    readonly_password: str = Field(..., env="READONLY_PASSWORD")

class SplunkSettings(BaseSettings):
    """Splunk connection settings"""
    
    host: str = Field(default="localhost", env="SPLUNK_HOST")
    port: int = Field(default=8089, env="SPLUNK_PORT")
    scheme: str = Field(default="https", env="SPLUNK_SCHEME")
    token: str = Field(..., env="SPLUNK_TOKEN")
    username: Optional[str] = Field(default=None, env="SPLUNK_USERNAME")
    password: Optional[str] = Field(default=None, env="SPLUNK_PASSWORD")
    max_retries: int = Field(default=3, env="SPLUNK_MAX_RETRIES")
    timeout: int = Field(default=30, env="SPLUNK_TIMEOUT")

class RedisSettings(BaseSettings):
    """Redis configuration settings"""
    
    host: str = Field(default="localhost", env="REDIS_HOST")
    port: int = Field(default=6379, env="REDIS_PORT")
    db: int = Field(default=0, env="REDIS_DB")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    max_connections: int = Field(default=10, env="REDIS_MAX_CONNECTIONS")
    
    # Cache TTL settings (in seconds)
    query_cache_ttl: int = Field(default=300, env="REDIS_QUERY_CACHE_TTL")
    itsi_cache_ttl: int = Field(default=60, env="REDIS_ITSI_CACHE_TTL")
    session_cache_ttl: int = Field(default=3600, env="REDIS_SESSION_CACHE_TTL")

class ServerSettings(BaseSettings):
    """Server configuration settings"""
    
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8334, env="PORT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    debug: bool = Field(default=False, env="DEBUG")
    
    # MCP Server settings
    mcp_server_name: str = Field(default="SplunkMCP", env="MCP_SERVER_NAME")
    mcp_version: str = Field(default="1.0.0", env="MCP_VERSION")

class MonitoringSettings(BaseSettings):
    """Monitoring and metrics settings"""
    
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    enable_health_checks: bool = Field(default=True, env="ENABLE_HEALTH_CHECKS")
    health_check_interval: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")

class Settings(BaseSettings):
    """Main application settings"""
    
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    splunk: SplunkSettings = Field(default_factory=SplunkSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    server: ServerSettings = Field(default_factory=ServerSettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

def validate_required_settings():
    """Validate that all required settings are provided"""
    settings = get_settings()
    
    required_vars = [
        "SECRET_KEY",
        "ADMIN_PASSWORD",
        "USER_PASSWORD",
        "READONLY_PASSWORD",
        "SPLUNK_TOKEN"
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}"
        )
    
    return True

# Export settings for easy import
settings = get_settings()
   