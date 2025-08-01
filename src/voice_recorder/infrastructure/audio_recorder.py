"""
Audio recording infrastructure implementations.
"""

import os
import tempfile
import math
import struct
import subprocess
from typing import Any, Dict, Optional

from ..domain.interfaces import AudioRecorderInterface, ConsoleInterface
from ..domain.models import AudioConfig, SoundConfig, SoundType


class PyAudioRecorder(AudioRecorderInterface):
    """PyAudio-based audio recorder implementation with built-in audio feedback."""

    def __init__(self, console: ConsoleInterface | None = None, sound_config: Optional[SoundConfig] = None):
        """Initialize PyAudio recorder."""
        self.console = console
        self.sound_config = sound_config or SoundConfig()
        self.pyaudio_available = False
        self.pyaudio: Optional[Any] = None
        self.pa_continue: Optional[Any] = None
        self.pa_int16: Optional[Any] = None
        self.audio_streams: Dict[str, Any] = {}
        self.audio_frames: Dict[str, list] = {}

        # Try to initialize PyAudio
        try:
            import pyaudio

            self.pyaudio = pyaudio.PyAudio()
            self.pa_continue = pyaudio.paContinue
            self.pa_int16 = pyaudio.paInt16
            self.pyaudio_available = True
        except ImportError:
            if self.console:
                self.console.error("PyAudio not available - audio recording disabled")
        except Exception as e:
            if self.console:
                self.console.error(f"PyAudio initialization failed: {e}")

    def _generate_tone(self, frequency: float, duration: float, volume: float = None) -> bytes:
        """Generate a tone at the specified frequency."""
        if volume is None:
            volume = self.sound_config.volume

        # Convert volume from 0-100 to 0.0-1.0 range
        volume_scale = volume / 100.0

        sample_rate = 44100
        num_samples = int(sample_rate * duration)

        audio_data = bytearray()
        for i in range(num_samples):
            # Generate sine wave
            t = i / sample_rate
            sine_value = math.sin(2.0 * math.pi * frequency * t)
            # Convert to 16-bit integer and apply volume
            sample = int(sine_value * volume_scale * 32767)
            # Ensure sample is within valid range
            sample = max(-32768, min(32767, sample))
            audio_data.extend(struct.pack("<h", sample))

        return bytes(audio_data)

    def _generate_sweep_tone(self, start_freq: float, end_freq: float, duration: float, volume: float = None) -> bytes:
        """Generate a frequency sweep tone."""
        if volume is None:
            volume = self.sound_config.volume

        # Convert volume from 0-100 to 0.0-1.0 range
        volume_scale = volume / 100.0

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
            sample = int(sine_value * volume_scale * 32767)
            # Ensure sample is within valid range
            sample = max(-32768, min(32767, sample))
            audio_data.extend(struct.pack("<h", sample))

        return bytes(audio_data)

    def _play_audio(self, audio_data: bytes) -> None:
        """Play audio data using system command."""
        if not self.sound_config.enabled:
            return

        try:
            # Create temporary WAV file
            temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            temp_file_path = temp_file.name
            temp_file.close()

            # Write WAV file
            import wave

            with wave.open(temp_file_path, "wb") as wav_file:
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
                self.console.warning(f"Audio playback failed: {e}")
            # Fallback to system beep
            print("\a", end="", flush=True)

    def play_start_beep(self, recording_type: str = "basic") -> None:
        """Play start recording beep."""
        if not self.sound_config.enabled:
            return

        try:
            if recording_type == "basic":
                if self.sound_config.basic_sound_type == SoundType.TONE:
                    # Generate ascending sweep tone
                    audio_data = self._generate_sweep_tone(
                        self.sound_config.basic_start_frequency,
                        self.sound_config.basic_end_frequency,
                        self.sound_config.duration,
                    )
                    self._play_audio(audio_data)
                elif self.sound_config.basic_sound_type == SoundType.BEEP:
                    print("\a", end="", flush=True)
            else:  # enhanced
                if self.sound_config.enhanced_sound_type == SoundType.TONE:
                    # Generate ascending sweep tone
                    audio_data = self._generate_sweep_tone(
                        self.sound_config.enhanced_start_frequency,
                        self.sound_config.enhanced_end_frequency,
                        self.sound_config.duration,
                    )
                    self._play_audio(audio_data)
                elif self.sound_config.enhanced_sound_type == SoundType.BEEP:
                    print("\a", end="", flush=True)

        except Exception as e:
            if self.console:
                self.console.error(f"Start beep failed: {e}")

    def play_stop_beep(self, recording_type: str = "basic") -> None:
        """Play stop recording beep."""
        if not self.sound_config.enabled:
            return

        try:
            if recording_type == "basic":
                if self.sound_config.basic_sound_type == SoundType.TONE:
                    # Generate descending sweep tone
                    audio_data = self._generate_sweep_tone(
                        self.sound_config.basic_end_frequency,
                        self.sound_config.basic_start_frequency,
                        self.sound_config.duration,
                    )
                    self._play_audio(audio_data)
                elif self.sound_config.basic_sound_type == SoundType.BEEP:
                    print("\a", end="", flush=True)
            else:  # enhanced
                if self.sound_config.enhanced_sound_type == SoundType.TONE:
                    # Generate descending sweep tone
                    audio_data = self._generate_sweep_tone(
                        self.sound_config.enhanced_end_frequency,
                        self.sound_config.enhanced_start_frequency,
                        self.sound_config.duration,
                    )
                    self._play_audio(audio_data)
                elif self.sound_config.enhanced_sound_type == SoundType.BEEP:
                    print("\a", end="", flush=True)

        except Exception as e:
            if self.console:
                self.console.error(f"Stop beep failed: {e}")

    def _create_audio_callback(self, session_id: str):
        """Create a proper audio callback closure."""

        def audio_callback(
            in_data: bytes, frame_count: int, time_info: Dict[str, Any], status: Any
        ) -> tuple[bytes, Any]:
            try:
                if session_id in self.audio_frames:
                    self.audio_frames[session_id].append(in_data)
            except Exception as e:
                if self.console:
                    self.console.error(f"Audio callback error: {e}")
            return (in_data, self.pa_continue)

        return audio_callback

    def start_recording(self, config: AudioConfig) -> str:
        """Start recording with PyAudio and play start beep."""
        if not self.pyaudio_available or self.pyaudio is None:
            raise RuntimeError("PyAudio not available")
        session_id = f"pyaudio_{len(self.audio_streams)}"
        try:
            # Initialize audio frames for this session
            self.audio_frames[session_id] = []
            # Create audio callback for this session
            callback = self._create_audio_callback(session_id)
            # Create audio stream
            stream = self.pyaudio.open(
                format=self.pa_int16,
                channels=config.channels,
                rate=config.sample_rate,
                input=True,
                frames_per_buffer=config.chunk_size,
                stream_callback=callback,
            )
            self.audio_streams[session_id] = stream
            stream.start_stream()

            if self.console:
                self.console.info(f"PyAudio recording started (Session: {session_id})")

            return session_id
        except Exception as e:
            if self.console:
                self.console.error(f"PyAudio recording failed: {e}")
            raise

    def stop_recording(self, session_id: str) -> Optional[str]:
        """Stop recording and save to file."""
        if session_id not in self.audio_streams:
            return None
        try:
            # Stop the stream
            stream = self.audio_streams[session_id]
            if hasattr(stream, "stop_stream"):
                stream.stop_stream()
            if hasattr(stream, "close"):
                stream.close()

            # Remove from active streams
            del self.audio_streams[session_id]

            # Get audio frames
            audio_frames = self.audio_frames.get(session_id, [])
            if not audio_frames:
                if self.console:
                    self.console.warning("No audio frames recorded")
                return None

            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(
                suffix=".wav", delete=False, dir=tempfile.gettempdir()
            )
            temp_file_path = temp_file.name
            temp_file.close()

            # Save audio to file
            import wave

            with wave.open(temp_file_path, "wb") as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(self.pyaudio.get_sample_size(self.pa_int16))
                wav_file.setframerate(16000)  # Default sample rate
                wav_file.writeframes(b"".join(audio_frames))

            # Clean up audio frames
            if session_id in self.audio_frames:
                del self.audio_frames[session_id]

            if self.console:
                self.console.info(f"Recording saved to: {temp_file_path}")

            return temp_file_path
        except Exception as e:
            if self.console:
                self.console.error(f"Failed to save recording: {e}")
            return None

    def is_recording(self, session_id: str) -> bool:
        """Check if recording is active."""
        return session_id in self.audio_streams
