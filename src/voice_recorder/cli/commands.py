"""
CLI command handlers for Voice Recorder.
"""

import argparse
import sys

from .config_wizard import ConfigurationWizard
from ..infrastructure.config_manager import ConfigManager
from ..infrastructure.logging_adapter import LoggingAdapter
from ..api.app import VoiceRecorderApp


class CLICommands:
    """Handle CLI commands and argument parsing"""

    def __init__(self):
        self.console = LoggingAdapter()
        self.config_manager = ConfigManager()

    def create_parser(self) -> argparse.ArgumentParser:
        """Create the main argument parser"""
        parser = argparse.ArgumentParser(
            prog="voice-recorder",
            description="Voice Recorder - Professional speech-to-text recording for macOS",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  voice-recorder init              Initialize configuration
  voice-recorder                   Start recording (default)
  voice-recorder --help            Show this help message
            """,
        )

        # Subcommands
        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # Init command
        init_parser = subparsers.add_parser(
            "init", help="Initialize configuration with interactive wizard"
        )
        init_parser.add_argument(
            "--force",
            action="store_true",
            help="Force initialization even if config exists",
        )

        # Config command (for future use)
        config_parser = subparsers.add_parser("config", help="Configuration management")
        config_subparsers = config_parser.add_subparsers(dest="config_action")

        config_subparsers.add_parser("show", help="Show current configuration")
        config_subparsers.add_parser("path", help="Show configuration file path")
        config_subparsers.add_parser("reset", help="Reset to default configuration")

        # Version
        parser.add_argument(
            "--version", action="version", version="voice-recorder 1.0.0"
        )

        return parser

    def handle_command(self, args) -> int:
        """Handle the parsed command"""
        try:
            if args.command == "init":
                return self._handle_init(args)
            elif args.command == "config":
                return self._handle_config(args)
            else:
                # Default: start the recorder
                return self._handle_start(args)

        except KeyboardInterrupt:
            self.console.info("Operation cancelled by user")
            return 1
        except Exception as e:
            self.console.error(f"Error: {e}")
            return 1

    def _handle_init(self, args) -> int:
        """Handle init command"""
        # Check if config exists and force flag
        if self.config_manager.config_exists() and not args.force:
            self.console.error("Configuration already exists!")
            self.console.info(f"Location: {self.config_manager.get_config_path()}")
            self.console.info(
                "Use --force to overwrite or 'voice-recorder config show' to view"
            )
            return 1

        # Run configuration wizard
        wizard = ConfigurationWizard()
        wizard.run_wizard()

        return 0

    def _handle_config(self, args) -> int:
        """Handle config command"""
        if not args.config_action:
            self.console.error("Config command requires an action (show, path, reset)")
            return 1

        if args.config_action == "show":
            return self._show_config()
        elif args.config_action == "path":
            return self._show_config_path()
        elif args.config_action == "reset":
            return self._reset_config()
        else:
            self.console.error(f"Unknown config action: {args.config_action}")
            return 1

    def _handle_start(self, args) -> int:
        """Handle start command (default)"""
        # Check if configuration exists
        if not self.config_manager.config_exists():
            self.console.error("No configuration found!")
            self.console.info("Run 'voice-recorder init' to set up your configuration")
            return 1

        # Start the voice recorder application
        try:
            app = VoiceRecorderApp()
            app.start()
            return 0
        except Exception as e:
            self.console.error(f"Failed to start voice recorder: {e}")
            return 1

    def _show_config(self) -> int:
        """Show current configuration"""
        if not self.config_manager.config_exists():
            self.console.error("No configuration found!")
            self.console.info("Run 'voice-recorder init' to create one")
            return 1

        try:
            config = self.config_manager.load_config()

            print("🎤 Voice Recorder Configuration")
            print("=" * 50)
            print()
            print("📁 Configuration File:")
            print(f"   {self.config_manager.get_config_path()}")
            print()

            print("🗣️  Transcription:")
            print(f"   Mode: {config.transcription_config.mode.value}")
            print(f"   Model: {config.transcription_config.model_name}")
            if config.transcription_config.api_key:
                print("   API Key: ******* (set)")
            else:
                print("   API Key: Not set")
            print()

            print("⌨️  Hotkey:")
            print(f"   Key: {config.hotkey_config.key}")
            if config.hotkey_config.modifiers:
                print(f"   Modifiers: {', '.join(config.hotkey_config.modifiers)}")
            print(f"   Description: {config.hotkey_config.description}")
            print()

            print("🎙️  Audio:")
            print(f"   Sample Rate: {config.audio_config.sample_rate} Hz")
            print(f"   Channels: {config.audio_config.channels}")
            print(f"   Format: {config.audio_config.format.value}")
            print()

            print("⚙️  General:")
            print(f"   Auto-paste: {config.auto_paste}")
            print(f"   Temp Directory: {config.temp_directory}")
            print()

            return 0

        except Exception as e:
            self.console.error(f"Failed to load configuration: {e}")
            return 1

    def _show_config_path(self) -> int:
        """Show configuration file path"""
        print(self.config_manager.get_config_path())
        return 0

    def _reset_config(self) -> int:
        """Reset configuration to defaults"""
        if not self.config_manager.config_exists():
            self.console.error("No configuration found to reset!")
            return 1

        # Confirm reset
        print("⚠️  This will reset your configuration to defaults!")
        print(f"📁 {self.config_manager.get_config_path()}")
        print()
        response = input("Are you sure? (y/N): ").strip().lower()

        if response not in ["y", "yes"]:
            print("Reset cancelled.")
            return 0

        try:
            self.config_manager.reset_to_defaults()
            self.console.info("Configuration reset to defaults successfully!")
            return 0
        except Exception as e:
            self.console.error(f"Failed to reset configuration: {e}")
            return 1


def main():
    """Main CLI entry point"""
    cli = CLICommands()
    parser = cli.create_parser()
    args = parser.parse_args()

    return cli.handle_command(args)


if __name__ == "__main__":
    sys.exit(main())
