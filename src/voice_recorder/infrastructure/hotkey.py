"""
Hotkey listening infrastructure implementations.
"""

from typing import Any, Callable

from ..domain.interfaces import HotkeyListenerInterface, ConsoleInterface


class PynputHotkeyListener(HotkeyListenerInterface):
    """Pynput-based hotkey listener implementation."""

    def __init__(self, console: ConsoleInterface | None = None):
        """Initialize Pynput hotkey listener."""
        self.console = console
        self.keyboard = None
        self.listener = None
        self.on_press_callback = None
        self.on_release_callback = None
        self.on_enhanced_press_callback = None
        self.on_enhanced_release_callback = None

        # Track currently pressed keys
        self.pressed_keys = set()

        try:
            from pynput import keyboard

            self.keyboard = keyboard

            if self.console:
                self.console.info("Pynput keyboard listener initialized")
        except ImportError:
            if self.console:
                self.console.error(
                    "Pynput library not available - Install with: pip install pynput"
                )
            raise RuntimeError("Pynput library not available")
        except Exception as e:
            if self.console:
                self.console.error(f"Pynput initialization failed: {e}")
            raise RuntimeError(f"Pynput initialization failed: {e}")

    def start_listening(self) -> None:
        """Start listening for hotkey events."""
        try:
            # Check for macOS accessibility permissions
            if hasattr(self, "_check_macos_permissions"):
                self._check_macos_permissions()

            self.listener = self.keyboard.Listener(
                on_press=self._on_press, on_release=self._on_release
            )
            self.listener.start()

            if self.console:
                self.console.info("Hotkey listener started")
                self.console.info(
                    "If hotkeys don't work, check macOS Accessibility permissions"
                )
        except Exception as e:
            if self.console:
                self.console.error(f"Failed to start hotkey listener: {e}")
                self.console.error(
                    "This might be due to macOS accessibility permissions"
                )
                self.console.error(
                    "Go to System Preferences > Security & Privacy > Accessibility"
                )
                self.console.error("Add your terminal/IDE to the list of allowed apps")
            raise

    def stop_listening(self) -> None:
        """Stop listening for hotkey events."""
        if self.listener:
            self.listener.stop()
            self.listener = None

            if self.console:
                self.console.warning("Hotkey listener stopped")

    def _on_press(self, key):
        """Handle key press events."""
        try:
            # Add key to pressed keys set
            key_str = self._key_to_string(key)
            self.pressed_keys.add(key_str)

            if self.console:
                self.console.debug(
                    f"Key press detected: {key} (pressed keys: {self.pressed_keys})"
                )

            # Check for enhanced transcription combination
            if self._is_enhanced_combination(key):
                if self.on_enhanced_press_callback:
                    self.on_enhanced_press_callback(key)
                else:
                    if self.console:
                        self.console.warning("No enhanced on_press callback set")
            # Check for regular transcription
            elif self.on_press_callback:
                self.on_press_callback(key)
            else:
                if self.console:
                    self.console.warning("No on_press callback set")
        except Exception as e:
            if self.console:
                self.console.error(f"Key press handler error: {e}")

    def _on_release(self, key):
        """Handle key release events."""
        try:
            # Remove key from pressed keys set
            key_str = self._key_to_string(key)
            self.pressed_keys.discard(key_str)

            if self.console:
                self.console.debug(
                    f"Key release detected: {key} (pressed keys: {self.pressed_keys})"
                )

            # Check for enhanced transcription combination
            if self._is_enhanced_combination(key):
                if self.on_enhanced_release_callback:
                    self.on_enhanced_release_callback(key)
            # Check for regular transcription
            elif self.on_release_callback:
                self.on_release_callback(key)
        except Exception as e:
            if self.console:
                self.console.error(f"Key release handler error: {e}")

    def _key_to_string(self, key) -> str:
        """Convert key object to string representation."""
        if hasattr(key, "char") and key.char:
            return key.char.lower()
        elif hasattr(key, "name"):
            return key.name.lower()
        else:
            return str(key).lower()

    def set_enhanced_combination_checker(self, checker_func):
        """Set the function to check for enhanced combinations."""
        self._enhanced_combination_checker = checker_func

    def _is_enhanced_combination(self, key=None) -> bool:
        """Check if current key combination matches enhanced transcription hotkey."""
        if hasattr(self, "_enhanced_combination_checker"):
            return self._enhanced_combination_checker(key)
        return False

    def set_callbacks(
        self, on_press: Callable[[Any], None], on_release: Callable[[Any], None]
    ) -> None:
        """Set the callback functions for key events."""
        self.on_press_callback = on_press
        self.on_release_callback = on_release
        if self.console:
            self.console.info("Hotkey callbacks set successfully")

    def set_enhanced_callbacks(
        self, on_press: Callable[[Any], None], on_release: Callable[[Any], None]
    ) -> None:
        """Set the callback functions for enhanced transcription key events."""
        self.on_enhanced_press_callback = on_press
        self.on_enhanced_release_callback = on_release
        if self.console:
            self.console.info("Enhanced hotkey callbacks set successfully")
