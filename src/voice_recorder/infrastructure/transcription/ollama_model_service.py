"""
Ollama model transcription service implementation.
"""

from ...domain.interfaces import TranscriptionService
from ...domain.models import TranscriptionResult


class OllamaModelTranscriptionService(TranscriptionService):
    """Ollama model transcription service implementation."""

    def __init__(self, model_name: str, base_url: str = "http://localhost:11434"):
        """Initialize Ollama model transcription service."""
        self.model_name = model_name
        self.base_url = base_url
        try:
            import ollama
            # Configure Ollama client
            ollama.set_host(self.base_url)
            
            # Test connection to Ollama
            try:
                models = ollama.list()
                print(f"Ollama server connected at {self.base_url}")
                print(f"Available models: {[model['name'] for model in models['models']]}")
                
                # Check if the specified model is available
                model_names = [model['name'] for model in models['models']]
                if self.model_name not in model_names:
                    print(f"Warning: Model '{self.model_name}' not found in available models: {model_names}")
            except Exception as e:
                raise RuntimeError(f"Ollama server not accessible at {self.base_url}: {e}")
        except ImportError:
            raise RuntimeError("ollama library not available. Install with: pip install ollama")
        except Exception as e:
            raise RuntimeError(f"Ollama connection failed: {e}")

    def transcribe(self, audio_file_path: str) -> TranscriptionResult:
        """Transcribe audio file using Ollama model."""
        try:
            import ollama
            import base64
            
            # Read and encode the audio file
            with open(audio_file_path, "rb") as f:
                audio_data = base64.b64encode(f.read()).decode("utf-8")
            
            # Prepare the request
            prompt = "Please transcribe this audio file to English text. Only return the transcribed text, nothing else:"
            
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
            print(f"Ollama model transcription error: {e}")
            raise 