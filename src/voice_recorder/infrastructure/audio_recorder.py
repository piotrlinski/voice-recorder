"""
Audio recorder infrastructure implementations.
"""

import tempfile
import wave
from typing import Any, Dict, Optional

from ..domain.models import AudioConfig


class PyAudioRecorder:
    """PyAudio-based audio recorder implementation."""

    def __init__(self):
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
            print("PyAudio initialized successfully")
        except ImportError:
            print("PyAudio not available")
        except Exception as e:
            print(f"PyAudio initialization failed: {e}")

    def _create_audio_callback(self, session_id: str):
        """Create a proper audio callback closure."""

        def audio_callback(
            in_data: bytes, frame_count: int, time_info: Dict[str, Any], status: Any
        ) -> tuple[bytes, Any]:
            try:
                if session_id in self.audio_frames:
                    self.audio_frames[session_id].append(in_data)
            except Exception as e:
                print(f"Audio callback error: {e}")
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
            print(f"PyAudio recording started (Session: {session_id})")
            return session_id
        except Exception as e:
            print(f"PyAudio recording failed: {e}")
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
            # Remove from tracking
            del self.audio_streams[session_id]
            # Save audio frames to file
            if session_id in self.audio_frames and self.audio_frames[session_id]:
                frames_count = len(self.audio_frames[session_id])
                total_bytes = sum(len(frame) for frame in self.audio_frames[session_id])
                print(f"Audio frames captured: {frames_count} frames, {total_bytes} bytes")
                
                temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
                temp_file.close()
                with wave.open(temp_file.name, "wb") as wf:
                    wf.setnchannels(1)  # Mono
                    if self.pyaudio and self.pa_int16:
                        wf.setsampwidth(self.pyaudio.get_sample_size(self.pa_int16))
                    else:
                        wf.setsampwidth(2)  # Default for 16-bit audio
                    wf.setframerate(16000)
                    wf.writeframes(b"".join(self.audio_frames[session_id]))
                
                # Verify the file was created and has content
                import os
                file_size = os.path.getsize(temp_file.name)
                print(f"Audio file created: {temp_file.name}, size: {file_size} bytes")
                
                # Clean up frames
                del self.audio_frames[session_id]
                print(f"PyAudio recording stopped (Session: {session_id})")
                return temp_file.name
            else:
                print(f"No audio frames recorded for session: {session_id}")
                return None
        except Exception as e:
            print(f"PyAudio stop recording failed: {e}")
            return None

    def is_recording(self, session_id: str) -> bool:
        """Check if recording is active."""
        return session_id in self.audio_streams
