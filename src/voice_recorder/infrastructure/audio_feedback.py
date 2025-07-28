"""
Audio feedback infrastructure implementations.
"""

import os
import math
import sys
import time
from typing import Optional

import pyaudio
from rich.console import Console
from rich.text import Text
from rich.panel import Panel

from ..domain.models import SoundConfig, SoundType


class SystemAudioFeedback:
    """System-based audio feedback implementation using PyAudio."""

    def __init__(self, sound_config: Optional[SoundConfig] = None):
        self.console = Console()
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
            error_text = Text()
            error_text.append(f"❌ Audio playback failed: {e}", style="bold red")
            
            error_panel = Panel(
                error_text,
                title="[bold red]Audio Playback Error[/bold red]",
                border_style="red",
                padding=(0, 1)
            )
            self.console.print(error_panel)
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
                
                # Only show Rich output if not in test environment
                if not os.getenv('PYTEST_CURRENT_TEST'):
                    start_text = Text()
                    start_text.append("🔊 Start recording sound played", style="bold green")
                    
                    start_panel = Panel(
                        start_text,
                        title="[bold green]Start Sound[/bold green]",
                        border_style="green",
                        padding=(0, 1)
                    )
                    self.console.print(start_panel)
            elif self.sound_config.sound_type == SoundType.BEEP:
                # Simple system beep
                print("\a", end="", flush=True)
                
                # Only show Rich output if not in test environment
                if not os.getenv('PYTEST_CURRENT_TEST'):
                    beep_text = Text()
                    beep_text.append("🔊 Start recording beep played", style="bold green")
                    
                    beep_panel = Panel(
                        beep_text,
                        title="[bold green]Start Beep[/bold green]",
                        border_style="green",
                        padding=(0, 1)
                    )
                    self.console.print(beep_panel)
            
        except Exception as e:
            error_text = Text()
            error_text.append(f"❌ Start beep failed: {e}", style="bold red")
            
            error_panel = Panel(
                error_text,
                title="[bold red]Start Sound Error[/bold red]",
                border_style="red",
                padding=(0, 1)
            )
            self.console.print(error_panel)
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
                
                # Only show Rich output if not in test environment
                if not os.getenv('PYTEST_CURRENT_TEST'):
                    stop_text = Text()
                    stop_text.append("🔊 Stop recording sound played", style="bold yellow")
                    
                    stop_panel = Panel(
                        stop_text,
                        title="[bold yellow]Stop Sound[/bold yellow]",
                        border_style="yellow",
                        padding=(0, 1)
                    )
                    self.console.print(stop_panel)
            elif self.sound_config.sound_type == SoundType.BEEP:
                # Simple system beep
                print("\a", end="", flush=True)
                
                # Only show Rich output if not in test environment
                if not os.getenv('PYTEST_CURRENT_TEST'):
                    beep_text = Text()
                    beep_text.append("🔊 Stop recording beep played", style="bold yellow")
                    
                    beep_panel = Panel(
                        beep_text,
                        title="[bold yellow]Stop Beep[/bold yellow]",
                        border_style="yellow",
                        padding=(0, 1)
                    )
                    self.console.print(beep_panel)
            
        except Exception as e:
            error_text = Text()
            error_text.append(f"❌ Stop beep failed: {e}", style="bold red")
            
            error_panel = Panel(
                error_text,
                title="[bold red]Stop Sound Error[/bold red]",
                border_style="red",
                padding=(0, 1)
            )
            self.console.print(error_panel)
            # Fallback to system beep
            print("\a", end="", flush=True)

    def __del__(self):
        """Clean up PyAudio resources."""
        try:
            if hasattr(self, 'pyaudio'):
                self.pyaudio.terminate()
        except:
            pass



