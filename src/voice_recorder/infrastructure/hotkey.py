"""
Hotkey listening infrastructure implementations.
"""

import os
from typing import Any, Callable, Optional

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
        try:
            from pynput import keyboard

            self.keyboard = keyboard
            
            if self.console:
                self.console.print_success("✅ Pynput keyboard listener initialized")
        except ImportError:
            if self.console:
                self.console.print_error("Pynput library not available - Install with: pip install pynput")
            raise RuntimeError("Pynput library not available")
        except Exception as e:
            if self.console:
                self.console.print_error(f"Pynput initialization failed: {e}")
            raise RuntimeError(f"Pynput initialization failed: {e}")

    def start_listening(self) -> None:
        """Start listening for hotkey events."""
        try:
            self.listener = self.keyboard.Listener(
                on_press=self._on_press, on_release=self._on_release
            )
            self.listener.start()
            
            if self.console:
                self.console.print_success("🎧 Hotkey listener started")
        except Exception as e:
            if self.console:
                self.console.print_error(f"Failed to start hotkey listener: {e}")
            raise

    def stop_listening(self) -> None:
        """Stop listening for hotkey events."""
        if self.listener:
            self.listener.stop()
            self.listener = None
            
            if self.console:
                self.console.print_warning("🛑 Hotkey listener stopped")

    def _on_press(self, key):
        """Handle key press events."""
        try:
            if self.on_press_callback:
                self.on_press_callback(key)
        except Exception as e:
            if self.console:
                self.console.print_error(f"Key press handler error: {e}")

    def _on_release(self, key):
        """Handle key release events."""
        try:
            if self.on_release_callback:
                self.on_release_callback(key)
        except Exception as e:
            if self.console:
                self.console.print_error(f"Key release handler error: {e}")

    def set_callbacks(self, on_press: Callable[[Any], None], on_release: Callable[[Any], None]) -> None:
        """Set the callback functions for key events."""
        self.on_press_callback = on_press
        self.on_release_callback = on_release






