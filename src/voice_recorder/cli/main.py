"""
Main CLI application for voice recorder.
"""

import os
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from ..api.app import VoiceRecorderApp
from ..infrastructure.config_manager import ConfigManager

# Create Typer app
app = typer.Typer(
    name="voice-recorder",
    help="Professional voice recording application with transcription",
    add_completion=False,
)

console = Console()


@app.command()
def start(
    config_file: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Path to configuration file"
    ),
    env_file: Optional[Path] = typer.Option(
        None, "--env-file", "-e", help="Path to custom .env file"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
):
    """Start the voice recorder application."""
    try:
        # Load configuration
        if config_file:
            config_manager = ConfigManager(str(config_file.parent))
        else:
            config_manager = ConfigManager()
        
        config = config_manager.load_config()
        
        if verbose:
            console.print(f"📁 Config file: {config_manager.get_config_path()}")
            console.print(f"🤖 Transcription mode: {config.transcription_config.mode.value}")
            console.print(f"🤖 Model: {config.transcription_config.model_name}")
            console.print(f"⌨️ Hotkey: {config.hotkey_config.key}")
            console.print(f"🔊 Sample rate: {config.audio_config.sample_rate}Hz")
        
        # Create and start application
        voice_app = VoiceRecorderApp(config, env_file=env_file)
        
        console.print(Panel.fit(
            Text("🎤 Voice Recorder Started", style="bold green"),
            title="Voice Recorder",
            border_style="green"
        ))
        console.print("Press Ctrl+C to stop the application")
        
        voice_app.start()
        
    except KeyboardInterrupt:
        console.print("\n🛑 Application stopped by user")
    except Exception as e:
        console.print(f"❌ Error starting application: {e}", style="bold red")
        sys.exit(1)


