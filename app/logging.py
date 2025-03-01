import json
import logging
import os
import sys
from datetime import datetime, UTC


class JsonFormatter(logging.Formatter):
    """Format logs as JSON for easier parsing."""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


def setup_logging(log_file, log_level):
    """Set up logging to both console and file with JSON formatting."""
    
    # Create log directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Configure console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JsonFormatter())
    root_logger.addHandler(console_handler)
    
    # Configure file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(JsonFormatter())
    root_logger.addHandler(file_handler)
    
    # Log the start of the application
    root_logger.debug(f"Logging initialized at level {log_level}")
    
    return root_logger
