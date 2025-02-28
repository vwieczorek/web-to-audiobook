import json
import logging
import os
import tempfile

import pytest

from app.logging import setup_logging


@pytest.fixture
def temp_log_file():
    """Create a temporary log file for testing."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        yield tmp.name
    # Cleanup
    if os.path.exists(tmp.name):
        os.remove(tmp.name)


def test_setup_logging_creates_log_file(temp_log_file):
    """Test that setup_logging creates the log file if it doesn't exist."""
    # The temp file exists, so delete it to test creation
    os.remove(temp_log_file)
    
    setup_logging(log_file=temp_log_file, log_level="INFO")
    
    assert os.path.exists(temp_log_file)


def test_setup_logging_json_format(temp_log_file):
    """Test that logs are written in JSON format."""
    setup_logging(log_file=temp_log_file, log_level="INFO")
    
    logger = logging.getLogger("test_logger")
    test_message = "Test message"
    logger.info(test_message)
    
    with open(temp_log_file, 'r') as f:
        log_line = f.readline()
        log_data = json.loads(log_line)
        
        assert log_data["message"] == test_message
        assert log_data["level"] == "INFO"
        assert "timestamp" in log_data


def test_setup_logging_log_level(temp_log_file):
    """Test that the log level is set correctly."""
    setup_logging(log_file=temp_log_file, log_level="WARNING")
    
    logger = logging.getLogger("test_logger")
    
    # This should not be logged as it's below the WARNING level
    logger.info("This should not be logged")
    
    # This should be logged
    test_message = "This should be logged"
    logger.warning(test_message)
    
    with open(temp_log_file, 'r') as f:
        log_lines = f.readlines()
        
        assert len(log_lines) == 1
        log_data = json.loads(log_lines[0])
        assert log_data["message"] == test_message
        assert log_data["level"] == "WARNING"