@app.command()
def init(
    config_dir: Optional[Path] = typer.Option(
        None, "--config-dir", "-d", help="Configuration directory"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing configuration"),
):
    """Initialize voice recorder configuration."""
    try:
        # Determine config directory
        if config_dir:
            config_manager = ConfigManager(str(config_dir))
        else:
            config_manager = ConfigManager()
        
        config_file = Path(config_manager.get_config_path())
        
        if config_file.exists() and not force:
            console.print(
                f"⚠️ Configuration already exists at {config_file}",
                style="yellow"
            )
            overwrite = typer.confirm("Do you want to overwrite it?")
            if not overwrite:
                console.print("Configuration initialization cancelled")
                return
        
        # Run interactive configuration
        from .config import run_configuration
        
        config = run_configuration(config_manager)
        
        console.print(Panel.fit(
            Text("✅ Configuration initialized successfully!", style="bold green"),
            title="Configuration Complete",
            border_style="green"
        ))
        
        console.print(f"📁 Config file: {config_file}")
        console.print(f"🤖 Transcription mode: {config.transcription_config.mode.value}")
        console.print(f"🤖 Model: {config.transcription_config.model_name}")
        console.print(f"⌨️ Hotkey: {config.hotkey_config.key}")
        console.print(f"🔊 Sample rate: {config.audio_config.sample_rate}Hz")
        console.print(f"📋 Auto-paste: {config.auto_paste}")
        console.print(f"🔔 Audio feedback: {config.beep_feedback}")
        console.print(f"📁 Temp directory: {config.temp_directory}")
        
    except Exception as e:
        console.print(f"❌ Error initializing configuration: {e}", style="bold red")
        sys.exit(1)


@app.command()
def config(
    show: bool = typer.Option(False, "--show", "-s", help="Show current configuration"),
    edit: bool = typer.Option(False, "--edit", "-e", help="Edit configuration interactively"),
    reset: bool = typer.Option(False, "--reset", "-r", help="Reset to default configuration"),
):
    """Manage voice recorder configuration."""
    try:
        config_manager = ConfigManager()
        
        if show:
            from .config import show_configuration
            show_configuration(config_manager)
        elif edit:
            from .config import run_configuration
            run_configuration(config_manager)
            console.print("✅ Configuration updated successfully!", style="bold green")
        elif reset:
            config = config_manager.reset_to_defaults()
            console.print("✅ Configuration reset to defaults!", style="bold green")
            console.print(f"📁 Config file: {config_manager.get_config_path()}")
        else:
            # Show help if no option specified
            console.print("Please specify an action: --show, --edit, or --reset")
            
    except Exception as e:
        console.print(f"❌ Error managing configuration: {e}", style="bold red")
        sys.exit(1)


@app.command()
def status():
    """Show application status and configuration."""
    try:
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        console.print(Panel.fit(
            Text("🎤 Voice Recorder Status", style="bold blue"),
            title="Status",
            border_style="blue"
        ))
        
        console.print(f"📁 Config file: {config_manager.get_config_path()}")
        console.print(f"🤖 Transcription mode: {config.transcription_config.mode.value}")
        console.print(f"🤖 Model: {config.transcription_config.model_name}")
        console.print(f"⌨️ Hotkey: {config.hotkey_config.key}")
        console.print(f"🔊 Sample rate: {config.audio_config.sample_rate}Hz")
        console.print(f"📋 Auto-paste: {config.auto_paste}")
        console.print(f"🔔 Sound feedback: {config.sound_config.enabled}")
        console.print(f"🎵 Sound type: {config.sound_config.sound_type.value}")
        console.print(f"🔊 Sound volume: {config.sound_config.volume:.2f}")
        console.print(f"📁 Temp directory: {config.temp_directory}")
        
        # Check if temp directory exists
        temp_dir = Path(config.temp_directory)
        if temp_dir.exists():
            console.print(f"✅ Temp directory exists: {temp_dir}")
        else:
            console.print(f"⚠️ Temp directory does not exist: {temp_dir}", style="yellow")
        
    except Exception as e:
        console.print(f"❌ Error getting status: {e}", style="bold red")
        sys.exit(1)


@app.command()
def purge(
    force: bool = typer.Option(False, "--force", "-f", help="Force deletion without confirmation"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show what would be deleted without actually deleting"),
):
    """Remove temporary voice files from the temp directory."""
    try:
        config_manager = ConfigManager()
        config = config_manager.load_config()
        temp_dir = Path(config.temp_directory)
        
        if not temp_dir.exists():
            console.print(f"⚠️ Temp directory does not exist: {temp_dir}", style="yellow")
            return
        
        # Find all temporary voice files
        voice_files = []
        for pattern in ["*.wav", "*.mp3", "*.flac", "*.m4a", "*.ogg"]:
            voice_files.extend(temp_dir.glob(pattern))
        
        if not voice_files:
            console.print("📁 No temporary voice files found to delete")
            return
        
        console.print(f"📁 Found {len(voice_files)} temporary voice files:")
        for file in voice_files:
            file_size = file.stat().st_size
            console.print(f"   📄 {file.name} ({file_size} bytes)")
        
        if dry_run:
            console.print(f"🔍 Dry run: Would delete {len(voice_files)} files")
            return
        
        if not force:
            console.print(f"⚠️ About to delete {len(voice_files)} temporary voice files")
            confirm = typer.confirm("Do you want to continue?")
            if not confirm:
                console.print("🗑️ Purge cancelled")
                return
        
        # Delete the files
        deleted_count = 0
        for file in voice_files:
            try:
                file.unlink()
                deleted_count += 1
                console.print(f"🗑️ Deleted: {file.name}")
            except Exception as e:
                console.print(f"❌ Error deleting {file.name}: {e}", style="red")
        
        console.print(Panel.fit(
            Text(f"✅ Successfully deleted {deleted_count} temporary voice files", style="bold green"),
            title="Purge Complete",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(f"❌ Error purging temporary files: {e}", style="bold red")
        sys.exit(1)


if __name__ == "__main__":
    app() 