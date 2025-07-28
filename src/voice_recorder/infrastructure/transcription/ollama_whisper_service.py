"""
Ollama Whisper transcription service implementation.
"""

from ...domain.interfaces import TranscriptionService
from ...domain.models import TranscriptionResult


class OllamaWhisperTranscriptionService(TranscriptionService):
    """Ollama Whisper transcription service implementation."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        """Initialize Ollama Whisper transcription service."""
        self.base_url = base_url
        self.model_name = "whisper"
        try:
            import ollama
            # Configure Ollama client
            ollama.set_host(self.base_url)
            
            # Test connection to Ollama
            try:
                models = ollama.list()
                print(f"Ollama server connected at {self.base_url}")
                print(f"Available models: {[model['name'] for model in models['models']]}")
            except Exception as e:
                raise RuntimeError(f"Ollama server not accessible at {self.base_url}: {e}")
        except ImportError:
            raise RuntimeError("ollama library not available. Install with: pip install ollama")
        except Exception as e:
            raise RuntimeError(f"Ollama connection failed: {e}")

    def transcribe(self, audio_file_path: str) -> TranscriptionResult:
        """Transcribe audio file using Ollama Whisper."""
        try:
            import ollama
            import base64
            
            # Read and encode the audio file
            with open(audio_file_path, "rb") as f:
                audio_data = base64.b64encode(f.read()).decode("utf-8")
            
            # Prepare the request
            prompt = "Transcribe this audio to English text:"
            
            # Use Ollama client to generate response
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                options={
                    "audio_data": audio_data
                }
            )
            
            transcribed_text = response.get("response", "").strip()
            
            return TranscriptionResult(
                text=transcribed_text,
                confidence=None,
                duration=None,
            )
        except Exception as e:
            print(f"Ollama transcription error: {e}")
            raise 