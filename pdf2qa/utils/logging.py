"""
Logging utilities for the pdf2qa library.
"""

import logging
import sys
from typing import Optional


def setup_logging(verbose: bool = False) -> logging.Logger:
    """
    Set up logging for the pdf2qa library.
    
    Args:
        verbose: Whether to enable verbose logging.
        
    Returns:
        Logger instance.
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Create logger
    logger = logging.getLogger("pdf2qa")
    logger.setLevel(log_level)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Add formatter to console handler
    console_handler.setFormatter(formatter)
    
    # Add console handler to logger
    logger.addHandler(console_handler)
    
    return logger


def get_logger() -> logging.Logger:
    """
    Get the pdf2qa logger.
    
    Returns:
        Logger instance.
    """
    return logging.getLogger("pdf2qa")
