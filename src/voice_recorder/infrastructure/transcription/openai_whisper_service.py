"""
OpenAI Whisper transcription service implementation.
"""

import os
from typing import Optional

from rich.console import Console
from rich.text import Text
from rich.panel import Panel

from ...domain.models import TranscriptionConfig, TranscriptionResult


class OpenAITranscriptionService:
    """OpenAI Whisper transcription service implementation."""

    def __init__(self, config: TranscriptionConfig):
        self.config = config
        self.console = Console()
        
        try:
            import openai
            openai.api_key = config.api_key
            api_key = config.api_key or os.getenv('OPENAI_API_KEY')
            self.client = openai.OpenAI(api_key=api_key)
            
            # Only show Rich output if not in test environment
            if not os.getenv('PYTEST_CURRENT_TEST'):
                init_text = Text()
                init_text.append("✅ OpenAI client initialized successfully", style="bold green")
                
                init_panel = Panel(
                    init_text,
                    title="[bold green]OpenAI Service Ready[/bold green]",
                    border_style="green",
                    padding=(0, 1)
                )
                self.console.print(init_panel)
        except ImportError:
            error_text = Text()
            error_text.append("❌ openai library not available", style="bold red")
            error_text.append("\n💡 Install with: pip install openai", style="yellow")
            
            error_panel = Panel(
                error_text,
                title="[bold red]OpenAI Service Error[/bold red]",
                border_style="red",
                padding=(0, 1)
            )
            self.console.print(error_panel)
            raise RuntimeError("openai library not available")

    def transcribe(self, audio_file_path: str) -> Optional[TranscriptionResult]:
        """Transcribe audio file using OpenAI Whisper."""
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        try:
            # Check file size
            file_size = os.path.getsize(audio_file_path)
            
            # Only show Rich output if not in test environment
            if not os.getenv('PYTEST_CURRENT_TEST'):
                size_text = Text()
                size_text.append("📊 Audio file size: ", style="bold blue")
                size_text.append(f"{file_size} bytes", style="cyan")
                
                size_panel = Panel(
                    size_text,
                    title="[bold blue]Processing Audio[/bold blue]",
                    border_style="blue",
                    padding=(0, 1)
                )
                self.console.print(size_panel)
            
            # Transcribe using OpenAI
            with open(audio_file_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model=self.config.model_name,
                    file=audio_file,
                    response_format="text"
                )
            
            if response and response.strip():
                result = TranscriptionResult(
                    text=response.strip(),
                    confidence=None,  # OpenAI doesn't provide confidence scores
                    duration=None
                )
                
                # Only show Rich output if not in test environment
                if not os.getenv('PYTEST_CURRENT_TEST'):
                    success_text = Text()
                    success_text.append("✅ Transcription completed successfully", style="bold green")
                    
                    success_panel = Panel(
                        success_text,
                        title="[bold green]Transcription Success[/bold green]",
                        border_style="green",
                        padding=(0, 1)
                    )
                    self.console.print(success_panel)
                
                return result
            else:
                error_text = Text()
                error_text.append("⚠️ No transcription result received", style="bold yellow")
                
                error_panel = Panel(
                    error_text,
                    title="[bold yellow]Transcription Issue[/bold yellow]",
                    border_style="yellow",
                    padding=(0, 1)
                )
                self.console.print(error_panel)
                return None
                
        except Exception as e:
            error_text = Text()
            error_text.append(f"❌ OpenAI transcription error: {e}", style="bold red")
            
            error_panel = Panel(
                error_text,
                title="[bold red]Transcription Error[/bold red]",
                border_style="red",
                padding=(0, 1)
            )
            self.console.print(error_panel)
            return None 