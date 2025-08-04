"""
Text pasting infrastructure implementations.
"""

import subprocess
from typing import Optional


from ..domain.interfaces import TextPasterInterface, ConsoleInterface


class MacOSTextPaster(TextPasterInterface):
    """macOS-specific text pasting implementation."""

    def __init__(self, console: ConsoleInterface | None = None):
        """Initialize macOS text paster."""
        self.console = console

    def paste_text(self, text: str) -> bool:
        """Paste text at the current cursor position."""
        try:
            # Copy text to clipboard
            process = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE, text=True)
            process.communicate(input=text)

            if process.returncode == 0:
                # Paste using AppleScript
                script = """
                tell application "System Events"
                    keystroke "v" using {command down}
                end tell
                """
                subprocess.run(["osascript", "-e", script], check=True)

                # Clear clipboard after successful paste
                self.clear_clipboard()

                if self.console:
                    self.console.info("Text pasted successfully")
                return True
            else:
                if self.console:
                    self.console.error("Failed to copy text to clipboard")
                return False
        except Exception as e:
            if self.console:
                self.console.error(f"Text pasting failed: {e}")
            return False

    def paste_at_mouse_position(self, text: str) -> bool:
        """Paste text at the current mouse position."""
        try:
            # Copy text to clipboard
            process = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE, text=True)
            process.communicate(input=text)

            if process.returncode == 0:
                # Click at mouse position and paste
                script = """
                tell application "System Events"
                    click at mouse location
                    keystroke "v" using {command down}
                end tell
                """
                subprocess.run(["osascript", "-e", script], check=True)

                # Clear clipboard after successful paste
                self.clear_clipboard()

                if self.console:
                    self.console.info("Text pasted at mouse position")
                return True
            else:
                if self.console:
                    self.console.error("Failed to copy text to clipboard")
                return False
        except Exception as e:
            if self.console:
                self.console.error(f"Paste at cursor failed: {e}")
            return False

    def paste_text_with_mouse_position(self, text: str) -> bool:
        """Paste text with mouse position handling."""
        try:
            # Copy text to clipboard
            process = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE, text=True)
            process.communicate(input=text)

            if process.returncode == 0:
                # Get mouse position and paste
                mouse_script = """
                tell application "System Events"
                    set mousePos to mouse location
                    return mousePos
                end tell
                """
                mouse_result = subprocess.run(
                    ["osascript", "-e", mouse_script],
                    capture_output=True,
                    text=True,
                    check=True,
                )

                # Parse mouse position
                mouse_pos = mouse_result.stdout.strip()
                if mouse_pos:
                    # Click at mouse position and paste
                    paste_script = """
                    tell application "System Events"
                        click at mouse location
                        keystroke "v" using {command down}
                    end tell
                    """
                    subprocess.run(["osascript", "-e", paste_script], check=True)

                    # Clear clipboard after successful paste
                    self.clear_clipboard()

                    if self.console:
                        self.console.info("Text pasted at mouse position")
                    return True
                else:
                    # Fallback to regular paste
                    fallback_script = """
                    tell application "System Events"
                        keystroke "v" using {command down}
                    end tell
                    """
                    subprocess.run(["osascript", "-e", fallback_script], check=True)

                    # Clear clipboard after successful paste
                    self.clear_clipboard()

                    if self.console:
                        self.console.info("Text pasted successfully")
                    return True
            else:
                if self.console:
                    self.console.error("Failed to copy text to clipboard")
                return False
        except Exception as e:
            if self.console:
                self.console.error(f"Paste with mouse position failed: {e}")
            return False

    def paste_text_with_position(
        self, text: str, position: Optional[str] = None
    ) -> bool:
        """Paste text at specified position."""
        if position == "mouse":
            return self.paste_at_mouse_position(text)
        else:
            return self.paste_text(text)

    def clear_clipboard(self) -> bool:
        """Clear the clipboard contents."""
        try:
            # Clear clipboard by setting it to empty string
            process = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE, text=True)
            process.communicate(input="")

            if process.returncode == 0:
                if self.console:
                    self.console.debug("Clipboard cleared successfully")
                return True
            else:
                if self.console:
                    self.console.error("Failed to clear clipboard")
                return False
        except Exception as e:
            if self.console:
                self.console.error(f"Clipboard clearing failed: {e}")
            return False
