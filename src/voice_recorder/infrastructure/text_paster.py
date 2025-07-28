"""
Text paster infrastructure implementations.
"""

import subprocess
import sys
from typing import Optional


class MacOSTextPaster:
    """macOS-specific text paster using clipboard and AppleScript."""

    def __init__(self):
        self.platform = sys.platform
        if not self.platform.startswith("darwin"):
            raise RuntimeError("MacOSTextPaster only works on macOS")

    def paste_text(self, text: str, position: Optional[str] = None) -> bool:
        """Paste text at the current cursor position or specified position."""
        try:
            # Copy text to clipboard
            self._copy_to_clipboard(text)
            # Paste at cursor position
            if position == "mouse":
                return self._paste_at_mouse_position()
            else:
                return self._paste_at_cursor_position()
        except Exception as e:
            print(f"Text pasting failed: {e}")
            return False

    def _copy_to_clipboard(self, text: str) -> None:
        """Copy text to macOS clipboard."""
        process = subprocess.Popen(
            "pbcopy", env={"LANG": "en_US.UTF-8"}, stdin=subprocess.PIPE
        )
        process.communicate(text.encode("utf-8"))

    def _paste_at_cursor_position(self) -> bool:
        """Paste at the current text cursor position."""
        try:
            # Use AppleScript to paste at cursor
            applescript = """
tell application "System Events"
    key code 9 using command down
end tell
"""
            subprocess.run(["osascript", "-e", applescript], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Paste at cursor failed: {e}")
            return False

    def _paste_at_mouse_position(self) -> bool:
        """Paste at the current mouse position."""
        try:
            # Get mouse position and click there, then paste
            applescript = """
tell application "System Events"
    set mouseLocation to mouse location
    click at mouseLocation
    delay 0.1
    key code 9 using command down
end tell
"""
            subprocess.run(["osascript", "-e", applescript], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Paste at mouse position failed: {e}")
            # Fall back to cursor position
            return self._paste_at_cursor_position()


class MockTextPaster:
    """Mock text paster for testing."""

    def __init__(self):
        self.pasted_texts = []

    def paste_text(self, text: str, position: Optional[str] = None) -> bool:
        """Mock paste text."""
        self.pasted_texts.append({"text": text, "position": position})
        print(f"Mock pasted: {text} at {position or 'cursor'}")
        return True

    def get_pasted_texts(self):
        """Get list of pasted texts for testing."""
        return self.pasted_texts
