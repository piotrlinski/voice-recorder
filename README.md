# Voice Recorder Application

A professional voice recording application for macOS that transcribes English speech using OpenAI's Whisper API and pastes the text at the mouse cursor location.

## Features

- **Hotkey Recording**: Press and hold the Shift key to record voice
- **Multiple Transcription Options**:
  - **OpenAI Whisper**: Cloud-based transcription (requires API key)
  - **Local Whisper**: Offline transcription using Whisper.cpp
  - **Ollama Whisper**: Local transcription using Ollama + Whisper
  - **Ollama Models**: Use any Ollama model (Llama, DeepSeek, etc.)
- **Smart Text Pasting**: Automatically pastes transcribed text at mouse cursor location
- **Background Service**: Runs continuously in the background
- **Audio Feedback**: Provides audio cues for recording start/stop
- **Professional Architecture**: Clean architecture with dependency injection

## Architecture

The application follows Clean Architecture principles with clear separation of concerns:

```
src/voice_recorder/
├── domain/           # Core business logic and models
├── services/         # Application business logic
├── infrastructure/   # External dependencies (adapters)
│   └── transcription/  # Transcription services module
│       ├── __init__.py
│       ├── factory.py
│       ├── openai_service.py
│       ├── local_whisper_service.py
│       ├── ollama_whisper_service.py
│       ├── (ollama services removed)
│       └── mock_service.py
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

- Python 3.8+
- macOS (for system integration features)
- OpenAI API key

### Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd my-voice-recorder
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

5. **Initialize configuration:**
   ```bash
   voice-recorder init
   ```
   
   This will guide you through setting up:
   - Transcription mode (OpenAI, Local Whisper, Ollama)
   - Model selection
   - Audio settings
   - Hotkey configuration
   - General preferences

### Alternative Installation Methods

**Using pip directly:**
```bash
pip install voice-recorder
```

**Using the entry point:**
```bash
# After installation, you can run:
voice-recorder start
```

## Usage

### CLI Commands

The application provides a comprehensive CLI interface:

#### Initialize Configuration
```bash
# Initialize with default settings
voice-recorder init

# Initialize with custom config directory
voice-recorder init --config-dir ~/custom_config

# Force overwrite existing configuration
voice-recorder init --force
```

#### Start the Application
```bash
# Start with default configuration
voice-recorder start

# Start with custom config file
voice-recorder start --config ~/.voicerecorder/config.json

# Start with custom environment file
voice-recorder start --env-file ~/.custom_env

# Start with verbose output
voice-recorder start --verbose
```

#### Manage Configuration
```bash
# Show current configuration
voice-recorder config --show

# Edit configuration interactively
voice-recorder config --edit

# Reset to defaults
voice-recorder config --reset

# Show application status
voice-recorder status

# Manage temporary files
voice-recorder purge --dry-run  # Preview files to be deleted
voice-recorder purge --force     # Delete without confirmation

