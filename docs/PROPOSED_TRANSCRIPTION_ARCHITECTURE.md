# Proposed New Transcription Module Architecture

## Overview
The new architecture separates concerns into distinct layers and provides better extensibility for different transcription and enhancement providers.

## New Directory Structure
```
src/voice_recorder/infrastructure/transcription/
├── __init__.py
├── base/
│   ├── __init__.py
│   ├── base_transcription_service.py
│   ├── base_enhancement_service.py
│   └── base_enhanced_service.py
├── providers/
│   ├── __init__.py
│   ├── whisper/
│   │   ├── __init__.py
│   │   ├── openai_whisper_provider.py
│   │   └── local_whisper_provider.py
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── openai_gpt_provider.py
│   │   └── ollama_provider.py
│   └── composite/
│       ├── __init__.py
│       ├── openai_enhanced_service.py
│       └── local_enhanced_service.py
├── factory.py
└── registry.py
```

## Core Components

### 1. Base Classes (base/)

#### BaseTranscriptionService
```python
class BaseTranscriptionService(TranscriptionServiceInterface):
    """Base class for all transcription services."""
    
    def __init__(self, config: Any, console: ConsoleInterface | None = None):
        self.config = config
        self.console = console
        self._validate_config()
        self._initialize()
    
    @abstractmethod
    def _validate_config(self) -> None:
        """Validate service-specific configuration."""
        pass
    
    @abstractmethod
    def _initialize(self) -> None:
        """Initialize service-specific resources."""
        pass
    
    @abstractmethod
    def _transcribe_audio(self, audio_file_path: str) -> str:
        """Perform the actual transcription."""
        pass
```

#### BaseEnhancementService
```python
class BaseEnhancementService(ABC):
    """Base class for all text enhancement services."""
    
    def __init__(self, config: Any, console: ConsoleInterface | None = None):
        self.config = config
        self.console = console
        self._validate_config()
        self._initialize()
    
    @abstractmethod
    def _validate_config(self) -> None:
        """Validate service-specific configuration."""
        pass
    
    @abstractmethod
    def _initialize(self) -> None:
        """Initialize service-specific resources."""
        pass
    
    @abstractmethod
    def enhance_text(self, original_text: str) -> str:
        """Enhance the given text."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the service is available."""
        pass
```

#### BaseEnhancedService
```python
class BaseEnhancedService(EnhancedTranscriptionServiceInterface):
    """Base class for enhanced transcription services."""
    
    def __init__(
        self,
        transcription_service: BaseTranscriptionService,
        enhancement_service: BaseEnhancementService,
        console: ConsoleInterface | None = None
    ):
        self.transcription_service = transcription_service
        self.enhancement_service = enhancement_service
        self.console = console
    
    def transcribe_and_enhance(self, audio_file_path: str) -> EnhancedTranscriptionResult:
        """Transcribe and enhance audio file."""
        # First transcribe
        transcription_result = self.transcription_service.transcribe(audio_file_path)
        
        # Then enhance
        enhanced_text = self.enhancement_service.enhance_text(transcription_result.text)
        
        return EnhancedTranscriptionResult(
            original_text=transcription_result.text,
            enhanced_text=enhanced_text,
            confidence=transcription_result.confidence,
            duration=transcription_result.duration
        )
```

### 2. Provider Implementations (providers/)

#### Whisper Providers (providers/whisper/)

**OpenAI Whisper Provider:**
```python
class OpenAIWhisperProvider(BaseTranscriptionService):
    """OpenAI Whisper API transcription provider."""
    
    def _validate_config(self) -> None:
        if not self.config.api_key:
            raise ValueError("OpenAI API key required")
    
    def _initialize(self) -> None:
        import openai
        self.client = openai.OpenAI(api_key=self.config.api_key)
    
    def _transcribe_audio(self, audio_file_path: str) -> str:
        with open(audio_file_path, "rb") as audio_file:
            response = self.client.audio.transcriptions.create(
                model=self.config.whisper_model,
                file=audio_file,
                response_format="json"
            )
        return response.text
```

**Local Whisper Provider:**
```python
class LocalWhisperProvider(BaseTranscriptionService):
    """Local Whisper transcription provider."""
    
    def _validate_config(self) -> None:
        if not self.config.whisper_model:
            raise ValueError("Whisper model size required")
    
    def _initialize(self) -> None:
        import whisper
        self.model = whisper.load_model(self.config.whisper_model.value)
    
    def _transcribe_audio(self, audio_file_path: str) -> str:
        result = self.model.transcribe(audio_file_path, language="en", fp16=False)
        return result["text"]
```

#### LLM Providers (providers/llm/)

**OpenAI GPT Provider:**
```python
class OpenAIGPTProvider(BaseEnhancementService):
    """OpenAI GPT text enhancement provider."""
    
    def _validate_config(self) -> None:
        if not self.config.api_key:
            raise ValueError("OpenAI API key required")
    
    def _initialize(self) -> None:
        import openai
        self.client = openai.OpenAI(api_key=self.config.api_key)
    
    def enhance_text(self, original_text: str) -> str:
        response = self.client.chat.completions.create(
            model=self.config.gpt_model,
            messages=[
                {"role": "system", "content": "Improve the following text..."},
                {"role": "user", "content": original_text}
            ],
            temperature=self.config.gpt_creativity
        )
        return response.choices[0].message.content
    
    def is_available(self) -> bool:
        return self.client is not None
```

