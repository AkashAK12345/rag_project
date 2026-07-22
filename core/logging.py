import logging
import sys

# Configure the root logger once for the application
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)

def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger instance for the given module name.
    Ensures all logging throughout the application is consistent.
    """
    return logging.getLogger(name)
