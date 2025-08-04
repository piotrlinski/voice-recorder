Services
========

The services layer contains the main application business logic and orchestration components.

voice_recorder.services.voice_recorder_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: voice_recorder.services.voice_recorder_service
   :members:
   :undoc-members:
   :show-inheritance:

Main Service Class
------------------

.. autoclass:: voice_recorder.services.voice_recorder_service.VoiceRecorderService
   :members:
   :undoc-members:
   :show-inheritance:
   
   The main service class that orchestrates all voice recording functionality.
   This is the primary entry point for the application's business logic.
   
   **Key Responsibilities:**
   
   * Coordinate audio recording, transcription, and text processing
   * Handle hotkey events for basic and enhanced recording modes
   * Manage recording sessions and their lifecycle
   * Provide thread-safe access to recording functionality
   * Ensure graceful startup and shutdown
   
   **Usage Example:**
   
   .. code-block:: python
   
       from voice_recorder.services.voice_recorder_service import VoiceRecorderService
       from voice_recorder.domain.models import ApplicationConfig
       
       # Initialize with dependency injection
       service = VoiceRecorderService(
           audio_recorder=audio_recorder,
           transcription_service=transcription_service,
           hotkey_listener=hotkey_listener,
           text_paster=text_paster,
           session_manager=session_manager,
           config=config,
           console=console,
           enhanced_transcription_service=enhanced_service  # Optional
       )
       
       # Start the service
       service.start()
       
       # Service will now listen for hotkey events
       # Press configured keys to start/stop recording
       
       # Stop the service
       service.stop()
   
   **Recording Flow:**
   
   1. **Key Press**: User presses basic or enhanced transcription key
   2. **Recording Start**: Audio recording begins, session created
   3. **Key Release**: User releases key, recording stops
   4. **Transcription**: Audio is transcribed (basic or enhanced mode)
   5. **Auto-paste**: Text is automatically pasted if enabled
   6. **Session Complete**: Session marked as completed

Service Methods
---------------

Core Methods
~~~~~~~~~~~~

.. automethod:: voice_recorder.services.voice_recorder_service.VoiceRecorderService.__init__
.. automethod:: voice_recorder.services.voice_recorder_service.VoiceRecorderService.start
.. automethod:: voice_recorder.services.voice_recorder_service.VoiceRecorderService.stop

Session Management
~~~~~~~~~~~~~~~~~~

.. automethod:: voice_recorder.services.voice_recorder_service.VoiceRecorderService.get_current_session
.. automethod:: voice_recorder.services.voice_recorder_service.VoiceRecorderService.get_session_history

Utility Methods
~~~~~~~~~~~~~~~

.. automethod:: voice_recorder.services.voice_recorder_service.VoiceRecorderService._is_meaningful_transcription

Architecture Notes
------------------

**Dependency Injection**
    The service requires all dependencies to be injected, following the dependency 
    inversion principle. This makes it highly testable and maintainable.

**Thread Safety**
    The service uses threading locks to ensure safe concurrent access to recording
    sessions and transcription processing.

**Error Handling**
    Comprehensive error handling ensures the service can recover from individual
    component failures without crashing.

**State Management**
    Recording state is carefully managed to prevent race conditions and ensure
    consistent behavior across different operating modes.

**Configuration**
    The service is driven by configuration, allowing different transcription modes,
    hotkey mappings, and behavior customization without code changes.