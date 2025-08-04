# Voice Recorder CLI Application

A professional voice recording command-line application for macOS with real-time speech-to-text transcription and AI-powered text enhancement.

## ✨ Features

📝 **Dual Transcription Modes**: OpenAI Whisper (cloud) or local Whisper models  
🤖 **Enhanced Transcription**: AI-powered grammar and punctuation improvement  
⌨️ **Hotkey Support**: Hands-free recording with customizable hotkeys  
📋 **Auto-paste**: Automatic text insertion at cursor position  
⚙️ **Interactive Setup**: Configuration wizard for easy setup  
🔒 **Privacy Options**: Complete offline operation with local models  

## Installation

### Prerequisites

- Python 3.11+
- macOS (for system integration features)
- OpenAI API key (for cloud transcription) or local Whisper model

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

## Usage

### Getting Started

1. **Initialize configuration:**
   ```bash
   voice-recorder init
   ```

2. **Start recording:**
   ```bash
   voice-recorder
   ```

### Command Line Options

```bash
# Initialize configuration (required on first run)
voice-recorder init

# Start voice recorder with default configuration
voice-recorder

# Configuration management
voice-recorder config show    # View current settings
voice-recorder config path    # Show config file location  
voice-recorder config reset   # Reset to defaults
```

### Hotkeys

- **Right Shift**: Basic transcription (speech → text)
- **Left Ctrl**: Enhanced transcription (speech → text → AI improvement)
- **Ctrl+C**: Stop the application

## 🔧 Configuration

The application uses a configuration file at `~/.voicerecorder/config.ini`. Here are common configuration examples:

### OpenAI Transcription (Cloud)

**Best for: Highest accuracy, internet available**

```ini
[transcription]
mode = openai

[transcription.openai]
api_key = sk-your-openai-key-here
whisper_model = whisper-1
gpt_model = gpt-3.5-turbo
gpt_creativity = 0.3
enhanced_transcription_prompt = Please improve the following transcribed text by fixing grammar, punctuation, and making it more coherent while preserving the original meaning. Only return the improved text without any explanations or additional commentary.

[controls]
basic_key = shift_r
enhanced_key = ctrl_l

[audio]
sample_rate = 16000
channels = 1
format = wav
chunk_size = 1024

[general]
auto_paste = true
```

**What this means:**
- Uses OpenAI's Whisper API for transcription
- Uses GPT-3.5-turbo for enhanced text improvement
- `gpt_creativity = 0.3` means conservative enhancement (range 0.0-2.0)
- Requires internet connection and OpenAI API key

### Local Transcription (Offline)

**Best for: Privacy, no internet required**

```ini
[transcription]
mode = local

[transcription.local]
whisper_model = small
ollama_base_url = http://localhost:11434
ollama_model = llama3.1
ollama_creativity = 0.3
enhanced_transcription_prompt = Please improve the following transcribed text by fixing grammar, punctuation, and making it more coherent while preserving the original meaning. Only return the improved text without any explanations or additional commentary.

[controls]
basic_key = shift_r
enhanced_key = ctrl_l

[audio]
sample_rate = 16000
channels = 1
format = wav
chunk_size = 1024

[general]
auto_paste = true
```

**What this means:**
- Uses local Whisper model for transcription (offline)
- Uses Ollama running locally for enhanced text improvement
- `whisper_model = small` for faster processing (can be `small`, `medium`, `large`)
- Requires Ollama installed locally for enhanced transcription
- Complete offline operation

### Basic vs Enhanced Transcription

#### Basic Transcription (Right Shift)
- **Process**: Audio → Whisper → Raw text
- **Speed**: Fast
- **Quality**: Good transcription accuracy
- **Example**: 
  ```
  Input: "um so i think we should uh maybe consider the new approach"
  Output: "Um, so I think we should, uh, maybe consider the new approach."
  ```

#### Enhanced Transcription (Left Ctrl)
- **Process**: Audio → Whisper → AI improvement → Polished text
- **Speed**: Slower (requires additional AI processing)
- **Quality**: Professional, polished text
- **Example**: 
  ```
  Input: "um so i think we should uh maybe consider the new approach"
  Output: "I think we should consider the new approach."
  ```

**Enhanced transcription benefits:**
- Removes filler words (um, uh, like)
- Fixes grammar and punctuation
- Improves sentence structure
- Makes text more professional and readable
- Maintains original meaning

### Configuration Options

#### Transcription Settings
- `mode`: `openai` (cloud) or `local` (offline)
- `whisper_model`: For local mode: `small`, `medium`, `large`
- `gpt_model`: For OpenAI mode: `gpt-3.5-turbo`, `gpt-4`, etc.
- `gpt_creativity`/`ollama_creativity`: 0.0-2.0 (lower = more conservative)

#### Control Settings
- `basic_key`: Hotkey for basic transcription
- `enhanced_key`: Hotkey for enhanced transcription
- Available keys: `shift_r`, `shift_l`, `ctrl_l`, `ctrl_r`, `alt_l`, `alt_r`, `cmd_l`, `cmd_r`

#### Audio Settings
- `sample_rate`: Recording quality (16000 recommended for Whisper)
- `channels`: 1 (mono) or 2 (stereo)
- `format`: Audio format (`wav`, `mp3`, `flac`)

#### General Settings
- `auto_paste`: Automatically paste transcribed text (`true`/`false`)

### Quick Setup Examples

#### Method 1: Interactive Setup
```bash
voice-recorder init
# Follow the prompts to configure transcription mode, API keys, and preferences
```

#### Method 2: Manual Configuration for Local Mode
```bash
# Create config directory
mkdir -p ~/.voicerecorder

# Create local transcription configuration
cat > ~/.voicerecorder/config.ini << 'EOF'
[transcription]
mode = local

[transcription.local]
whisper_model = small

[controls]
basic_key = shift_r
enhanced_key = ctrl_l

[general]
auto_paste = true
EOF
```

#### Method 3: Manual Configuration for OpenAI Mode
```bash
# Create config directory
mkdir -p ~/.voicerecorder

# Create OpenAI transcription configuration
cat > ~/.voicerecorder/config.ini << 'EOF'
[transcription]
mode = openai

[transcription.openai]
api_key = your-openai-api-key-here
whisper_model = whisper-1
gpt_model = gpt-3.5-turbo

[controls]
basic_key = shift_r
enhanced_key = ctrl_l

[general]
auto_paste = true
EOF
```

## Architecture

The application follows Clean Architecture principles with clear separation of concerns:

```
src/voice_recorder/
├── domain/           # Core business logic and models
├── services/         # Application business logic
├── infrastructure/   # External dependencies (adapters)
│   └── transcription/  # Transcription services module
├── cli/             # Command-line interface
└── api/             # Application entry points
```

### Design Patterns

- **Dependency Injection**: All components are injected via interfaces
- **Protocol/Interface Segregation**: Clear contracts between layers
- **Factory Pattern**: Application factory for dependency setup
- **Observer Pattern**: Hotkey event handling

## 📚 Documentation

### Additional Documentation
- **[Troubleshooting](./docs/HOTKEY_TROUBLESHOOTING.md)** - Common issues and solutions
- **[Enhanced Transcription Guide](./docs/ENHANCED_TRANSCRIPTION.md)** - AI configuration details

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/voice_recorder

# Run specific test categories
pytest tests/unit/
```

### Code Quality

```bash
# Type checking
mypy src/

# Linting
flake8 src/

# Formatting
black src/

# All quality checks at once
pytest && mypy src/ && black --check src/ && flake8 src/
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