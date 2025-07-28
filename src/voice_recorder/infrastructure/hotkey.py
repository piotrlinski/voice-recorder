"""
Hotkey listener infrastructure implementations.
"""

from typing import Any, Callable


class PynputHotkeyListener:
    """Pynput-based hotkey listener implementation."""

    def __init__(self):
        self.listener = None
        self.on_press_callback = None
        self.on_release_callback = None
        try:
            from pynput import keyboard

            self.keyboard = keyboard
            print("Pynput keyboard listener initialized")
        except ImportError:
            raise RuntimeError("Pynput library not available")
        except Exception as e:
            raise RuntimeError(f"Pynput initialization failed: {e}")

    def start_listening(
        self, on_press: Callable[[Any], None], on_release: Callable[[Any], None]
    ) -> None:
        """Start listening for hotkey events."""
        self.on_press_callback = on_press
        self.on_release_callback = on_release
        try:
            self.listener = self.keyboard.Listener(
                on_press=self._on_press, on_release=self._on_release
            )
            self.listener.start()
            print("Hotkey listener started")
        except Exception as e:
            print(f"Failed to start hotkey listener: {e}")
            raise

    def stop_listening(self) -> None:
        """Stop listening for hotkey events."""
        if self.listener:
            self.listener.stop()
            self.listener = None
            print("Hotkey listener stopped")

    def _on_press(self, key):
        """Internal key press handler."""
        if self.on_press_callback:
            try:
                self.on_press_callback(key)
            except Exception as e:
                print(f"Error in key press handler: {e}")

    def _on_release(self, key):
        """Internal key release handler."""
        if self.on_release_callback:
            try:
                self.on_release_callback(key)
            except Exception as e:
                print(f"Error in key release handler: {e}")


class MockHotkeyListener:
    """Mock hotkey listener for testing."""

    def __init__(self):
        self.is_listening = False
        self.on_press_callback = None
        self.on_release_callback = None

    def start_listening(
        self, on_press: Callable[[Any], None], on_release: Callable[[Any], None]
    ) -> None:
        """Start listening for hotkey events."""
        self.is_listening = True
        self.on_press_callback = on_press
        self.on_release_callback = on_release

    def stop_listening(self) -> None:
        """Stop listening for hotkey events."""
        self.is_listening = False

    def simulate_key_press(self, key):
        """Simulate a key press event."""
        if self.on_press_callback:
            self.on_press_callback(key)

    def simulate_key_release(self, key):
        """Simulate a key release event."""
        if self.on_release_callback:
            self.on_release_callback(key)



