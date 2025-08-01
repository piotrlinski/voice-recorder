"""
Base enhancement service class.

This module provides the foundation for all text enhancement service implementations.
"""

from abc import ABC, abstractmethod
from typing import Any

from voice_recorder.domain.interfaces import ConsoleInterface


class BaseEnhancementService(ABC):
    """Base class for all text enhancement services."""

    def __init__(self, config: Any, console: ConsoleInterface | None = None):
        """Initialize base enhancement service."""
        self.config = config
        self.console = console
        self._validate_config()
        self._initialize()

    @abstractmethod
    def _validate_config(self) -> None:
        """Validate service-specific configuration."""
        pass

    @abstractmethod
    def _initialize(self) -> None:
        """Initialize service-specific resources."""
        pass

    @abstractmethod
    def enhance_text(self, original_text: str) -> str:
        """Enhance the given text."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the service is available."""
        pass

    def _log_enhancement_start(self, provider_name: str) -> None:
        """Log the start of text enhancement."""
        if self.console:
            self.console.info(f"Enhancing text with {provider_name}...")

    def _log_enhancement_complete(self, provider_name: str) -> None:
        """Log the completion of text enhancement."""
        if self.console:
            self.console.info(f"{provider_name} text enhancement completed")

    def _log_enhancement_error(self, provider_name: str, error: Exception) -> None:
        """Log enhancement errors."""
        if self.console:
            self.console.error(f"{provider_name} text enhancement failed: {error}") 