"""
No-op text processor.

Simple implementation that passes text through unchanged.
Useful when you only want transcription without text improvement.
"""

from voice_recorder.domain.interfaces import ConsoleInterface


class NoTextProcessor:
    """No-op text processor that passes text through unchanged.

    This is useful when you want to use the transcription service
    without any text improvement.
    """

    def __init__(self, console: ConsoleInterface | None = None):
        """Initialize no-op text processor.

        Args:
            console: Optional console for logging (unused)
        """
        self.console = console

    def process_text(self, text: str) -> str:
        """Return text unchanged.

        Args:
            text: Original text

        Returns:
            The same text, unchanged
        """
        return text

    def is_available(self) -> bool:
        """No-op processor is always available.

        Returns:
            True always
        """
        return True
