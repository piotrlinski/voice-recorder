# Voice Recorder Application

A professional voice recording application for macOS that transcribes English speech using OpenAI's Whisper API and pastes the text at the mouse cursor location.

## Features

- **Hotkey Recording**: Press and hold the Shift key to record voice
- **Multiple Transcription Options**:
  - **OpenAI Whisper**: Cloud-based transcription (requires API key)
  - **Local Whisper**: Offline transcription using OpenAI Whisper
- **English Language Support**: Optimized for English speech transcription
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
│       ├── openai_whisper_service.py
│       ├── local_whisper_service.py
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
   
   **Note**: The application will automatically start the configuration setup on first run if no configuration file exists.
   
   This will guide you through an interactive setup process:
   - **Transcription mode** (OpenAI Whisper or Local Whisper)
   - **Model selection** (for Local Whisper: tiny, base, small, medium, large)
   - **Audio settings** (sample rate, channels, chunk size)
   - **Hotkey configuration** (recording trigger key)
   - **Sound feedback settings** (enabled/disabled, volume, duration)
   - **General preferences** (auto-paste, temp directory)

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
# Interactive configuration setup
voice-recorder init

# Initialize with custom config directory
voice-recorder init --config-dir ~/custom_config

# Force overwrite existing configuration
voice-recorder init --force
```

**Interactive Configuration Features:**
- **Step-by-step setup** with clear prompts and descriptions
- **Model selection** for Local Whisper with size and accuracy information
- **Audio configuration** with sensible defaults
- **Sound feedback customization** with volume and duration controls

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

**First Time Setup**: If no configuration file exists, the application will automatically start the interactive configuration setup before launching.

#### Manage Configuration
```bash
# Show current configuration
voice-recorder config --show

# Edit configuration in your default editor
voice-recorder config --edit
voice-recorder config --edit --editor vim
voice-recorder config --edit --editor code

# Reset to defaults
voice-recorder config --reset

# Quick configuration changes
voice-recorder set transcription.mode local_whisper
voice-recorder set sound.volume 0.2
voice-recorder set hotkey.key ctrl+shift

# Show application status
voice-recorder status

# Manage temporary files
voice-recorder purge --dry-run  # Preview files to be deleted
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

### Configuration

The application uses an **INI-based configuration system** stored in `~/.voicerecorder/config.ini`. INI files are more readable and user-friendly than JSON.

**Initialize Configuration:**
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
voice-recorder config --edit --editor vim
voice-recorder config --edit --editor code
```

**Quick Configuration Changes:**
```bash
voice-recorder set transcription.mode local_whisper
voice-recorder set sound.volume 0.2
voice-recorder set hotkey.key ctrl+shift
```

**Convert to JSON:**
```bash
voice-recorder convert json  # Convert INI to JSON for backup
```

**Configuration Options:**
- **Transcription Mode**: Choose between OpenAI, Local Whisper
- **Model Selection**: Specify which model to use
- **Hotkey**: Change the trigger key (default: Shift)
- **Audio Settings**: Sample rate, channels, format
- **Auto-paste**: Enable/disable automatic text pasting
- **Sound Feedback**: Enable/disable and customize recording sounds
- **Temp Directory**: Customize temporary file storage location

**Configuration Examples:**
See the `examples/` directory for sample INI configuration files:
- `config_openai_whisper.ini` - OpenAI Whisper setup
- `config_local_whisper.ini` - Local Whisper setup
- `config_quiet.ini` - Quiet operation
- `config_no_sound.ini` - Silent operation
- `config_high_quality.ini` - High-quality audio settings

**Note:** The application now uses INI format exclusively. JSON configurations can be converted using `voice-recorder convert json`.

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