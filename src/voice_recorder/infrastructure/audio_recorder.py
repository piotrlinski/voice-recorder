"""
Audio recording infrastructure implementations.
"""

import os
import tempfile
from typing import Any, Dict, Optional

from ..domain.interfaces import AudioRecorderInterface, ConsoleInterface
from ..domain.models import AudioConfig


class PyAudioRecorder(AudioRecorderInterface):
    """PyAudio-based audio recorder implementation."""

    def __init__(self, console: ConsoleInterface | None = None):
        """Initialize PyAudio recorder."""
        self.console = console
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
                self.console.print_error("PyAudio not available - audio recording disabled")
        except Exception as e:
            if self.console:
                self.console.print_error(f"PyAudio initialization failed: {e}")

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
                    self.console.print_error(f"⚠️ Audio callback error: {e}")
            return (in_data, self.pa_continue)

        return audio_callback

    def start_recording(self, config: AudioConfig) -> str:
        """Start recording with PyAudio."""
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
                self.console.print_success(f"🎙️ PyAudio recording started (Session: {session_id})")
            
            return session_id
        except Exception as e:
            if self.console:
                self.console.print_error(f"PyAudio recording failed: {e}")
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
                    self.console.print_warning("No audio frames recorded")
                return None
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(
                suffix=".wav", delete=False, dir=tempfile.gettempdir()
            )
            temp_file_path = temp_file.name
            temp_file.close()
            
            # Save audio to file
            import wave
            with wave.open(temp_file_path, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(self.pyaudio.get_sample_size(self.pa_int16))
                wav_file.setframerate(16000)  # Default sample rate
                wav_file.writeframes(b''.join(audio_frames))
            
            # Clean up audio frames
            if session_id in self.audio_frames:
                del self.audio_frames[session_id]
            
            if self.console:
                self.console.print_success(f"Recording saved to: {temp_file_path}")
            
            return temp_file_path
        except Exception as e:
            if self.console:
                self.console.print_error(f"Failed to save recording: {e}")
            return None

    def is_recording(self, session_id: str) -> bool:
        """Check if recording is active."""
        return session_id in self.audio_streams
