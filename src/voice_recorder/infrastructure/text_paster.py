"""
Text paster infrastructure implementations.
"""

import os
import subprocess
from typing import Optional

from rich.console import Console
from rich.text import Text
from rich.panel import Panel


class MacOSTextPaster:
    """macOS-specific text paster implementation."""

    def __init__(self):
        self.console = Console()

    def paste_text(self, text: str) -> bool:
        """Paste text at the current cursor position."""
        try:
            # Copy text to clipboard
            process = subprocess.Popen(
                ["pbcopy"], stdin=subprocess.PIPE, text=True
            )
            process.communicate(input=text)
            
            if process.returncode == 0:
                # Paste using AppleScript
                script = f'''
                tell application "System Events"
                    keystroke "v" using {{command down}}
                end tell
                '''
                subprocess.run(["osascript", "-e", script], check=True)
                
                # Only show Rich output if not in test environment
                if not os.getenv('PYTEST_CURRENT_TEST'):
                    paste_text = Text()
                    paste_text.append("📋 Text pasted successfully", style="bold green")
                    
                    paste_panel = Panel(
                        paste_text,
                        title="[bold green]Paste Success[/bold green]",
                        border_style="green",
                        padding=(0, 1)
                    )
                    self.console.print(paste_panel)
                return True
            else:
                error_text = Text()
                error_text.append("❌ Failed to copy text to clipboard", style="bold red")
                
                error_panel = Panel(
                    error_text,
                    title="[bold red]Copy Error[/bold red]",
                    border_style="red",
                    padding=(0, 1)
                )
                self.console.print(error_panel)
                return False
        except Exception as e:
            error_text = Text()
            error_text.append(f"❌ Text pasting failed: {e}", style="bold red")
            
            error_panel = Panel(
                error_text,
                title="[bold red]Paste Error[/bold red]",
                border_style="red",
                padding=(0, 1)
            )
            self.console.print(error_panel)
            return False

    def paste_at_mouse_position(self, text: str) -> bool:
        """Paste text at the current mouse position."""
        try:
            # Copy text to clipboard
            process = subprocess.Popen(
                ["pbcopy"], stdin=subprocess.PIPE, text=True
            )
            process.communicate(input=text)
            
            if process.returncode == 0:
                # Click at mouse position and paste
                script = f'''
                tell application "System Events"
                    click at mouse location
                    keystroke "v" using {{command down}}
                end tell
                '''
                subprocess.run(["osascript", "-e", script], check=True)
                
                # Only show Rich output if not in test environment
                if not os.getenv('PYTEST_CURRENT_TEST'):
                    paste_text = Text()
                    paste_text.append("📋 Text pasted at mouse position", style="bold green")
                    
                    paste_panel = Panel(
                        paste_text,
                        title="[bold green]Paste Success[/bold green]",
                        border_style="green",
                        padding=(0, 1)
                    )
                    self.console.print(paste_panel)
                return True
            else:
                error_text = Text()
                error_text.append("❌ Failed to copy text to clipboard", style="bold red")
                
                error_panel = Panel(
                    error_text,
                    title="[bold red]Copy Error[/bold red]",
                    border_style="red",
                    padding=(0, 1)
                )
                self.console.print(error_panel)
                return False
        except Exception as e:
            error_text = Text()
            error_text.append(f"❌ Paste at cursor failed: {e}", style="bold red")
            
            error_panel = Panel(
                error_text,
                title="[bold red]Paste Error[/bold red]",
                border_style="red",
                padding=(0, 1)
            )
            self.console.print(error_panel)
            return False

    def paste_text_with_mouse_position(self, text: str) -> bool:
        """Paste text at the current mouse position."""
        try:
            # Copy text to clipboard
            process = subprocess.Popen(
                ["pbcopy"], stdin=subprocess.PIPE, text=True
            )
            process.communicate(input=text)
            
            if process.returncode == 0:
                # Click at mouse position and paste
                script = f'''
                tell application "System Events"
                    click at mouse location
                    keystroke "v" using {{command down}}
                end tell
                '''
                subprocess.run(["osascript", "-e", script], check=True)
                
                # Only show Rich output if not in test environment
                if not os.getenv('PYTEST_CURRENT_TEST'):
                    paste_text = Text()
                    paste_text.append("📋 Text pasted at mouse position", style="bold green")
                    
                    paste_panel = Panel(
                        paste_text,
                        title="[bold green]Paste Success[/bold green]",
                        border_style="green",
                        padding=(0, 1)
                    )
                    self.console.print(paste_panel)
                return True
            else:
                error_text = Text()
                error_text.append("❌ Failed to copy text to clipboard", style="bold red")
                
                error_panel = Panel(
                    error_text,
                    title="[bold red]Copy Error[/bold red]",
                    border_style="red",
                    padding=(0, 1)
                )
                self.console.print(error_panel)
                return False
        except Exception as e:
            error_text = Text()
            error_text.append(f"❌ Paste at mouse position failed: {e}", style="bold red")
            
            error_panel = Panel(
                error_text,
                title="[bold red]Paste Error[/bold red]",
                border_style="red",
                padding=(0, 1)
            )
            self.console.print(error_panel)
            return False



