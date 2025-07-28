# Voice Recorder Configuration Examples

This directory contains various configuration examples for the voice recorder application, demonstrating different transcription modes and sound feedback options.

## Configuration Examples

### Transcription Mode Examples

#### 1. `config_local_whisper.json` - Local Whisper (Offline)
**Use Case**: Offline transcription using OpenAI Whisper
```json
{
  "transcription_config": {
    "mode": "local_whisper",
    "model_name": "base"
  }
}
```
**Features**:
- Works offline (no internet required)
- No API costs
- Requires model download on first use
- Optimized for CPU with FP32 precision

#### 2. `config_openai_whisper.json` - OpenAI Whisper (Cloud)
**Use Case**: High-accuracy cloud-based transcription
```json
{
  "transcription_config": {
    "mode": "openai_whisper",
    "model_name": "whisper-1",
    "api_key": "your-openai-api-key"
  }
}
```
**Features**:
- Highest accuracy
- Requires OpenAI API key
- Internet connection required
- Pay-per-use pricing

# Note: Ollama model configuration examples have been removed as Ollama services are no longer supported

### Sound Configuration Examples

#### 4. `config_beep.json` - System Beep Sounds
**Use Case**: Simple, system-native beep sounds
```json
{
  "sound_config": {
    "enabled": true,
    "sound_type": "beep",
    "volume": 0.15
  }
}
```
**Features**:
- System beep compatibility
- Minimal resource usage
- Works on all operating systems

#### 5. `config_quiet_tone.json` - Very Quiet Tones
**Use Case**: Minimal audio feedback
```json
{
  "sound_config": {
    "enabled": true,
    "sound_type": "tone",
    "volume": 0.05,
    "duration": 0.2
  }
}
```
**Features**:
- Very low volume (5%)
- Short duration (0.2s)
- Suitable for quiet environments

#### 6. `config_custom_tone.json` - Custom Tone Settings
**Use Case**: Customized frequency range and volume
```json
{
  "sound_config": {
    "enabled": true,
    "sound_type": "tone",
    "volume": 0.25,
    "start_frequency": 600.0,
    "end_frequency": 1000.0,
    "duration": 0.4
  }
}
```
**Features**:
- Higher volume (25%)
- Custom frequency range (600Hz-1000Hz)
- Longer duration (0.4s)

#### 7. `config_no_sound.json` - Silent Operation
**Use Case**: No audio feedback during recording
```json
{
  "sound_config": {
    "enabled": false,
    "sound_type": "none"
  }
}
```
**Features**:
- Completely silent operation
- No audio feedback
- Suitable for quiet environments

## Documentation

### `sound_configuration_examples.md`
Comprehensive guide covering all sound configuration options, parameters, usage examples, and troubleshooting tips.



### `custom_transcription.py`
Example script demonstrating how to use different transcription services programmatically.

## Usage

### Apply a Configuration
```bash
# Copy a configuration example to your config directory
cp examples/config_beep.json ~/.voicerecorder/config.json

# Or use with the --config flag
voice-recorder start --config examples/config_quiet_tone.json
```

### Test Configurations
```bash
# Test sound configurations
python -c "
import sys; sys.path.insert(0, 'src')
from voice_recorder.domain.models import SoundConfig, SoundType
from voice_recorder.infrastructure.audio_feedback import SystemAudioFeedback
import time

config = SoundConfig(enabled=True, sound_type=SoundType.BEEP)
feedback = SystemAudioFeedback(config)
feedback.play_start_beep()
time.sleep(1)
feedback.play_stop_beep()
print('Test completed!')
"
```

### Interactive Configuration
```bash
# Edit configuration interactively
voice-recorder config --edit

# Show current configuration
voice-recorder status
```

## Quick Start

1. **Choose your transcription mode**:
   - For offline use: `config_local_whisper.json`
   - For best accuracy: `config_openai_whisper.json`
   - (Ollama model examples removed)

2. **Choose your sound preference**:
   - For quiet operation: `config_quiet_tone.json` or `config_no_sound.json`
   - For system compatibility: `config_beep.json`
   - For custom sounds: `config_custom_tone.json`

3. **Apply the configuration**:
   ```bash
   cp examples/config_local_whisper.json ~/.voicerecorder/config.json
   voice-recorder start
   ```

## Recommended Combinations

### Quiet Office Environment
- Transcription: `config_local_whisper.json`
- Sound: `config_quiet_tone.json`

### Noisy Environment
- Transcription: `config_openai_whisper.json`
- Sound: `config_custom_tone.json` (higher volume)

### System Compatibility Focus
- Transcription: `config_local_whisper.json`
- Sound: `config_beep.json`

### Maximum Privacy
- Transcription: `config_local_whisper.json`
- Sound: `config_no_sound.json` 