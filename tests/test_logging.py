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
        log_lines = f.readlines()
        
        # Find the line with our test message
        test_log_data = None
        for line in log_lines:
            data = json.loads(line)
            if data.get("name") == "test_logger":
                test_log_data = data
                break
        
        assert test_log_data is not None, "Test logger message not found in log file"
        assert test_log_data["message"] == test_message
        assert test_log_data["level"] == "INFO"
        assert "timestamp" in test_log_data


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
        
        # Should have at least one log entry (there might be an initialization message)
        assert len(log_lines) >= 1
        
        # Find the warning message from our test logger
        warning_found = False
        info_found = False
        
        for line in log_lines:
            data = json.loads(line)
            if data.get("name") == "test_logger":
                if data.get("level") == "WARNING" and data.get("message") == test_message:
                    warning_found = True
                if data.get("level") == "INFO" and data.get("message") == "This should not be logged":
                    info_found = True
        
        assert warning_found, "Warning message not found in logs"
        assert not info_found, "Info message should not have been logged"