**Ollama Provider:**
```python
class OllamaProvider(BaseEnhancementService):
    """Ollama local LLM text enhancement provider."""
    
    def _validate_config(self) -> None:
        if not self.config.ollama_model:
            raise ValueError("Ollama model name required")
    
    def _initialize(self) -> None:
        self.base_url = self.config.ollama_base_url.rstrip("/")
        self._test_connection()
    
    def enhance_text(self, original_text: str) -> str:
        # Implementation using httpx to call Ollama API
        pass
    
    def is_available(self) -> bool:
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.base_url}/api/version")
                return response.status_code == 200
        except Exception:
            return False
```

### 3. Composite Services (providers/composite/)

**OpenAI Enhanced Service:**
```python
class OpenAIEnhancedService(BaseEnhancedService):
    """OpenAI Whisper + GPT enhanced transcription service."""
    
    def __init__(self, config: TranscriptionConfig, console: ConsoleInterface | None = None):
        transcription_service = OpenAIWhisperProvider(config.openai, console)
        enhancement_service = OpenAIGPTProvider(config.openai, console)
        super().__init__(transcription_service, enhancement_service, console)
```

**Local Enhanced Service:**
```python
class LocalEnhancedService(BaseEnhancedService):
    """Local Whisper + Ollama enhanced transcription service."""
    
    def __init__(self, config: TranscriptionConfig, console: ConsoleInterface | None = None):
        transcription_service = LocalWhisperProvider(config.local, console)
        enhancement_service = OllamaProvider(config.local, console)
        super().__init__(transcription_service, enhancement_service, console)
```

### 4. Service Registry (registry.py)
```python
class TranscriptionServiceRegistry:
    """Registry for transcription service providers."""
    
    _transcription_providers: Dict[str, Type[BaseTranscriptionService]] = {}
    _enhancement_providers: Dict[str, Type[BaseEnhancementService]] = {}
    _enhanced_services: Dict[str, Type[BaseEnhancedService]] = {}
    
    @classmethod
    def register_transcription_provider(cls, name: str, provider_class: Type[BaseTranscriptionService]) -> None:
        cls._transcription_providers[name] = provider_class
    
    @classmethod
    def register_enhancement_provider(cls, name: str, provider_class: Type[BaseEnhancementService]) -> None:
        cls._enhancement_providers[name] = provider_class
    
    @classmethod
    def register_enhanced_service(cls, name: str, service_class: Type[BaseEnhancedService]) -> None:
        cls._enhanced_services[name] = service_class
    
    @classmethod
    def get_transcription_provider(cls, name: str) -> Type[BaseTranscriptionService]:
        return cls._transcription_providers.get(name)
    
    @classmethod
    def get_enhancement_provider(cls, name: str) -> Type[BaseEnhancementService]:
        return cls._enhancement_providers.get(name)
    
    @classmethod
    def get_enhanced_service(cls, name: str) -> Type[BaseEnhancedService]:
        return cls._enhanced_services.get(name)
```

### 5. Updated Factory (factory.py)
```python
class TranscriptionServiceFactory:
    """Factory for creating transcription services."""
    
    @staticmethod
    def create_basic_service(
        config: TranscriptionConfig,
        console: ConsoleInterface | None = None
    ) -> TranscriptionServiceInterface:
        """Create a basic transcription service."""
        if config.mode == TranscriptionMode.OPENAI:
            return OpenAIWhisperProvider(config.openai, console)
        elif config.mode == TranscriptionMode.LOCAL:
            return LocalWhisperProvider(config.local, console)
        else:
            raise ValueError(f"Unsupported transcription mode: {config.mode}")
    
    @staticmethod
    def create_enhanced_service(
        config: TranscriptionConfig,
        console: ConsoleInterface | None = None
    ) -> EnhancedTranscriptionServiceInterface:
        """Create an enhanced transcription service."""
        if config.mode == TranscriptionMode.OPENAI:
            return OpenAIEnhancedService(config, console)
        elif config.mode == TranscriptionMode.LOCAL:
            return LocalEnhancedService(config, console)
        else:
            raise ValueError(f"Unsupported transcription mode: {config.mode}")
```

## Benefits of New Architecture

### 1. **Separation of Concerns**
- Basic transcription and enhancement are completely separate
- Each provider has a single responsibility
- Easy to test individual components

### 2. **Extensibility**
- Adding new providers requires only implementing the base classes
- No need to modify existing code
- Registry pattern allows dynamic provider discovery

### 3. **Flexibility**
- Can mix and match different transcription and enhancement providers
- Easy to create new composite services
- Configuration-driven provider selection

### 4. **Maintainability**
- Clear inheritance hierarchy
- Consistent interfaces across all providers
- Easy to understand and modify

### 5. **Testability**
- Each component can be tested in isolation
- Easy to mock dependencies
- Clear boundaries between components

## Migration Strategy

1. **Phase 1**: Create new base classes and provider implementations
2. **Phase 2**: Update factory to use new structure
3. **Phase 3**: Update service layer to use new factory
4. **Phase 4**: Remove old implementations
5. **Phase 5**: Add new providers (e.g., Azure Speech, Google Speech-to-Text)

## Example Usage

```python
# Basic transcription
basic_service = TranscriptionServiceFactory.create_basic_service(config, console)
result = basic_service.transcribe("audio.wav")

# Enhanced transcription
enhanced_service = TranscriptionServiceFactory.create_enhanced_service(config, console)
result = enhanced_service.transcribe_and_enhance("audio.wav")

# Custom composite service
transcription_provider = OpenAIWhisperProvider(config.openai, console)
enhancement_provider = OllamaProvider(config.local, console)
custom_service = BaseEnhancedService(transcription_provider, enhancement_provider, console)
```

This new architecture provides a solid foundation for future expansion while maintaining clean separation of concerns and following SOLID principles. 