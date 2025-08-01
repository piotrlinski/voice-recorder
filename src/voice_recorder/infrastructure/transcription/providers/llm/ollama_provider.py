"""
Ollama LLM text enhancement provider implementation.
"""

import httpx
from typing import Optional

from voice_recorder.domain.interfaces import ConsoleInterface
from voice_recorder.domain.models import LocalTranscriptionConfig
from voice_recorder.infrastructure.transcription.base.base_enhancement_service import BaseEnhancementService


class OllamaProvider(BaseEnhancementService):
    """Ollama local LLM text enhancement provider."""

    def __init__(
        self,
        config: LocalTranscriptionConfig,
        console: ConsoleInterface | None = None,
    ):
        """Initialize Ollama enhancement provider."""
        super().__init__(config, console)

    def _validate_config(self) -> None:
        """Validate Ollama configuration."""
        if not self.config.ollama_model:
            raise ValueError("Ollama model name required")

    def _initialize(self) -> None:
        """Initialize Ollama connection."""
        self.base_url = self.config.ollama_base_url.rstrip("/")
        self.model_name = self.config.ollama_model
        self.temperature = self.config.ollama_creativity
        
        # Test connection to Ollama
        self._test_connection()

    def _test_connection(self) -> None:
        """Test connection to Ollama API."""
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(f"{self.base_url}/api/version")
                if response.status_code == 200:
                    if self.console:
                        self.console.info(f"Ollama connection successful at {self.base_url}")
                else:
                    raise RuntimeError(f"Ollama API returned status {response.status_code}")
        except httpx.ConnectError:
            error_msg = f"Cannot connect to Ollama at {self.base_url}. Make sure Ollama is running."
            if self.console:
                self.console.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Ollama connection test failed: {e}"
            if self.console:
                self.console.error(error_msg)
            raise RuntimeError(error_msg)

    def enhance_text(self, original_text: str) -> str:
        """Enhance text using Ollama LLM."""
        if not original_text.strip():
            return original_text

        try:
            # Use configurable prompt for text improvement
            prompt = f"{self.config.enhanced_transcription_prompt}\n\n{original_text}"

            # Prepare request payload
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "top_p": 0.9,
                    "max_tokens": 500,
                },
            }

            # Make request to Ollama
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )

                if response.status_code != 200:
                    error_msg = f"Ollama API error: {response.status_code} - {response.text}"
                    if self.console:
                        self.console.error(error_msg)
                    return original_text  # Fallback to original text

                # Parse response
                result = response.json()
                enhanced_text = result.get("response", "").strip()

                if not enhanced_text:
                    if self.console:
                        self.console.warning("Ollama returned empty response, using original text")
                    return original_text

                return enhanced_text

        except httpx.TimeoutException:
            if self.console:
                self.console.error("Ollama request timed out, using original text")
            return original_text
        except Exception as e:
            self._log_enhancement_error("Ollama", e)
            return original_text  # Fallback to original text

    def is_available(self) -> bool:
        """Check if Ollama service is available."""
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.base_url}/api/version")
                return response.status_code == 200
        except Exception:
            return False

    def list_models(self) -> list[str]:
        """List available models in Ollama."""
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    models = [model["name"] for model in data.get("models", [])]
                    return models
                else:
                    return []
        except Exception:
            return [] 