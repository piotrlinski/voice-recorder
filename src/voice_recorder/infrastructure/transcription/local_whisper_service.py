"""
Local Whisper transcription service implementation.
"""

import os
import warnings
from typing import Optional

from rich.console import Console
from rich.text import Text
from rich.panel import Panel

from ...domain.models import TranscriptionConfig, TranscriptionResult


class LocalWhisperTranscriptionService:
    """Local Whisper transcription service implementation."""

    def __init__(self, config: TranscriptionConfig):
        self.config = config
        self.console = Console()
        self.model = None
        
        try:
            import whisper
            
            # Suppress FP16 warning
            warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")
            
            # Load the model
            self.model = whisper.load_model(config.model_name)
            
            # Only show Rich output if not in test environment
            if not os.getenv('PYTEST_CURRENT_TEST'):
                model_text = Text()
                model_text.append(f"✅ Local Whisper model '{config.model_name}' loaded successfully", style="bold green")
                model_text.append(" (FP32)", style="cyan")
                
                model_panel = Panel(
                    model_text,
                    title="[bold green]Local Model Ready[/bold green]",
                    border_style="green",
                    padding=(0, 1)
                )
                self.console.print(model_panel)
            
        except ImportError:
            error_text = Text()
            error_text.append("❌ openai-whisper library not available", style="bold red")
            error_text.append("\n💡 Install with: pip install openai-whisper", style="yellow")
            
            error_panel = Panel(
                error_text,
                title="[bold red]Local Model Error[/bold red]",
                border_style="red",
                padding=(0, 1)
            )
            self.console.print(error_panel)
            raise RuntimeError("openai-whisper library not available")
        except Exception as e:
            error_text = Text()
            error_text.append(f"❌ Local Whisper initialization failed: {e}", style="bold red")
            
            error_panel = Panel(
                error_text,
                title="[bold red]Local Model Error[/bold red]",
                border_style="red",
                padding=(0, 1)
            )
            self.console.print(error_panel)
            raise RuntimeError(f"Local Whisper initialization failed: {e}")

    def transcribe(self, audio_file_path: str) -> Optional[TranscriptionResult]:
        """Transcribe audio file using local Whisper."""
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        if not self.model:
            error_text = Text()
            error_text.append("❌ Whisper model not loaded", style="bold red")
            
            error_panel = Panel(
                error_text,
                title="[bold red]Model Error[/bold red]",
                border_style="red",
                padding=(0, 1)
            )
            self.console.print(error_panel)
            return None
        
        try:
            # Suppress FP16 warning during transcription
            warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")
            
            # Transcribe using local Whisper
            result = self.model.transcribe(
                audio_file_path,
                fp16=False,  # Use FP32 for CPU compatibility
                language="en"
            )
            
            if result and result.get("text", "").strip():
                transcription_result = TranscriptionResult(
                    text=result["text"].strip(),
                    confidence=result.get("confidence", None),
                    duration=result.get("duration", None)
                )
                
                # Only show Rich output if not in test environment
                if not os.getenv('PYTEST_CURRENT_TEST'):
                    success_text = Text()
                    success_text.append("✅ Local transcription completed successfully", style="bold green")
                    
                    success_panel = Panel(
                        success_text,
                        title="[bold green]Local Transcription Success[/bold green]",
                        border_style="green",
                        padding=(0, 1)
                    )
                    self.console.print(success_panel)
                
                return transcription_result
            else:
                error_text = Text()
                error_text.append("⚠️ No transcription result generated", style="bold yellow")
                
                error_panel = Panel(
                    error_text,
                    title="[bold yellow]Local Transcription Issue[/bold yellow]",
                    border_style="yellow",
                    padding=(0, 1)
                )
                self.console.print(error_panel)
                return None
                
        except Exception as e:
            error_text = Text()
            error_text.append(f"❌ Local transcription error: {e}", style="bold red")
            
            error_panel = Panel(
                error_text,
                title="[bold red]Local Transcription Error[/bold red]",
                border_style="red",
                padding=(0, 1)
            )
            self.console.print(error_panel)
            return None 