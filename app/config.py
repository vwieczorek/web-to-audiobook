from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # FastAPI settings
    port: int = 8142
    host: str = "0.0.0.0"
    
    # Logging settings
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    # Validation
    @validator("port")
    def port_must_be_valid(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v
    
    @validator("log_level")
    def log_level_must_be_valid(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v
    
    class Config:
        """Pydantic configuration."""
        env_prefix = "APP_"  # Environment variables will be prefixed with APP_
        case_sensitive = True