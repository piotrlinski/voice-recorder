# Sound Configuration Examples

This directory contains various configuration examples demonstrating different sound feedback options for the voice recorder application.

## Configuration Files

### 1. `config_beep.json` - System Beep Sounds
**Use Case**: Simple, system-native beep sounds
```json
{
  "sound_config": {
    "enabled": true,
    "sound_type": "beep",
    "volume": 0.15,
    "start_frequency": 800.0,
    "end_frequency": 1200.0,
    "duration": 0.3
  }
}
```
**Features**:
- Uses system beep (`\a`) for audio feedback
- Compatible with all operating systems
- Minimal resource usage
- Volume setting is ignored (uses system volume)

### 2. `config_no_sound.json` - Silent Operation
**Use Case**: No audio feedback during recording
```json
{
  "sound_config": {
    "enabled": false,
    "sound_type": "none",
    "volume": 0.15,
    "start_frequency": 800.0,
    "end_frequency": 1200.0,
    "duration": 0.3
  }
}
```
**Features**:
- Completely silent operation
- No audio feedback when recording starts/stops
- Useful for quiet environments or when audio feedback is not desired
- All other settings are ignored when disabled

### 3. `config_custom_tone.json` - Custom Tone Settings
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
- Higher volume (25% vs default 15%)
- Lower frequency range (600Hz-1000Hz vs 800Hz-1200Hz)
- Longer duration (0.4s vs 0.3s)
- More noticeable audio feedback

### 4. `config_quiet_tone.json` - Very Quiet Tones
**Use Case**: Minimal audio feedback
```json
{
  "sound_config": {
    "enabled": true,
    "sound_type": "tone",
    "volume": 0.05,
    "start_frequency": 800.0,
    "end_frequency": 1200.0,
    "duration": 0.2
  }
}
```
**Features**:
- Very low volume (5% vs default 15%)
- Shorter duration (0.2s vs 0.3s)
- Standard frequency range
- Barely audible feedback

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

## Usage Examples

### Apply a Configuration
```bash
# Copy a configuration example to your config directory
cp examples/config_beep.json ~/.voicerecorder/config.json

# Or use with the --config flag
voice-recorder start --config examples/config_quiet_tone.json
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

# Show current sound configuration
voice-recorder status
```

## Recommended Settings

### For Quiet Environments
- Use `config_quiet_tone.json` or `config_no_sound.json`
- Volume: 0.05-0.10
- Duration: 0.2 seconds

### For Noisy Environments
- Use `config_custom_tone.json`
- Volume: 0.25-0.50
- Duration: 0.4-0.5 seconds

### For System Compatibility
- Use `config_beep.json`
- Works on all systems
- Uses system volume control

### For High-Quality Audio
- Use default tone settings
- Volume: 0.15
- Frequency: 800Hz-1200Hz
- Duration: 0.3 seconds

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