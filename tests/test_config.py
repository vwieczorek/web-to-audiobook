import os
import pytest
from pydantic_core import ValidationError

# Import the Config class from app
from app.config import Settings


def test_settings_default_values():
    """Test that default values are set correctly when environment variables are not provided."""
    # Clear environment variables that might be set
    for env_var in ["APP_PORT", "APP_HOST", "APP_LOG_LEVEL", "APP_LOG_FILE"]:
        if env_var in os.environ:
            del os.environ[env_var]

    settings = Settings()
    assert settings.port == 8142  # As specified in the requirements
    assert settings.host == "0.0.0.0"
    assert settings.log_level == "INFO"
    assert settings.log_file == "logs/app.log"


def test_settings_from_environment():
    """Test that settings are loaded from environment variables when provided."""
    # Set environment variables with APP_ prefix
    os.environ["APP_PORT"] = "9000"
    os.environ["APP_HOST"] = "127.0.0.1"
    os.environ["APP_LOG_LEVEL"] = "DEBUG"
    os.environ["APP_LOG_FILE"] = "custom_logs/app.log"
    
    settings = Settings()
    assert settings.port == 9000
    assert settings.host == "127.0.0.1"
    assert settings.log_level == "DEBUG"
    assert settings.log_file == "custom_logs/app.log"

    # Clean up
    for env_var in ["APP_PORT", "APP_HOST", "APP_LOG_LEVEL", "APP_LOG_FILE"]:
        if env_var in os.environ:
            del os.environ[env_var]


def test_settings_validation():
    """Test that validation works correctly for settings."""
    os.environ["APP_PORT"] = "invalid_port"

    with pytest.raises(ValidationError):
        Settings()

    # Clean up
    if "APP_PORT" in os.environ:
        del os.environ["APP_PORT"]