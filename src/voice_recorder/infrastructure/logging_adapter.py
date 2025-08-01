"""
Logging adapter for the voice recorder application.
"""

import logging
from ..domain.interfaces import ConsoleInterface


class LoggingAdapter(ConsoleInterface):
    """Simple logging adapter that implements ConsoleInterface."""

    def __init__(self, logger_name: str = "voice_recorder"):
        """Initialize the logging adapter."""
        self.logger = logging.getLogger(logger_name)

        # Set up basic logging configuration if not already configured
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)

    def error(self, message: str) -> None:
        """Log error message."""
        self.logger.error(message)

    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)

    def debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)
