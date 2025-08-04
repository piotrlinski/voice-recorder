API Reference
=============

This section contains the complete API documentation for the Voice Recorder library.

.. toctree::
   :maxdepth: 2

   services
   domain

The Voice Recorder API is organized into several key modules:

Services
--------

The services layer contains the main application business logic and orchestration.

:doc:`services`
    Main service classes that coordinate between different components.

Domain
------

The domain layer contains core business logic, models, and interfaces.

:doc:`domain`
    Core domain models, enumerations, and interface definitions.

Infrastructure
--------------

The infrastructure layer contains adapters for external services and systems including
audio recording, transcription services, hotkey handling, and configuration management.

CLI
---

The CLI layer contains command-line interface components including configuration wizards
and user interaction components.

Usage Patterns
--------------

Main Service Usage
~~~~~~~~~~~~~~~~~~

The primary entry point for using the Voice Recorder programmatically:

.. code-block:: python

    from voice_recorder.api.app import VoiceRecorderApp
    from voice_recorder.domain.models import ApplicationConfig
    
    # Create application with default configuration
    app = VoiceRecorderApp()
    
    # Or with custom configuration
    config = ApplicationConfig(...)
    app = VoiceRecorderApp(config=config)
    
    # Start the service
    app.start()
    
    # Stop gracefully
    app.stop()

Configuration Management
~~~~~~~~~~~~~~~~~~~~~~~~

Working with configuration programmatically:

.. code-block:: python

    from voice_recorder.infrastructure.config_manager import ConfigManager
    from voice_recorder.domain.models import (
        ApplicationConfig, 
        TranscriptionConfig, 
        TranscriptionMode
    )
    
    # Load existing configuration
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    # Create new configuration
    config = ApplicationConfig(
        transcription=TranscriptionConfig(
            mode=TranscriptionMode.OPENAI
        )
    )
    
    # Save configuration
    config_manager.save_config(config)

Transcription Services
~~~~~~~~~~~~~~~~~~~~~~

Using transcription services directly:

.. code-block:: python

    from voice_recorder.infrastructure.transcription.simple_factory import (
        SimpleTranscriptionServiceFactory
    )
    from voice_recorder.domain.models import TranscriptionConfig
    
    # Create transcription service
    factory = SimpleTranscriptionServiceFactory()
    config = TranscriptionConfig(...)
    
    # Basic transcription
    service = factory.create_service(config)
    result = service.transcribe("path/to/audio.wav")
    print(result.text)
    
    # Enhanced transcription
    enhanced_service = factory.create_enhanced_service(config)
    result = enhanced_service.transcribe_and_enhance("path/to/audio.wav")
    print(result.text)

Error Handling
--------------

The API uses standard Python exceptions with clear error messages:

.. code-block:: python

    from voice_recorder.api.app import VoiceRecorderApp
    
    try:
        app = VoiceRecorderApp()
        app.start()
    except FileNotFoundError:
        print("Configuration file not found. Run 'voice-recorder init' first.")
    except RuntimeError as e:
        print(f"Failed to start voice recorder: {e}")
    except KeyboardInterrupt:
        print("Shutting down...")
        app.stop()

Type Safety
-----------

The entire API is fully typed with mypy strict mode enabled. All public methods
include comprehensive type hints:

.. code-block:: python

    from typing import Optional
    from voice_recorder.domain.models import ApplicationConfig, RecordingSession
    from voice_recorder.services.voice_recorder_service import VoiceRecorderService
    
    def create_service(config: ApplicationConfig) -> VoiceRecorderService:
        # All parameters are properly typed
        pass
    
    def get_session() -> Optional[RecordingSession]:
        # Return types are explicit
        pass

Thread Safety
-------------

The Voice Recorder service handles concurrent operations safely:

* Audio recording runs in background threads
* Transcription processing is asynchronous
* Hotkey detection is non-blocking
* Session management is thread-safe

The main service coordinates all these operations and provides proper cleanup
when stopping.