# Remove temporary voice files
voice-recorder purge --dry-run  # Preview what would be deleted
voice-recorder purge --force     # Delete without confirmation
```

### Running the Application

**Method 1: Using the CLI (Recommended)**
```bash
voice-recorder start
```

**Method 2: Using the installed package**
```bash
voice-recorder
```

**Method 3: Python module execution**
```bash
python -m voice_recorder.cli.main start
```

**Method 4: Direct execution (development)**
```bash
python -c "import sys; sys.path.insert(0, 'src'); from voice_recorder.cli.main import app; app()"
```

The application will start and listen for the Shift key. When you press and hold Shift, it will:

1. Start recording audio
2. Play a start beep
3. Continue recording until you release Shift
4. Play a stop beep
5. Transcribe the audio using the configured transcription service
6. Paste the text at your current mouse cursor location

### Transcription Modes

The application supports multiple transcription modes to suit different needs:

#### 1. OpenAI Whisper (Default)
- **Pros**: High accuracy, no local setup required
- **Cons**: Requires API key, internet connection
- **Setup**: Set `OPENAI_API_KEY` in `my.env`
- **Note**: Uses OpenAI API v1.0+ (latest version)

#### 2. Local Whisper (Offline)
- **Pros**: Works offline, no API costs, optimized for CPU
- **Cons**: Requires model download, more setup
- **Setup**: 
  ```bash
  pip install openai-whisper
  # Models are downloaded automatically
  ```
- **Note**: Automatically uses FP32 precision to avoid CPU compatibility warnings

#### 3. Ollama Whisper (Local)
- **Pros**: Easy setup, good performance, official Python client
- **Cons**: Requires Ollama installation
- **Setup**:
  ```bash
  brew install ollama
  ollama pull whisper
  pip install ollama
  ```

#### 4. Ollama Custom Models (Local)
- **Pros**: Use any model (Llama, DeepSeek, etc.), official Python client
- **Cons**: May be less accurate for transcription
- **Setup**:
  ```bash
  brew install ollama
  ollama pull llama3.2  # or any other model
  pip install ollama
  ```

### Configuration

The application uses a JSON-based configuration system stored in `~/.voicerecorder/config.json`.

**Interactive Configuration:**
```bash
voice-recorder init
```

**Show Current Configuration:**
```bash
voice-recorder config --show
```

**Edit Configuration:**
```bash
voice-recorder config --edit
```

**Configuration Options:**
- **Transcription Mode**: Choose between OpenAI, Local Whisper, Ollama
- **Model Selection**: Specify which model to use
- **Hotkey**: Change the trigger key (default: Shift)
- **Audio Settings**: Sample rate, channels, format
- **Auto-paste**: Enable/disable automatic text pasting
- **Sound Feedback**: Enable/disable and customize recording sounds
- **Temp Directory**: Customize temporary file storage location

**Configuration Examples:**
See the `examples/` directory for sample configuration files:
- `config_local_whisper.json` - Local Whisper setup
- `config_openai_whisper.json` - OpenAI Whisper setup
- (Ollama model examples removed)
- `config_beep.json` - System beep sounds
- `config_quiet_tone.json` - Very quiet tones
- `config_custom_tone.json` - Custom tone settings
- `config_no_sound.json` - Silent operation

### Environment Variables

The application supports custom environment files for API keys and other sensitive configuration:

**Default Behavior:**
- Automatically loads `.env` file from the current directory
- Falls back to system environment variables

**Custom Environment File:**
```bash
# Use a custom .env file
voice-recorder start --env-file ~/.my_custom_env

# Use a different environment file for testing
voice-recorder start --env-file ~/.test_env
```

**Environment Variables:**
- `OPENAI_API_KEY`: Required for OpenAI Whisper mode
- `OLLAMA_BASE_URL`: Optional, defaults to `http://localhost:11434`

### Sound Configuration

The application provides customizable audio feedback when recording starts and stops:

**Sound Types:**
- **Tone**: High-quality ascending/descending tones (default)
- **Beep**: Simple system beep sounds
- **None**: No audio feedback

**Sound Settings:**
- **Volume**: Adjustable from 0.0 to 1.0 (default: 0.15)
- **Frequency Range**: Customizable start/end frequencies (default: 800Hz-1200Hz)
- **Duration**: Adjustable sound duration (default: 0.3 seconds)
- **Enabled/Disabled**: Toggle sound feedback on/off

**Default Configuration:**
- **Start Sound**: Ascending tone (800Hz → 1200Hz)
- **Stop Sound**: Descending tone (1200Hz → 800Hz)
- **Volume**: 15% (quiet and pleasant)
- **Duration**: 0.3 seconds

**Configuration:**
- Sound feedback is enabled by default
- Customize via CLI: `voice-recorder config --edit`
- Uses PyAudio for high-quality audio playback
- Falls back to system beep if PyAudio fails

## Testing

The project includes comprehensive unit and integration tests.

### Running Tests

**All tests:**
```bash
python run_tests.py
```

**Unit tests only:**
```bash
python run_tests.py --type unit
```

**Integration tests only:**
```bash
python run_tests.py --type integration
```

