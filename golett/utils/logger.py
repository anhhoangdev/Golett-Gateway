import logging
import os
import sys
from typing import Optional

# Set up logging configuration
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"

# Create a dictionary to store loggers to avoid creating multiple loggers for the same name
_loggers = {}

def get_logger(name: str, log_level: Optional[int] = None) -> logging.Logger:
    """
    Get a logger with the specified name and log level.
    
    Args:
        name: The name of the logger
        log_level: The log level to use, defaults to DEFAULT_LOG_LEVEL if not specified
        
    Returns:
        A configured logger instance
    """
    global _loggers
    
    if name in _loggers:
        return _loggers[name]
    
    logger = logging.getLogger(name)
    
    # Set log level from environment variable or default
    if log_level is None:
        env_log_level = os.environ.get("GOLETT_LOG_LEVEL", "").upper()
        if env_log_level == "DEBUG":
            log_level = logging.DEBUG
        elif env_log_level == "INFO":
            log_level = logging.INFO
        elif env_log_level == "WARNING":
            log_level = logging.WARNING
        elif env_log_level == "ERROR":
            log_level = logging.ERROR
        else:
            log_level = DEFAULT_LOG_LEVEL
    
    logger.setLevel(log_level)
    
    # Create console handler if no handlers exist
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)
        formatter = logging.Formatter(DEFAULT_LOG_FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    # Prevent propagation to the root logger
    logger.propagate = False
    
    # Store logger in cache
    _loggers[name] = logger
    
    return logger

def setup_file_logging(log_file: str, log_level: Optional[int] = None) -> None:
    """
    Set up file logging for all loggers.
    
    Args:
        log_file: Path to the log file
        log_level: Log level for the file handler
    """
    if log_level is None:
        log_level = DEFAULT_LOG_LEVEL
        
    # Create directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    formatter = logging.Formatter(DEFAULT_LOG_FORMAT)
    file_handler.setFormatter(formatter)
    
    # Add the file handler to the root logger to affect all loggers
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler) 