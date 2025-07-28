"""
Rich console implementation for the voice recorder application.
"""

from rich.console import Console as RichConsole
from rich.panel import Panel
from rich.text import Text

from ..domain.interfaces import ConsoleInterface


class RichConsoleAdapter(ConsoleInterface):
    """Rich console adapter implementing ConsoleInterface."""
    
    def __init__(self, console: RichConsole | None = None):
        """Initialize with optional Rich console instance."""
        self.console = console or RichConsole()
    
    def print(self, *args, **kwargs) -> None:
        """Print to console using Rich."""
        self.console.print(*args, **kwargs)
    
    def print_panel(self, text: str, title: str = "", style: str = "default") -> None:
        """Print a formatted panel."""
        rich_text = Text(text)
        panel = Panel(
            rich_text,
            title=title,
            border_style=style,
            padding=(0, 1)
        )
        self.console.print(panel)
    
    def print_error(self, message: str) -> None:
        """Print error message."""
        error_text = Text()
        error_text.append(f"❌ {message}", style="bold red")
        
        error_panel = Panel(
            error_text,
            title="[bold red]Error[/bold red]",
            border_style="red",
            padding=(0, 1)
        )
        self.console.print(error_panel)
    
    def print_success(self, message: str) -> None:
        """Print success message."""
        success_text = Text()
        success_text.append(f"✅ {message}", style="bold green")
        
        success_panel = Panel(
            success_text,
            title="[bold green]Success[/bold green]",
            border_style="green",
            padding=(0, 1)
        )
        self.console.print(success_panel)
    
    def print_warning(self, message: str) -> None:
        """Print warning message."""
        warning_text = Text()
        warning_text.append(f"⚠️ {message}", style="bold yellow")
        
        warning_panel = Panel(
            warning_text,
            title="[bold yellow]Warning[/bold yellow]",
            border_style="yellow",
            padding=(0, 1)
        )
        self.console.print(warning_panel) 