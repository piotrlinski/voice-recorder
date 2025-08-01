# Voice Recorder Desktop Application

A professional voice recording desktop application for macOS with a modern Flow-style interface. Features real-time speech-to-text transcription using OpenAI's Whisper API, hotkey support, and beautiful animated UI.

## Features

🎤 **Modern Desktop GUI**: Beautiful Flow-style interface with smooth animations  
📝 **Real-time Transcription**: Instant speech-to-text with OpenAI Whisper  
⌨️ **Hotkey Support**: Hands-free recording with customizable hotkeys  
📊 **Live Statistics**: Track recordings, word counts, and success rates  
💾 **Export Options**: Save transcriptions as TXT or JSON files  
🎨 **Animated Interface**: Smooth hover effects and entrance animations  
🖱️ **Manual Controls**: Click-to-record button for direct control  
📋 **Copy to Clipboard**: Quick copy of transcribed text  
⚙️ **Settings Integration**: Easy configuration management  
🔄 **Session Management**: Track and view recording history

## Architecture

The application follows Clean Architecture principles with clear separation of concerns:

```
src/voice_recorder/
├── domain/           # Core business logic and models
├── services/         # Application business logic
├── infrastructure/   # External dependencies (adapters)
│   └── transcription/  # Transcription services module
├── gui/             # Desktop GUI application
│   ├── __init__.py
│   └── main_window.py  # Flow-style main window
└── api/             # Application entry points
```

### Design Patterns

- **Dependency Injection**: All components are injected via interfaces
- **Protocol/Interface Segregation**: Clear contracts between layers
- **Factory Pattern**: Application factory for dependency setup
- **Observer Pattern**: Hotkey event handling
- **Repository Pattern**: Session management

## Installation

### Prerequisites

- Python 3.11+
- macOS (for system integration features)
- OpenAI API key (for transcription)
- PyQt6 (automatically installed)

### Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd voice-recorder
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   ```

3. **Install the package:**
   ```bash
   # Install in development mode
   pip install -e .
   
   # Or install with all dependencies
   pip install -e ".[dev,test]"
   ```

4. **Install system dependencies:**
   ```bash
   # Install PortAudio (required for PyAudio)
   brew install portaudio
   
   # Install ffmpeg (required for local Whisper transcription)
   brew install ffmpeg
   ```

5. **Optional: Initialize configuration manually:**
   ```python
   from voice_recorder.infrastructure.config_manager import ConfigManager
   
   # Create default configuration
   config_manager = ConfigManager()
   config = config_manager.load_config()  # Creates default config if none exists
   ```

### Alternative Installation Methods

**Using pip directly:**
```bash
pip install voice-recorder
```

## Usage

### Command Line Interface

```bash
# Start voice recorder with CLI
voice-recorder

# Run configuration wizard
voice-recorder --config-wizard

# Start GUI application
voice-recorder-gui
```

### Hotkeys

- **Right Shift**: Start/stop basic transcription
- **Left Ctrl**: Start/stop enhanced transcription (with LLM improvement)
- **Ctrl+C**: Stop the application

### Configuration

The application uses a configuration file located at `~/.voicerecorder/config.ini`. You can:

1. **Run the configuration wizard:**
   ```bash
   voice-recorder --config-wizard
   ```

2. **Edit the configuration manually:**
   ```bash
   nano ~/.voicerecorder/config.ini
   ```

3. **Use example configurations:**
   ```bash
   cp examples/config_openai_whisper.ini ~/.voicerecorder/config.ini
   ```

## Documentation

Comprehensive documentation is available in the [`docs/`](./docs/) directory:

- **[Architecture Documentation](./docs/)** - Detailed architecture guides
- **[Troubleshooting](./docs/HOTKEY_TROUBLESHOOTING.md)** - Common issues and solutions
- **[Configuration Examples](./examples/)** - Sample configuration files

## Development

### Project Structure

```
voice-recorder/
├── docs/                          # Documentation
├── examples/                      # Configuration examples
├── src/voice_recorder/           # Source code
│   ├── api/                      # Application entry points
│   ├── cli/                      # Command-line interface
│   ├── domain/                   # Core business logic
│   ├── gui/                      # Graphical user interface
│   ├── infrastructure/           # External dependencies
│   └── services/                 # Application services
├── tests/                        # Test suite
└── README.md                     # This file
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/voice_recorder

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
```

### Code Quality

```bash
# Type checking
mypy src/

# Linting
flake8 src/

# Formatting
black src/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the [troubleshooting guide](./docs/HOTKEY_TROUBLESHOOTING.md)
- Review the [documentation](./docs/)
- Open an issue on GitHub