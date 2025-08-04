# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a professional voice recording library for macOS that transcribes English speech using OpenAI's Whisper API or local Whisper models. The library provides programmatic access to voice recording and transcription functionality and uses Clean Architecture principles with dependency injection.

## Development Commands

### Core Commands
```bash
# Install dependencies
pip install -e ".[dev,test]"

# Run tests
python -m pytest tests/ --cov=src/voice_recorder --cov-report=html

# Type checking
mypy src/voice_recorder

# Code formatting
black src/ tests/
isort src/ tests/

# Linting  
flake8 src/ tests/

# Run all quality checks
pytest && mypy src/voice_recorder && black --check src/ tests/ && isort --check-only src/ tests/ && flake8 src/ tests/
```

### Testing Commands
```bash
# All tests with coverage
python -m pytest tests/ --cov=src/voice_recorder --cov-report=term-missing --cov-report=html

# Unit tests only
python -m pytest tests/unit/ -v

# Integration tests only  
python -m pytest tests/integration/ -v

# Run specific test
python -m pytest tests/unit/test_audio_recorder.py::TestPyAudioRecorder::test_init_with_pyaudio -v
```

## Architecture

The application follows Clean Architecture with clear separation of concerns:

### Layer Structure
- **Domain Layer** (`src/voice_recorder/domain/`): Core business logic, Pydantic models, and interfaces (protocols)
- **Services Layer** (`src/voice_recorder/services/`): Application business logic and orchestration  
- **Infrastructure Layer** (`src/voice_recorder/infrastructure/`): External dependencies and adapters
- **API Layer** (`src/voice_recorder/api/`): Application entry points and dependency injection

### Key Design Patterns
- **Dependency Injection**: All components are injected via interfaces defined in `domain/interfaces.py`
- **Factory Pattern**: `TranscriptionServiceFactory` creates transcription services based on configuration
- **Clean Architecture**: Strict dependency inversion - domain layer has no external dependencies
- **Protocol/Interface Segregation**: Clear contracts between layers using Python protocols

### Core Components

#### Main Application Entry Point
- `src/voice_recorder/api/app.py`: Main application class with dependency injection setup

#### Business Logic
- `src/voice_recorder/services/voice_recorder_service.py`: Main orchestration service
- `src/voice_recorder/domain/models.py`: Pydantic models for configuration and data
- `src/voice_recorder/domain/interfaces.py`: Protocol definitions for all interfaces

#### Infrastructure Adapters
- `src/voice_recorder/infrastructure/audio_recorder.py`: PyAudio-based recording
- `src/voice_recorder/infrastructure/transcription/`: Transcription service implementations (OpenAI, Local Whisper, Mock)
- `src/voice_recorder/infrastructure/hotkey.py`: Pynput-based hotkey detection
- `src/voice_recorder/infrastructure/text_paster.py`: macOS text pasting
- `src/voice_recorder/infrastructure/config_manager.py`: INI-based configuration management
- `src/voice_recorder/infrastructure/logging_adapter.py`: Standard logging adapter that replaced Rich console

## Configuration System

The library uses INI-based configuration stored in `~/.voicerecorder/config.ini`:

### Configuration Management
```python
from voice_recorder.infrastructure.config_manager import ConfigManager

# Load configuration programmatically
config_manager = ConfigManager()
config = config_manager.load_config()

# Create custom configuration
from voice_recorder.domain.models import ApplicationConfig, TranscriptionConfig, TranscriptionMode

transcription_config = TranscriptionConfig(
    mode=TranscriptionMode.LOCAL_WHISPER,
    model_name="base"
)
config = ApplicationConfig(transcription_config=transcription_config)
```

### Transcription Modes
- **OpenAI Whisper**: Requires API key to be configured in config file
- **Local Whisper**: Offline transcription, requires `pip install openai-whisper`
- **Mock**: For testing purposes

## Testing Strategy

### Test Structure
```
tests/
├── conftest.py                    # Shared fixtures and pytest configuration
├── unit/                          # Unit tests (34 tests)
│   ├── test_audio_recorder.py     # Audio recording component tests
│   ├── test_transcription.py      # Transcription service tests
│   ├── test_session_manager.py    # Session management tests
│   └── ...
└── integration/                   # Integration tests (9 tests)
    └── test_voice_recorder_service.py  # End-to-end workflow tests
```

### Testing Guidelines
- Use mocks for external dependencies (OpenAI API, audio devices)
- Test both success and failure scenarios
- Use fixtures from `conftest.py` for common setup
- Aim for high test coverage (current coverage reports in `htmlcov/`)

## Key Technologies & Dependencies

### Core Dependencies
- **Python 3.11+**: Main language (strict type checking enabled)
- **Pydantic v2**: Data validation and settings management
- **PyAudio**: Cross-platform audio recording and playback
- **OpenAI API v1.0+**: Speech-to-text transcription
- **Pynput**: Cross-platform input monitoring for hotkeys

### Development Dependencies
- **pytest**: Testing framework with coverage reporting
- **mypy**: Static type checking (strict mode enabled)
- **black**: Code formatting (88 character line length)
- **isort**: Import sorting
- **flake8**: Linting

## Important Implementation Details

### Type Safety
- Strict mypy configuration in `pyproject.toml`
- All public methods and classes must have type hints
- Use protocols for dependency injection interfaces

### Error Handling
- Graceful degradation for audio device failures
- Comprehensive exception handling in service layer
- Rich console output for user-friendly error messages

### Platform-Specific Features
- macOS-optimized text pasting using AppleScript
- Cross-platform audio recording with PyAudio
- Hotkey detection works across platforms

### Audio Processing
- Configurable sample rates (default: 16kHz for Whisper compatibility)
- Support for multiple audio formats
- Natural system audio feedback when accessing microphone

## Development Workflow

1. Install dependencies: `pip install -e ".[dev,test]"`
2. Run tests before making changes: `pytest`
3. Make changes following Clean Architecture principles
4. Add/update tests for new functionality
5. Run quality checks: `mypy`, `black`, `isort`, `flake8`
6. Test functionality:
   - **CLI**: `voice-recorder` (supports hotkeys and background operation)
   - **Configuration**: `voice-recorder init` (interactive setup wizard)
   - **Python API**:

     ```python
     from voice_recorder.api.app import VoiceRecorderApp
     app = VoiceRecorderApp()
     app.start()
     ```

## CLI Mode

- **CLI Mode** (`voice-recorder`): Full functionality with hotkey support and background operation
  - Interactive configuration wizard: `voice-recorder init`
  - Configuration management: `voice-recorder config show/path/reset`
  - Background hotkey support for hands-free operation
  - Lightweight and efficient command-line interface

## Security Considerations

- Never commit API keys (store them in configuration files that are ignored by git)
- All configuration must be done through the INI configuration file system
- Input validation using Pydantic models
- Secure temporary file handling in configured temp directories
