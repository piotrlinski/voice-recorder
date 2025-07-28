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
│       ├── ollama_model_service.py
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

4. **Install PortAudio (required for PyAudio):**
   ```bash
   brew install portaudio
   ```

5. **Configure transcription mode:**
   
   **Option A: Interactive configuration**
   ```bash
   python configure_transcription.py
   ```
   
   **Option B: Manual configuration**
   Create a `my.env` file in the project root:
   ```
   OPENAI_API_KEY=your_openai_api_key_here  # For OpenAI mode
   ```

### Alternative Installation Methods

**Using pip directly:**
```bash
pip install voice-recorder
```

**Using the entry point:**
```bash
# After installation, you can run:
voice-recorder
```

## Usage

### Running the Application

**Method 1: Using the installed package**
```bash
voice-recorder
```

**Method 2: Python module execution**
```bash
python -m voice_recorder.api.app
```

**Method 3: Direct execution (development)**
```bash
python -c "import sys; sys.path.insert(0, 'src'); from voice_recorder.api.app import main; main()"
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
- **Pros**: Works offline, no API costs
- **Cons**: Requires model download, more setup
- **Setup**: 
  ```bash
  pip install whisper-cpp-python
  # Models are downloaded automatically
  ```

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

**Interactive Configuration:**
```bash
python configure_transcription.py
```

**Manual Configuration:**
You can customize the application behavior by modifying the configuration in `src/voice_recorder/api/app.py`:

- **Transcription Mode**: Choose between OpenAI, Local Whisper, Ollama
- **Model Selection**: Specify which model to use
- **Hotkey**: Change the trigger key (default: Shift)
- **Audio Settings**: Sample rate, channels, format
- **Auto-paste**: Enable/disable automatic text pasting
- **Audio Feedback**: Enable/disable beep sounds

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

2. **"OpenAI API key not found"**
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