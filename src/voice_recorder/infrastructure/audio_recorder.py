"""
Audio recorder infrastructure implementations.
"""

import os
import tempfile
import wave
from typing import Any, Dict, Optional

from rich.console import Console
from rich.text import Text
from rich.panel import Panel

from ..domain.models import AudioConfig


class PyAudioRecorder:
    """PyAudio-based audio recorder implementation."""

    def __init__(self):
        self.console = Console()
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
            
            # Only show Rich output if not in test environment
            if not os.getenv('PYTEST_CURRENT_TEST'):
                init_text = Text()
                init_text.append("✅ PyAudio initialized successfully", style="bold green")
                
                init_panel = Panel(
                    init_text,
                    title="[bold green]Audio System Ready[/bold green]",
                    border_style="green",
                    padding=(0, 1)
                )
                self.console.print(init_panel)
        except ImportError:
            error_text = Text()
            error_text.append("❌ PyAudio not available", style="bold red")
            error_text.append("\n💡 Install with: pip install pyaudio", style="yellow")
            
            error_panel = Panel(
                error_text,
                title="[bold red]Audio System Error[/bold red]",
                border_style="red",
                padding=(0, 1)
            )
            self.console.print(error_panel)
        except Exception as e:
            error_text = Text()
            error_text.append(f"❌ PyAudio initialization failed: {e}", style="bold red")
            
            error_panel = Panel(
                error_text,
                title="[bold red]Audio System Error[/bold red]",
                border_style="red",
                padding=(0, 1)
            )
            self.console.print(error_panel)

    def _create_audio_callback(self, session_id: str):
        """Create a proper audio callback closure."""

        def audio_callback(
            in_data: bytes, frame_count: int, time_info: Dict[str, Any], status: Any
        ) -> tuple[bytes, Any]:
            try:
                if session_id in self.audio_frames:
                    self.audio_frames[session_id].append(in_data)
            except Exception as e:
                error_text = Text()
                error_text.append(f"⚠️ Audio callback error: {e}", style="bold yellow")
                
                error_panel = Panel(
                    error_text,
                    title="[bold yellow]Audio Callback Error[/bold yellow]",
                    border_style="yellow",
                    padding=(0, 1)
                )
                self.console.print(error_panel)
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
            
            # Only show Rich output if not in test environment
            if not os.getenv('PYTEST_CURRENT_TEST'):
                start_text = Text()
                start_text.append("🎙️ PyAudio recording started", style="bold green")
                start_text.append(f" (Session: {session_id})", style="cyan")
                
                start_panel = Panel(
                    start_text,
                    title="[bold green]Recording Started[/bold green]",
                    border_style="green",
                    padding=(0, 1)
                )
                self.console.print(start_panel)
            
            return session_id
        except Exception as e:
            error_text = Text()
            error_text.append(f"❌ PyAudio recording failed: {e}", style="bold red")
            
            error_panel = Panel(
                error_text,
                title="[bold red]Recording Error[/bold red]",
                border_style="red",
                padding=(0, 1)
            )
            self.console.print(error_panel)
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
                
                # Only show Rich output if not in test environment
                if not os.getenv('PYTEST_CURRENT_TEST'):
                    capture_text = Text()
                    capture_text.append("📊 Audio frames captured: ", style="bold blue")
                    capture_text.append(f"{frames_count} frames, {total_bytes} bytes", style="cyan")
                    
                    capture_panel = Panel(
                        capture_text,
                        title="[bold blue]Audio Capture[/bold blue]",
                        border_style="blue",
                        padding=(0, 1)
                    )
                    self.console.print(capture_panel)
                
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
                file_size = os.path.getsize(temp_file.name)
                
                # Only show Rich output if not in test environment
                if not os.getenv('PYTEST_CURRENT_TEST'):
                    file_text = Text()
                    file_text.append("💾 Audio file created: ", style="bold green")
                    file_text.append(f"{temp_file.name}", style="cyan")
                    file_text.append(f", size: {file_size} bytes", style="cyan")
                    
                    file_panel = Panel(
                        file_text,
                        title="[bold green]File Saved[/bold green]",
                        border_style="green",
                        padding=(0, 1)
                    )
                    self.console.print(file_panel)
                
                # Clean up frames
                del self.audio_frames[session_id]
                
                # Only show Rich output if not in test environment
                if not os.getenv('PYTEST_CURRENT_TEST'):
                    stop_text = Text()
                    stop_text.append("🛑 PyAudio recording stopped", style="bold yellow")
                    stop_text.append(f" (Session: {session_id})", style="cyan")
                    
                    stop_panel = Panel(
                        stop_text,
                        title="[bold yellow]Recording Stopped[/bold yellow]",
                        border_style="yellow",
                        padding=(0, 1)
                    )
                    self.console.print(stop_panel)
                
                return temp_file.name
            else:
                no_frames_text = Text()
                no_frames_text.append("⚠️ No audio frames recorded", style="bold yellow")
                no_frames_text.append(f" (Session: {session_id})", style="cyan")
                
                no_frames_panel = Panel(
                    no_frames_text,
                    title="[bold yellow]Recording Issue[/bold yellow]",
                    border_style="yellow",
                    padding=(0, 1)
                )
                self.console.print(no_frames_panel)
                return None
        except Exception as e:
            error_text = Text()
            error_text.append(f"❌ PyAudio stop recording failed: {e}", style="bold red")
            
            error_panel = Panel(
                error_text,
                title="[bold red]Stop Error[/bold red]",
                border_style="red",
                padding=(0, 1)
            )
            self.console.print(error_panel)
            return None

    def is_recording(self, session_id: str) -> bool:
        """Check if recording is active."""
        return session_id in self.audio_streams
