"""
Ollama text processing provider.

Simple implementation that improves text using local Ollama models.
"""

from voice_recorder.domain.interfaces import ConsoleInterface
from voice_recorder.domain.models import LocalTranscriptionConfig


class OllamaTextProcessor:
    """Ollama text processing provider.
    
    Simple class that improves text quality using local Ollama models.
    """
    
    def __init__(
        self, 
        config: LocalTranscriptionConfig,
        console: ConsoleInterface | None = None
    ):
        """Initialize Ollama text processor.
        
        Args:
            config: Local transcription configuration with Ollama settings
            console: Optional console for logging
        """
        self.config = config
        self.console = console
        self.client = None
        
        # Try to initialize Ollama client
        try:
            import httpx
            self.client = httpx.Client(base_url=config.ollama_base_url, timeout=30.0)
            
            # Test connection
            response = self.client.get("/api/tags")
            if response.status_code == 200:
                if console:
                    console.info(f"Ollama text processor initialized with model: {config.ollama_model}")
            else:
                if console:
                    console.warning(f"Ollama server not responding: {response.status_code}")
                self.client = None
                
        except ImportError:
            if console:
                console.warning("httpx library not available - Install with: pip install httpx")
            self.client = None
        except Exception as e:
            if console:
                console.warning(f"Failed to connect to Ollama: {e}")
            self.client = None
    
    def process_text(self, text: str) -> str:
        """Improve text using Ollama.
        
        Args:
            text: Original text to improve
            
        Returns:
            Improved text, or original text if processing fails
        """
        if not text.strip() or not self.is_available():
            return text
        
        try:
            prompt = f"{self.config.enhanced_transcription_prompt}\n\nText to improve: {text}"
            
            response = self.client.post("/api/generate", json={
                "model": self.config.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.config.ollama_creativity
                }
            })
            
            if response.status_code == 200:
                result = response.json()
                improved_text = result.get("response", "").strip()
                
                if improved_text:
                    return improved_text
                else:
                    if self.console:
                        self.console.warning("Ollama returned empty response")
                    return text
            else:
                if self.console:
                    self.console.warning(f"Ollama request failed: {response.status_code}")
                return text
                
        except Exception as e:
            if self.console:
                self.console.warning(f"Ollama text processing failed: {e}")
            return text
    
    def is_available(self) -> bool:
        """Check if the text processor is available.
        
        Returns:
            True if Ollama client is connected and working
        """
        return self.client is not None