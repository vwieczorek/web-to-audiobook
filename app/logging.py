import json
import logging
import logging.handlers
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


class JsonFormatter(logging.Formatter):
    """Format logs as JSON for easier parsing."""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        # Add extra fields if they exist
        if hasattr(record, 'extra') and record.extra:
            log_data.update(record.extra)
        
        return json.dumps(log_data)


def setup_logging(log_file, log_level, max_bytes=10485760, backup_count=5):
    """
    Set up logging to both console and file with JSON formatting and rotation.
    
    Args:
        log_file: Path to the log file
        log_level: Logging level (DEBUG, INFO, etc.)
        max_bytes: Maximum size of log file before rotation (default: 10MB)
        backup_count: Number of backup files to keep (default: 5)
        
    Returns:
        Logger: Root logger configured for the application
    """
    
    # Create log directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
    
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
    
    # Configure rotating file handler
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8"
    )
    file_handler.setFormatter(JsonFormatter())
    root_logger.addHandler(file_handler)
    
    # Log the start of the application
    root_logger.debug(f"Logging initialized at level {log_level}")
    
    return root_logger


# Add a method to create a logger with extra context
def get_logger(name, **extra):
    """
    Get a logger with extra context that will be included in all log messages.
    
    Args:
        name: Logger name
        **extra: Extra context to include in all log messages
        
    Returns:
        Logger: Configured logger with context
    """
    logger = logging.getLogger(name)
    
    # Add a filter to include extra context
    class ContextFilter(logging.Filter):
        def filter(self, record):
            record.extra = extra
            return True
    
    # Remove existing filters and add our context filter
    for f in logger.filters:
        logger.removeFilter(f)
    logger.addFilter(ContextFilter())
    
    return logger
