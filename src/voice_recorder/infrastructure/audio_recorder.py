"""
Audio recording infrastructure implementations.
"""

import os
import sys
import tempfile
from contextlib import contextmanager
from typing import Any, Dict, Optional

from ..domain.interfaces import AudioRecorderInterface, ConsoleInterface
from ..domain.models import AudioConfig


class PyAudioRecorder(AudioRecorderInterface):
    """PyAudio-based audio recorder implementation with simple system beeps."""

    @contextmanager
    def _suppress_pyaudio_noise(self):
        """Context manager to suppress PyAudio's noisy output during initialization."""
        # Save original stderr and stdout
        original_stderr = sys.stderr
        original_stdout = sys.stdout
        
        try:
            # Redirect to devnull to suppress PyAudio noise
            with open(os.devnull, 'w') as devnull:
                sys.stderr = devnull
                sys.stdout = devnull
                yield
        finally:
            # Always restore original streams
            sys.stderr = original_stderr
            sys.stdout = original_stdout

    def __init__(self, console: ConsoleInterface | None = None):
        """Initialize PyAudio recorder."""
        self.console = console
        self.pyaudio_available = False
        self.pyaudio: Optional[Any] = None
        self.pa_continue: Optional[Any] = None
        self.pa_int16: Optional[Any] = None
        self.audio_streams: Dict[str, Any] = {}
        self.audio_frames: Dict[str, list] = {}
        self._session_counter = 0  # Use counter instead of len() to avoid ID reuse

        # Try to initialize PyAudio with complete noise suppression
        try:
            import pyaudio
            
            # Set environment variables to potentially disable system beeps
            original_env = {}
            suppress_env_vars = {
                'ALSA_NOBEEP': '1',
                'PA_ALSA_PLUGHW': '0',
                'PULSE_RUNTIME_PATH': '/dev/null',
                'PULSE_SERVER': 'none',
                'TERM': 'dumb',  # Disable terminal capabilities
            }
            
            # Save original environment and set suppression variables
            for key, value in suppress_env_vars.items():
                original_env[key] = os.environ.get(key)
                os.environ[key] = value

            try:
                # Suppress PyAudio's noisy initialization
                with self._suppress_pyaudio_noise():
                    # Try to monkey-patch potential beep functions before initializing
                    try:
                        # Disable terminal bell by redirecting it to nothing
                        os.system('stty -echo 2>/dev/null || true')
                    except:
                        pass
                    
                    self.pyaudio = pyaudio.PyAudio()
                    
                    # Try to set PyAudio to use Core Audio exclusively if on macOS
                    if hasattr(self.pyaudio, 'get_host_api_count'):
                        try:
                            for i in range(self.pyaudio.get_host_api_count()):
                                api_info = self.pyaudio.get_host_api_info_by_index(i)
                                if api_info['name'] == 'Core Audio':
                                    # Store the Core Audio host API index for later use
                                    self._core_audio_host_api = i
                                    break
                        except:
                            pass
            finally:
                # Restore original environment
                for key, original_value in original_env.items():
                    if original_value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = original_value
                        
                # Re-enable terminal echo
                try:
                    os.system('stty echo 2>/dev/null || true')
                except:
                    pass
                
            self.pa_continue = pyaudio.paContinue
            self.pa_int16 = pyaudio.paInt16
            self.pyaudio_available = True
            
            # Store reference to pyaudio module for host API queries
            self._pyaudio_module = pyaudio
            self._core_audio_host_api = getattr(self, '_core_audio_host_api', None)
        except ImportError:
            if self.console:
                self.console.error("PyAudio not available - audio recording disabled")
        except Exception as e:
            if self.console:
                self.console.error(f"PyAudio initialization failed: {e}")



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
        """Start recording with PyAudio."""
        if not self.pyaudio_available or self.pyaudio is None:
            raise RuntimeError("PyAudio not available")
        
        # Generate unique session ID using counter
        self._session_counter += 1
        session_id = f"pyaudio_{self._session_counter}"
        
        try:
            # Initialize audio frames for this session
            self.audio_frames[session_id] = []
            # Create audio callback for this session
            callback = self._create_audio_callback(session_id)
            
            # Simple stream creation with PyAudio noise suppression
            with self._suppress_pyaudio_noise():
                # Build basic stream parameters
                stream_params = {
                    'format': self.pa_int16,
                    'channels': config.channels,
                    'rate': config.sample_rate,
                    'input': True,
                    'frames_per_buffer': config.chunk_size,
                    'stream_callback': callback,
                    'start': False,  # Don't auto-start
                }
                
                # Create and start stream - this will produce natural system beep
                stream = self.pyaudio.open(**stream_params)
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