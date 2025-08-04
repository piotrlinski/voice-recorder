"""
OpenAI GPT text processing provider.

Simple implementation that improves text using OpenAI's GPT models.
"""

from voice_recorder.domain.interfaces import ConsoleInterface
from voice_recorder.domain.models import OpenAITranscriptionConfig


class OpenAITextProcessor:
    """OpenAI GPT text processing provider.
    
    Simple class that improves text quality using OpenAI's GPT models.
    """
    
    def __init__(
        self, 
        config: OpenAITranscriptionConfig,
        console: ConsoleInterface | None = None
    ):
        """Initialize OpenAI text processor.
        
        Args:
            config: OpenAI configuration
            console: Optional console for logging
            
        Raises:
            ValueError: If API key is missing
            RuntimeError: If OpenAI library is not available
        """
        self.config = config
        self.console = console
        
        # Validate configuration
        if not config.api_key:
            raise ValueError("OpenAI API key is required")
        
        # Initialize OpenAI client
        try:
            import openai
            self.client = openai.OpenAI(api_key=config.api_key)
            
            if console:
                console.info("OpenAI GPT text processor initialized")
                
        except ImportError:
            error_msg = "OpenAI library not available - Install with: pip install openai"
            if console:
                console.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Failed to initialize OpenAI client: {e}"
            if console:
                console.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    def process_text(self, text: str) -> str:
        """Improve text using OpenAI GPT.
        
        Args:
            text: Original text to improve
            
        Returns:
            Improved text, or original text if processing fails
        """
        if not text.strip():
            return text
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.gpt_model,
                messages=[
                    {"role": "system", "content": self.config.enhanced_transcription_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=self.config.gpt_creativity,
                max_tokens=500,
            )
            
            improved_text = response.choices[0].message.content.strip()
            
            # Return original text if GPT returns empty response
            if not improved_text:
                if self.console:
                    self.console.warning("OpenAI GPT returned empty response")
                return text
            
            return improved_text
            
        except Exception as e:
            if self.console:
                self.console.warning(f"Text processing failed: {e}")
            return text  # Return original text on failure
    
    def is_available(self) -> bool:
        """Check if the text processor is available.
        
        Returns:
            True if the OpenAI client is initialized and ready
        """
        return hasattr(self, 'client') and self.client is not None