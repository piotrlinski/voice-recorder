"""
Audio feedback infrastructure implementations.
"""

import os
import struct
import tempfile
import subprocess
from typing import Optional
import math

from rich.panel import Panel
from rich.text import Text

from ..domain.interfaces import AudioFeedback, ConsoleInterface
from ..domain.models import SoundConfig, SoundType


class SystemAudioFeedback(AudioFeedback):
    """System audio feedback implementation."""

    def __init__(self, sound_config: Optional[SoundConfig] = None, console: ConsoleInterface | None = None):
        """Initialize audio feedback service."""
        self.sound_config = sound_config or SoundConfig()
        self.console = console
        self.pyaudio_available = False
        self.pyaudio = None
        
        # Try to initialize PyAudio for audio playback
        try:
            import pyaudio
            self.pyaudio = pyaudio.PyAudio()
            self.pyaudio_available = True
        except ImportError:
            if self.console:
                self.console.print_warning("PyAudio not available - using system beep")
        except Exception as e:
            if self.console:
                self.console.print_warning(f"PyAudio initialization failed: {e}")

    def _generate_tone(self, frequency: float, duration: float, volume: float = None) -> bytes:
        """Generate a simple sine wave tone."""
        if volume is None:
            volume = self.sound_config.volume
        
        sample_rate = 44100
        num_samples = int(sample_rate * duration)
        
        audio_data = bytearray()
        for i in range(num_samples):
            # Generate sine wave
            t = i / sample_rate
            sine_value = math.sin(2.0 * math.pi * frequency * t)
            # Convert to 16-bit integer and apply volume
            sample = int(sine_value * volume * 32767)
            # Ensure sample is within valid range
            sample = max(-32768, min(32767, sample))
            audio_data.extend(struct.pack('<h', sample))
        
        return bytes(audio_data)

    def _generate_sweep_tone(self, start_freq: float, end_freq: float, duration: float, volume: float = None) -> bytes:
        """Generate a frequency sweep tone."""
        if volume is None:
            volume = self.sound_config.volume
        
        sample_rate = 44100
        num_samples = int(sample_rate * duration)
        
        audio_data = bytearray()
        for i in range(num_samples):
            # Calculate current frequency (linear sweep)
            progress = i / num_samples
            current_freq = start_freq + (end_freq - start_freq) * progress
            
            # Generate sine wave at current frequency
            t = i / sample_rate
            sine_value = math.sin(2.0 * math.pi * current_freq * t)
            # Convert to 16-bit integer and apply volume
            sample = int(sine_value * volume * 32767)
            # Ensure sample is within valid range
            sample = max(-32768, min(32767, sample))
            audio_data.extend(struct.pack('<h', sample))
        
        return bytes(audio_data)

    def _play_audio(self, audio_data: bytes) -> None:
        """Play audio data using PyAudio."""
        if not self.pyaudio_available or self.pyaudio is None:
            # Fallback to system beep
            print("\a", end="", flush=True)
            return
        
        try:
            # Create temporary WAV file
            temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            temp_file_path = temp_file.name
            temp_file.close()
            
            # Write WAV file
            import wave
            with wave.open(temp_file_path, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(44100)  # Sample rate
                wav_file.writeframes(audio_data)
            
            # Play audio using afplay (macOS)
            subprocess.run(["afplay", temp_file_path], check=True, capture_output=True)
            
            # Clean up
            try:
                os.unlink(temp_file_path)
            except:
                pass
                
        except Exception as e:
            if self.console:
                self.console.print_warning(f"Audio playback failed: {e}")
            # Fallback to system beep
            print("\a", end="", flush=True)

    def play_start_beep(self) -> None:
        """Play start recording beep."""
        if not self.sound_config.enabled or self.sound_config.sound_type == SoundType.NONE:
            return
            
        try:
            if self.sound_config.sound_type == SoundType.TONE:
                # Generate ascending tone
                audio_data = self._generate_sweep_tone(
                    self.sound_config.start_frequency,
                    self.sound_config.end_frequency,
                    self.sound_config.duration
                )
                self._play_audio(audio_data)
                
                if self.console:
                    self.console.print_success("🔊 Start recording sound played")
            elif self.sound_config.sound_type == SoundType.BEEP:
                # Simple system beep
                print("\a", end="", flush=True)
                
                if self.console:
                    self.console.print_success("🔊 Start recording beep played")
            
        except Exception as e:
            if self.console:
                self.console.print_error(f"Start beep failed: {e}")
            # Fallback to system beep
            print("\a", end="", flush=True)

    def play_stop_beep(self) -> None:
        """Play stop recording beep."""
        if not self.sound_config.enabled or self.sound_config.sound_type == SoundType.NONE:
            return
            
        try:
            if self.sound_config.sound_type == SoundType.TONE:
                # Generate descending tone
                audio_data = self._generate_sweep_tone(
                    self.sound_config.end_frequency,
                    self.sound_config.start_frequency,
                    self.sound_config.duration
                )
                self._play_audio(audio_data)
                
                if self.console:
                    self.console.print_success("🔊 Stop recording sound played")
            elif self.sound_config.sound_type == SoundType.BEEP:
                # Simple system beep
                print("\a", end="", flush=True)
                
                if self.console:
                    self.console.print_success("🔊 Stop recording beep played")
            
        except Exception as e:
            if self.console:
                self.console.print_error(f"Stop beep failed: {e}")
            # Fallback to system beep
            print("\a", end="", flush=True)

    def __del__(self):
        """Clean up PyAudio resources."""
        if self.pyaudio:
            try:
                self.pyaudio.terminate()
            except:
                pass



