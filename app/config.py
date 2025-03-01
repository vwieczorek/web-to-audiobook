from typing import Any, Optional
from pydantic import field_validator, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # FastAPI settings
    port: int = Field(default=8142, description="Port to run the server on")
    host: str = Field(default="0.0.0.0", description="Host to run the server on")
    
    # Logging settings
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: str = Field(default="logs/app.log", description="Log file path")
    
    # API Keys
    jina_api_key: Optional[SecretStr] = Field(None, description="Jina.ai API key for content extraction")
    
    # Validation
    @field_validator("port")
    @classmethod
    def port_must_be_valid(cls, v: Any) -> int:
        try:
            port_num = int(v)
        except (ValueError, TypeError):
            raise ValueError("Port must be a valid integer")
            
        if not 1 <= port_num <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return port_num
    
    @field_validator("log_level")
    @classmethod
    def log_level_must_be_valid(cls, v: str) -> str:
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()
    
    # Configure environment variable settings
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        case_sensitive=False,  # Case-insensitive environment variables
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )