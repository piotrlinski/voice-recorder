"""
Audio feedback infrastructure implementations.
"""

import math
import sys
import time
from typing import Optional

import pyaudio

from ..domain.models import SoundConfig, SoundType


class SystemAudioFeedback:
    """System-based audio feedback implementation using PyAudio."""

    def __init__(self, sound_config: Optional[SoundConfig] = None):
        self.platform = sys.platform
        self.pyaudio = pyaudio.PyAudio()
        self.sample_rate = 44100
        self.chunk_size = 1024
        self.sound_config = sound_config or SoundConfig()

    def _generate_tone(self, frequency: float, duration: float, volume: float = None) -> bytes:
        """Generate a tone with the specified frequency and duration."""
        if volume is None:
            volume = self.sound_config.volume
            
        num_frames = int(self.sample_rate * duration)
        audio_data = []
        
        for i in range(num_frames):
            # Generate sine wave
            sample = math.sin(2 * math.pi * frequency * i / self.sample_rate)
            # Apply volume and convert to 16-bit integer
            sample = int(sample * volume * 32767)
            # Convert to bytes (little-endian)
            audio_data.extend([sample & 0xFF, (sample >> 8) & 0xFF])
        
        return bytes(audio_data)

    def _generate_sweep_tone(self, start_freq: float, end_freq: float, duration: float, volume: float = None) -> bytes:
        """Generate a frequency sweep tone."""
        if volume is None:
            volume = self.sound_config.volume
            
        audio_data = b""
        for i in range(int(self.sample_rate * duration)):
            # Interpolate frequency
            freq = start_freq + (end_freq - start_freq) * i / (self.sample_rate * duration)
            sample = math.sin(2 * math.pi * freq * i / self.sample_rate)
            sample = int(sample * volume * 32767)
            audio_data += bytes([sample & 0xFF, (sample >> 8) & 0xFF])
        
        return audio_data

    def _play_audio(self, audio_data: bytes) -> None:
        """Play audio data through the default output device."""
        try:
            stream = self.pyaudio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                output=True,
                frames_per_buffer=self.chunk_size
            )
            
            # Play the audio in chunks
            for i in range(0, len(audio_data), self.chunk_size * 2):
                chunk = audio_data[i:i + self.chunk_size * 2]
                if chunk:
                    stream.write(chunk)
            
            stream.stop_stream()
            stream.close()
            
        except Exception as e:
            print(f"Audio playback failed: {e}")
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
                print("🔊 Start recording sound played")
            elif self.sound_config.sound_type == SoundType.BEEP:
                # Simple system beep
                print("\a", end="", flush=True)
                print("🔊 Start recording beep played")
            
        except Exception as e:
            print(f"Start beep failed: {e}")
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
                print("🔊 Stop recording sound played")
            elif self.sound_config.sound_type == SoundType.BEEP:
                # Simple system beep
                print("\a", end="", flush=True)
                print("🔊 Stop recording beep played")
            
        except Exception as e:
            print(f"Stop beep failed: {e}")
            # Fallback to system beep
            print("\a", end="", flush=True)

    def __del__(self):
        """Clean up PyAudio resources."""
        try:
            if hasattr(self, 'pyaudio'):
                self.pyaudio.terminate()
        except:
            pass



