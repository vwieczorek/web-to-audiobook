"""Pytest configuration file."""
import os
import pytest


# Configure pytest-asyncio
pytest_plugins = ["pytest_asyncio"]


@pytest.fixture(autouse=True)
def env_setup():
    """
    Set up environment variables for testing.
    This fixture is applied to all tests automatically.
    """
    # Store original environment variables
    original_env = os.environ.copy()
    
    yield
    
    # Restore original environment variables
    os.environ.clear()
    os.environ.update(original_env)