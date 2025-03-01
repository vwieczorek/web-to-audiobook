"""Pytest configuration file."""
import os
import logging
import tempfile
from pathlib import Path
import pytest
from unittest.mock import MagicMock


# Try to configure pytest-asyncio if available
try:
    import pytest_asyncio
    pytest_plugins = ["pytest_asyncio"]
except ImportError:
    # pytest-asyncio not installed, we'll handle async tests differently
    pass


@pytest.fixture(autouse=True)
def env_setup():
    """
    Set up environment variables for testing.
    This fixture is applied to all tests automatically.
    """
    # Store original environment variables
    original_env = os.environ.copy()
    
    # Set test environment variables
    os.environ["ENVIRONMENT"] = "test"
    
    yield
    
    # Restore original environment variables
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_logger():
    """Return a mock logger for testing."""
    return MagicMock(spec=logging.Logger)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def mock_http_client():
    """Return a mock HTTP client for testing."""
    mock_client = MagicMock()
    mock_client.request = MagicMock()
    return mock_client
