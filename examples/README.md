# Voice Recorder Configuration Examples

This directory contains various configuration examples for the voice recorder application, demonstrating different transcription modes and sound feedback options.

## Configuration Examples

### Transcription Mode Examples

#### 1. `config_local_whisper.ini` - Local Whisper (Offline)
**Use Case**: Offline transcription using OpenAI Whisper
```ini
[transcription]
mode = local_whisper
model_name = base
```
**Features**:
- Works offline (no internet required)
- No API costs
- Requires model download on first use
- Optimized for CPU with FP32 precision

#### 2. `config_openai_whisper.ini` - OpenAI Whisper (Cloud)
**Use Case**: High-accuracy cloud-based transcription
```ini
[transcription]
mode = openai_whisper
model_name = whisper-1
api_key = your-openai-api-key
```
**Features**:
- Highest accuracy
- Requires OpenAI API key
- Internet connection required
- Pay-per-use pricing

### Sound Configuration Examples

#### 3. `config_beep.ini` - System Beep Sounds
**Use Case**: Simple, system-native beep sounds
```ini
[sound]
enabled = true
sound_type = beep
volume = 0.15
```
**Features**:
- Uses system beep (`\a`) for audio feedback
- Compatible with all operating systems
- Minimal resource usage
- Volume setting is ignored (uses system volume)

#### 4. `config_quiet.ini` - Very Quiet Tones
**Use Case**: Minimal audio feedback
```ini
[sound]
enabled = true
sound_type = tone
volume = 0.05
duration = 0.2
```
**Features**:
- Very low volume (5%)
- Short duration (0.2s)
- Suitable for quiet environments

#### 5. `config_custom_tone.ini` - Custom Tone Settings
**Use Case**: Customized frequency range and volume
```ini
[sound]
enabled = true
sound_type = tone
volume = 0.25
start_frequency = 600.0
end_frequency = 1000.0
duration = 0.4
```
**Features**:
- Higher volume (25%)
- Custom frequency range (600Hz-1000Hz)
- Longer duration (0.4s)
- More noticeable audio feedback

#### 6. `config_no_sound.ini` - Silent Operation
**Use Case**: No audio feedback during recording
```ini
[sound]
enabled = false
sound_type = none
```
**Features**:
- Completely silent operation
- No audio feedback
- Suitable for quiet environments

#### 7. `config_high_quality.ini` - High-Quality Audio Settings
**Use Case**: Professional audio feedback
```ini
[sound]
enabled = true
sound_type = tone
volume = 0.30
start_frequency = 800.0
end_frequency = 1200.0
duration = 0.5
```
**Features**:
- Higher volume (30%)
- Standard frequency range (800Hz-1200Hz)
- Longer duration (0.5s)
- Professional audio feedback

## Sound Configuration Parameters

### `enabled` (boolean)
- **Default**: `true`
- **Description**: Enable or disable sound feedback
- **Values**: `true` (sounds enabled), `false` (sounds disabled)

### `sound_type` (string)
- **Default**: `"tone"`
- **Description**: Type of sound to play
- **Values**: 
  - `"tone"` - High-quality frequency sweep tones
  - `"beep"` - Simple system beep
  - `"none"` - No sound (same as `enabled: false`)

### `volume` (float)
- **Default**: `0.15`
- **Description**: Sound volume level
- **Range**: `0.0` to `1.0`
- **Note**: Only applies to `"tone"` type sounds

### `start_frequency` (float)
- **Default**: `800.0`
- **Description**: Starting frequency for tone sweep (Hz)
- **Range**: `20.0` to `20000.0`
- **Note**: Only applies to `"tone"` type sounds

### `end_frequency` (float)
- **Default**: `1200.0`
- **Description**: Ending frequency for tone sweep (Hz)
- **Range**: `20.0` to `20000.0`
- **Note**: Only applies to `"tone"` type sounds

### `duration` (float)
- **Default**: `0.3`
- **Description**: Sound duration in seconds
- **Range**: `0.1` to `5.0`
- **Note**: Only applies to `"tone"` type sounds

## Usage

### Apply a Configuration
```bash
# Copy a configuration example to your config directory
cp examples/config_beep.ini ~/.voicerecorder/config.ini

# Or use with the --config flag
voice-recorder start --config examples/config_quiet.ini
```

### Test Sound Configurations
```bash
# Test the beep configuration
python -c "
import sys; sys.path.insert(0, 'src')
from voice_recorder.domain.models import SoundConfig, SoundType
from voice_recorder.infrastructure.audio_feedback import SystemAudioFeedback
import time

# Test beep configuration
config = SoundConfig(enabled=True, sound_type=SoundType.BEEP)
feedback = SystemAudioFeedback(config)
print('Testing beep sound...')
feedback.play_start_beep()
time.sleep(1)
feedback.play_stop_beep()
print('Beep test completed!')
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
   - For offline use: `config_local_whisper.ini`
   - For best accuracy: `config_openai_whisper.ini`

2. **Choose your sound preference**:
   - For quiet operation: `config_quiet.ini` or `config_no_sound.ini`
   - For system compatibility: `config_beep.ini`
   - For custom sounds: `config_custom_tone.ini`
   - For professional use: `config_high_quality.ini`

3. **Apply the configuration**:
   ```bash
   cp examples/config_local_whisper.ini ~/.voicerecorder/config.ini
   voice-recorder start
   ```

## Recommended Combinations

### Quiet Office Environment
- Transcription: `config_local_whisper.ini`
- Sound: `config_quiet.ini`

### Noisy Environment
- Transcription: `config_openai_whisper.ini`
- Sound: `config_custom_tone.ini` (higher volume)

### System Compatibility Focus
- Transcription: `config_local_whisper.ini`
- Sound: `config_beep.ini`

### Maximum Privacy
- Transcription: `config_local_whisper.ini`
- Sound: `config_no_sound.ini`

### Professional Use
- Transcription: `config_openai_whisper.ini`
- Sound: `config_high_quality.ini`

## Troubleshooting

### No Sound Heard
1. Check if sound is enabled: `voice-recorder status`
2. Verify system volume is not muted
3. Try the beep configuration for system compatibility
4. Check if PyAudio is properly installed

### Sound Too Loud/Quiet
1. Adjust the `volume` parameter (0.0 to 1.0)
2. Try different `sound_type` values
3. Use system volume control for beep sounds

### Sound Quality Issues
1. Ensure PyAudio is installed: `pip install pyaudio`
2. Try different frequency ranges
3. Adjust duration for better clarity

### Configuration Issues
1. Verify INI file format is correct
2. Check file permissions: `ls -la ~/.voicerecorder/`
3. Use `voice-recorder status` to verify current settings
4. Try `voice-recorder init` to reset configuration

## Recommended Settings by Environment

### For Quiet Environments
- Use `config_quiet.ini` or `config_no_sound.ini`
- Volume: 0.05-0.10
- Duration: 0.2 seconds

### For Noisy Environments
- Use `config_custom_tone.ini`
- Volume: 0.25-0.50
- Duration: 0.4-0.5 seconds

### For System Compatibility
- Use `config_beep.ini`
- Works on all systems
- Uses system volume control

### For High-Quality Audio
- Use `config_high_quality.ini`
- Volume: 0.30
- Frequency: 800Hz-1200Hz
- Duration: 0.5 seconds 