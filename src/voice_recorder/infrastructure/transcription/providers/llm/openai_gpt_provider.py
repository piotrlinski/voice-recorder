"""
OpenAI GPT text enhancement provider implementation.
"""

from voice_recorder.domain.interfaces import ConsoleInterface
from voice_recorder.domain.models import OpenAITranscriptionConfig
from voice_recorder.infrastructure.transcription.base.base_enhancement_service import BaseEnhancementService


class OpenAIGPTProvider(BaseEnhancementService):
    """OpenAI GPT text enhancement provider."""

    def __init__(
        self,
        config: OpenAITranscriptionConfig,
        console: ConsoleInterface | None = None,
    ):
        """Initialize OpenAI GPT enhancement provider."""
        super().__init__(config, console)

    def _validate_config(self) -> None:
        """Validate OpenAI GPT configuration."""
        if not self.config.api_key:
            raise ValueError("OpenAI API key required")

    def _initialize(self) -> None:
        """Initialize OpenAI GPT client."""
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.config.api_key)
            
            if self.console:
                self.console.info("OpenAI GPT client initialized for text improvement")
        except ImportError:
            if self.console:
                self.console.error(
                    "OpenAI library not available - Install with: pip install openai"
                )
            raise RuntimeError("OpenAI library not available")
        except Exception as e:
            if self.console:
                self.console.error(f"OpenAI GPT initialization failed: {e}")
            raise RuntimeError(f"OpenAI GPT initialization failed: {e}")

    def enhance_text(self, original_text: str) -> str:
        """Enhance text using OpenAI GPT."""
        if not original_text.strip():
            return original_text

        try:
            # Use configurable prompt for text improvement
            system_prompt = self.config.enhanced_transcription_prompt

            response = self.client.chat.completions.create(
                model=self.config.gpt_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": original_text}
                ],
                temperature=self.config.gpt_creativity,
                max_tokens=500,
            )

            enhanced_text = response.choices[0].message.content.strip()
            
            # Fallback to original text if enhancement is empty
            if not enhanced_text:
                if self.console:
                    self.console.warning("OpenAI GPT returned empty response, using original text")
                return original_text

            return enhanced_text

        except Exception as e:
            self._log_enhancement_error("OpenAI GPT", e)
            return original_text  # Fallback to original text

    def is_available(self) -> bool:
        """Check if OpenAI GPT service is available."""
        return hasattr(self, 'client') and self.client is not None 