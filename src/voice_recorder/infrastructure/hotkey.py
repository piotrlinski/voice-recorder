"""
Hotkey listener infrastructure implementations.
"""

import os
from typing import Any, Callable

from rich.console import Console
from rich.text import Text
from rich.panel import Panel


class PynputHotkeyListener:
    """Pynput-based hotkey listener implementation."""

    def __init__(self):
        self.console = Console()
        self.listener = None
        self.on_press_callback = None
        self.on_release_callback = None
        try:
            from pynput import keyboard

            self.keyboard = keyboard
            
            # Only show Rich output if not in test environment
            if not os.getenv('PYTEST_CURRENT_TEST'):
                init_text = Text()
                init_text.append("✅ Pynput keyboard listener initialized", style="bold green")
                
                init_panel = Panel(
                    init_text,
                    title="[bold green]Hotkey System Ready[/bold green]",
                    border_style="green",
                    padding=(0, 1)
                )
                self.console.print(init_panel)
        except ImportError:
            error_text = Text()
            error_text.append("❌ Pynput library not available", style="bold red")
            error_text.append("\n💡 Install with: pip install pynput", style="yellow")
            
            error_panel = Panel(
                error_text,
                title="[bold red]Hotkey System Error[/bold red]",
                border_style="red",
                padding=(0, 1)
            )
            self.console.print(error_panel)
            raise RuntimeError("Pynput library not available")
        except Exception as e:
            error_text = Text()
            error_text.append(f"❌ Pynput initialization failed: {e}", style="bold red")
            
            error_panel = Panel(
                error_text,
                title="[bold red]Hotkey System Error[/bold red]",
                border_style="red",
                padding=(0, 1)
            )
            self.console.print(error_panel)
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
            
            # Only show Rich output if not in test environment
            if not os.getenv('PYTEST_CURRENT_TEST'):
                start_text = Text()
                start_text.append("🎧 Hotkey listener started", style="bold green")
                
                start_panel = Panel(
                    start_text,
                    title="[bold green]Listening Active[/bold green]",
                    border_style="green",
                    padding=(0, 1)
                )
                self.console.print(start_panel)
        except Exception as e:
            error_text = Text()
            error_text.append(f"❌ Failed to start hotkey listener: {e}", style="bold red")
            
            error_panel = Panel(
                error_text,
                title="[bold red]Listener Error[/bold red]",
                border_style="red",
                padding=(0, 1)
            )
            self.console.print(error_panel)
            raise

    def stop_listening(self) -> None:
        """Stop listening for hotkey events."""
        if self.listener:
            self.listener.stop()
            self.listener = None
            
            # Only show Rich output if not in test environment
            if not os.getenv('PYTEST_CURRENT_TEST'):
                stop_text = Text()
                stop_text.append("🛑 Hotkey listener stopped", style="bold yellow")
                
                stop_panel = Panel(
                    stop_text,
                    title="[bold yellow]Listening Stopped[/bold yellow]",
                    border_style="yellow",
                    padding=(0, 1)
                )
                self.console.print(stop_panel)

    def _on_press(self, key):
        """Internal key press handler."""
        if self.on_press_callback:
            try:
                self.on_press_callback(key)
            except Exception as e:
                error_text = Text()
                error_text.append(f"⚠️ Error in key press handler: {e}", style="bold yellow")
                
                error_panel = Panel(
                    error_text,
                    title="[bold yellow]Key Press Error[/bold yellow]",
                    border_style="yellow",
                    padding=(0, 1)
                )
                self.console.print(error_panel)

    def _on_release(self, key):
        """Internal key release handler."""
        if self.on_release_callback:
            try:
                self.on_release_callback(key)
            except Exception as e:
                error_text = Text()
                error_text.append(f"⚠️ Error in key release handler: {e}", style="bold yellow")
                
                error_panel = Panel(
                    error_text,
                    title="[bold yellow]Key Release Error[/bold yellow]",
                    border_style="yellow",
                    padding=(0, 1)
                )
                self.console.print(error_panel)