**With coverage report:**
```bash
python run_tests.py --coverage
```

**Verbose output:**
```bash
python run_tests.py -v
```

### Test Structure

```
tests/
├── conftest.py                    # Shared test fixtures
├── unit/                          # Unit tests
│   ├── test_audio_recorder.py     # Audio recording tests
│   ├── test_transcription.py      # Transcription service tests
│   └── test_session_manager.py    # Session management tests
└── integration/                   # Integration tests
    └── test_voice_recorder_service.py  # End-to-end workflow tests
```

### Test Coverage

The test suite covers:

- **Unit Tests (34 tests):**
  - Audio recorder initialization and operation
  - Transcription service with OpenAI integration
  - Session management and state transitions
  - Error handling and edge cases

- **Integration Tests (9 tests):**
  - Complete recording workflow
  - Hotkey press/release detection
  - Service lifecycle management
  - Configuration options

### Running Individual Tests

```bash
# Run specific test file
python -m pytest tests/unit/test_audio_recorder.py -v

# Run specific test method
python -m pytest tests/unit/test_audio_recorder.py::TestPyAudioRecorder::test_init_with_pyaudio -v

# Run tests with coverage
python -m pytest tests/ --cov=src/voice_recorder --cov-report=html
```

## Development

### Project Structure

```
my-voice-recorder/
├── src/voice_recorder/           # Main application code
│   ├── domain/                   # Core business logic
│   │   ├── models.py            # Pydantic models
│   │   └── interfaces.py        # Protocol definitions
│   ├── services/                 # Application services
│   │   └── voice_recorder_service.py
│   ├── infrastructure/           # External adapters
│   │   ├── audio_recorder.py    # PyAudio implementation
│   │   ├── transcription.py     # OpenAI integration
│   │   ├── hotkey.py           # Pynput implementation
│   │   ├── text_paster.py      # macOS text pasting
│   │   ├── session_manager.py  # Session tracking
│   │   └── audio_feedback.py   # System audio
│   └── api/                     # Application entry points
│       └── app.py              # Dependency injection setup
├── tests/                       # Test suite
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── run_tests.py                # Test runner script
└── README.md                   # This file
```

### Adding New Features

1. **Domain Layer**: Define models and interfaces in `domain/`
2. **Infrastructure Layer**: Implement adapters in `infrastructure/`
3. **Service Layer**: Add business logic in `services/`
4. **Tests**: Add corresponding unit and integration tests

### Code Quality

- **Type Safety**: All code uses strict type hints
- **Clean Architecture**: Clear separation of concerns
- **Dependency Injection**: All dependencies are injected
- **Comprehensive Testing**: High test coverage with mocks

## Troubleshooting

### Common Issues

1. **"PyAudio not available"**
   - Install PortAudio: `brew install portaudio`
   - Reinstall PyAudio: `pip install --force-reinstall pyaudio`

2. **"ffmpeg not found" (for local Whisper)**
   - Install ffmpeg: `brew install ffmpeg`
   - This is required for local Whisper transcription

3. **FP16/FP32 warnings (for local Whisper)**
   - These warnings are automatically suppressed in the application
   - The service uses FP32 precision for better CPU compatibility

4. **"OpenAI API key not found"**
   - Ensure `my.env` file exists with `OPENAI_API_KEY=your_key`

3. **"Permission denied" for audio recording**
   - Grant microphone permissions to Terminal/IDE in System Preferences

4. **Text not pasting at cursor location**
   - Ensure the target application supports text input
   - Check that the application has focus

### Debug Mode

Run with verbose logging:
```bash
python main.py --debug
```

## Dependencies

- **openai**: OpenAI API client
- **python-dotenv**: Environment variable management
- **pynput**: Cross-platform input monitoring
- **pyaudio**: Audio recording and playback
- **pydantic**: Data validation and settings
- **pytest**: Testing framework
- **pytest-mock**: Mocking utilities
- **pytest-cov**: Coverage reporting

## License

This project is licensed under the MIT License. 