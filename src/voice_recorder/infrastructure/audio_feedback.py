"""
Audio feedback infrastructure implementations.
"""

import sys


class SystemAudioFeedback:
    """System-based audio feedback implementation."""

    def __init__(self):
        self.platform = sys.platform

    def play_start_beep(self) -> None:
        """Play start recording beep."""
        try:
            # Simple system beep
            print("\a", end="", flush=True)
        except Exception as e:
            print(f"Start beep failed: {e}")

    def play_stop_beep(self) -> None:
        """Play stop recording beep."""
        try:
            # Simple system beep
            print("\a", end="", flush=True)
        except Exception as e:
            print(f"Stop beep failed: {e}")


class MockAudioFeedback:
    """Mock audio feedback for testing."""

    def __init__(self):
        self.start_beep_count = 0
        self.stop_beep_count = 0

    def play_start_beep(self) -> None:
        """Mock start beep."""
        self.start_beep_count += 1
        print("Mock start beep")

    def play_stop_beep(self) -> None:
        """Mock stop beep."""
        self.stop_beep_count += 1
        print("Mock stop beep")

    def get_beep_counts(self):
        """Get beep counts for testing."""
        return {"start": self.start_beep_count, "stop": self.stop_beep_count}
