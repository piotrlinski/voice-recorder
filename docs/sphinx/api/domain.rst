Domain
======

The domain layer contains core business logic, models, and interfaces that define
the fundamental concepts and contracts of the voice recording system.

Models
------

voice_recorder.domain.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: voice_recorder.domain.models
   :members:
   :undoc-members:
   :show-inheritance:

Configuration Models
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: voice_recorder.domain.models.ApplicationConfig
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: voice_recorder.domain.models.TranscriptionConfig
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: voice_recorder.domain.models.OpenAITranscriptionConfig
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: voice_recorder.domain.models.LocalTranscriptionConfig
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: voice_recorder.domain.models.ControlsConfig
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: voice_recorder.domain.models.AudioConfig
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: voice_recorder.domain.models.GeneralConfig
   :members:
   :undoc-members:
   :show-inheritance:

Session Models
~~~~~~~~~~~~~~

.. autoclass:: voice_recorder.domain.models.RecordingSession
   :members:
   :undoc-members:
   :show-inheritance:

Result Models
~~~~~~~~~~~~~

.. autoclass:: voice_recorder.domain.models.TranscriptionResult
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: voice_recorder.domain.models.EnhancedTranscriptionResult
   :members:
   :undoc-members:
   :show-inheritance:

Enumerations
~~~~~~~~~~~~

.. autoclass:: voice_recorder.domain.models.RecordingState
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: voice_recorder.domain.models.TranscriptionMode
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: voice_recorder.domain.models.AudioFormat
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: voice_recorder.domain.models.LocalWhisperModel
   :members:
   :undoc-members:
   :show-inheritance:

Interfaces
----------

voice_recorder.domain.interfaces
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: voice_recorder.domain.interfaces
   :members:
   :undoc-members:
   :show-inheritance:

Core Interfaces
~~~~~~~~~~~~~~~

.. autoclass:: voice_recorder.domain.interfaces.AudioRecorderInterface
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: voice_recorder.domain.interfaces.TranscriptionServiceInterface
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: voice_recorder.domain.interfaces.EnhancedTranscriptionServiceInterface
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: voice_recorder.domain.interfaces.HotkeyListenerInterface
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: voice_recorder.domain.interfaces.TextPasterInterface
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: voice_recorder.domain.interfaces.SessionManagerInterface
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: voice_recorder.domain.interfaces.ConsoleInterface
   :members:
   :undoc-members:
   :show-inheritance:

Domain Concepts
---------------

Configuration Hierarchy
~~~~~~~~~~~~~~~~~~~~~~~~

The configuration system is organized hierarchically:

.. code-block:: text

    ApplicationConfig
    ├── TranscriptionConfig
    │   ├── OpenAITranscriptionConfig
    │   └── LocalTranscriptionConfig
    ├── ControlsConfig
    ├── AudioConfig
    └── GeneralConfig

**ApplicationConfig** is the root configuration containing all application settings.

**TranscriptionConfig** manages transcription providers and can operate in two modes:
- OpenAI mode using cloud-based Whisper and GPT
- Local mode using local Whisper and Ollama

Recording Session Lifecycle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Recording sessions progress through defined states:

1. **IDLE**: Session created but recording not started
2. **RECORDING**: Audio is being captured
3. **PROCESSING**: Recording complete, transcription in progress
4. **COMPLETED**: Transcription finished successfully
5. **ERROR**: An error occurred during recording or processing

.. code-block:: python

    from voice_recorder.domain.models import RecordingState
    
    # Session lifecycle
    session.state = RecordingState.IDLE
    # ... start recording ...
    session.state = RecordingState.RECORDING
    # ... stop recording ...
    session.state = RecordingState.PROCESSING
    # ... transcription complete ...
    session.state = RecordingState.COMPLETED

Transcription Results
~~~~~~~~~~~~~~~~~~~~

The system produces two types of transcription results:

**TranscriptionResult**
    Basic transcription output with raw speech-to-text conversion.

**EnhancedTranscriptionResult**
    Enhanced output that includes both original and AI-improved text.

Interface Contracts
~~~~~~~~~~~~~~~~~~~

All interfaces define clear contracts for dependency injection:

- **AudioRecorderInterface**: Audio capture and file management
- **TranscriptionServiceInterface**: Basic speech-to-text conversion
- **EnhancedTranscriptionServiceInterface**: AI-enhanced text processing
- **HotkeyListenerInterface**: System hotkey detection
- **TextPasterInterface**: Text insertion capabilities
- **SessionManagerInterface**: Recording session management
- **ConsoleInterface**: Logging and user feedback

These interfaces enable the application to work with different implementations
while maintaining consistent behavior and testability.