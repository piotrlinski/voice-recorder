Configuration
=============

The Voice Recorder uses a configuration file located at ``~/.voicerecorder/config.ini``
to manage all application settings. This guide covers all available configuration options.

Configuration File Location
---------------------------

The configuration file is automatically created in::

    ~/.voicerecorder/config.ini

You can view the current configuration with::

    voice-recorder config show

Or find the exact path with::

    voice-recorder config path

Complete Configuration Reference
-------------------------------

Here's a complete configuration file with all available options:

.. code-block:: ini

    [transcription]
    mode = openai

    [transcription.openai]
    api_key = sk-your-openai-key-here
    whisper_model = whisper-1
    gpt_model = gpt-3.5-turbo
    gpt_creativity = 0.3
    enhanced_transcription_prompt = Please improve the following transcribed text by fixing grammar, punctuation, and making it more coherent while preserving the original meaning. Only return the improved text without any explanations or additional commentary.

    [transcription.local]
    whisper_model = small
    ollama_base_url = http://localhost:11434
    ollama_model = llama3.1
    ollama_creativity = 0.3
    enhanced_transcription_prompt = Please improve the following transcribed text by fixing grammar, punctuation, and making it more coherent while preserving the original meaning. Only return the improved text without any explanations or additional commentary.

    [controls]
    basic_key = shift_r
    enhanced_key = ctrl_l

    [audio]
    sample_rate = 16000
    channels = 1
    format = wav
    chunk_size = 1024

    [general]
    auto_paste = true

Transcription Settings
----------------------

Mode Selection
~~~~~~~~~~~~~~

.. code-block:: ini

    [transcription]
    mode = openai  # or "local"

**Options:**

* ``openai``: Use OpenAI's cloud-based Whisper API and GPT for enhancement
* ``local``: Use local Whisper model and Ollama for offline processing

OpenAI Configuration
~~~~~~~~~~~~~~~~~~~~

.. code-block:: ini

    [transcription.openai]
    api_key = sk-your-openai-key-here
    whisper_model = whisper-1
    gpt_model = gpt-3.5-turbo
    gpt_creativity = 0.3
    enhanced_transcription_prompt = Your custom prompt here...

**Settings:**

* ``api_key``: Your OpenAI API key (required for OpenAI mode)
* ``whisper_model``: OpenAI Whisper model (currently only ``whisper-1``)
* ``gpt_model``: GPT model for enhancement (``gpt-3.5-turbo``, ``gpt-4``, etc.)
* ``gpt_creativity``: Creativity level 0.0-2.0 (0.0 = conservative, 2.0 = creative)
* ``enhanced_transcription_prompt``: Custom prompt for AI enhancement

Local Configuration
~~~~~~~~~~~~~~~~~~~

.. code-block:: ini

    [transcription.local]
    whisper_model = small
    ollama_base_url = http://localhost:11434
    ollama_model = llama3.1
    ollama_creativity = 0.3
    enhanced_transcription_prompt = Your custom prompt here...

**Settings:**

* ``whisper_model``: Local Whisper model size
  
  * ``tiny``: Fastest, lowest accuracy (~39 MB)
  * ``small``: Good balance (~244 MB)
  * ``medium``: Better accuracy (~769 MB)
  * ``large``: Best accuracy (~1550 MB)

* ``ollama_base_url``: Ollama server URL (default: ``http://localhost:11434``)
* ``ollama_model``: Ollama model name (``llama3.1``, ``mistral``, ``codellama``, etc.)
* ``ollama_creativity``: Temperature for text generation 0.0-2.0
* ``enhanced_transcription_prompt``: Custom prompt for AI enhancement

Control Settings
----------------

Hotkey Configuration
~~~~~~~~~~~~~~~~~~~~

.. code-block:: ini

    [controls]
    basic_key = shift_r
    enhanced_key = ctrl_l

**Available Keys:**

* ``shift_r``, ``shift_l``: Right/left Shift keys
* ``ctrl_r``, ``ctrl_l``: Right/left Control keys  
* ``alt_r``, ``alt_l``: Right/left Alt/Option keys
* ``cmd_r``, ``cmd_l``: Right/left Command keys
* ``f1`` through ``f12``: Function keys

**Usage:**

* ``basic_key``: Trigger for basic transcription (speech → text)
* ``enhanced_key``: Trigger for enhanced transcription (speech → AI-improved text)

Audio Settings
--------------

Recording Configuration
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: ini

    [audio]
    sample_rate = 16000
    channels = 1
    format = wav
    chunk_size = 1024

**Settings:**

* ``sample_rate``: Recording sample rate in Hz
  
  * ``16000``: Recommended for Whisper (best compatibility)
  * ``44100``: CD quality (higher processing overhead)
  * ``48000``: Professional audio (highest quality)

* ``channels``: Number of audio channels
  
  * ``1``: Mono (recommended for speech)
  * ``2``: Stereo (larger file sizes)

* ``format``: Audio file format
  
  * ``wav``: Uncompressed, best quality (recommended)
  * ``mp3``: Compressed, smaller files
  * ``flac``: Lossless compression

* ``chunk_size``: Audio buffer size in samples (1024 is optimal for most systems)

General Settings
----------------

Application Behavior
~~~~~~~~~~~~~~~~~~~~

.. code-block:: ini

    [general]
    auto_paste = true

**Settings:**

* ``auto_paste``: Automatically paste transcribed text at cursor position
  
  * ``true``: Paste immediately after transcription
  * ``false``: Don't paste (transcription still occurs)

Custom Prompts
--------------

Enhancement Prompts
~~~~~~~~~~~~~~~~~~~

You can customize how AI enhances your transcriptions by modifying the prompt:

**Default Prompt:**

.. code-block:: text

    Please improve the following transcribed text by fixing grammar, punctuation, 
    and making it more coherent while preserving the original meaning. Only return 
    the improved text without any explanations or additional commentary.

**Custom Prompt Examples:**

**Business Writing:**

.. code-block:: text

    Convert the following transcribed speech into professional business language 
    with proper grammar, punctuation, and formal tone. Maintain the original 
    meaning while making it suitable for corporate communication.

**Academic Style:**

.. code-block:: text

    Improve the following transcribed text to academic writing standards with 
    proper grammar, punctuation, and scholarly tone. Maintain accuracy while 
    enhancing clarity and formality.

**Creative Writing:**

.. code-block:: text

    Enhance the following transcribed text with more vivid language and creative 
    expression while maintaining the original meaning and improving flow and 
    readability.

**Technical Documentation:**

.. code-block:: text

    Improve the following transcribed text for technical documentation with 
    clear, precise language and proper technical terminology while maintaining 
    accuracy and clarity.

Configuration Examples
----------------------

Content Creator Setup
~~~~~~~~~~~~~~~~~~~~~

For bloggers, writers, and content creators:

.. code-block:: ini

    [transcription]
    mode = openai

    [transcription.openai]
    api_key = your-key-here
    gpt_model = gpt-4
    gpt_creativity = 0.5
    enhanced_transcription_prompt = Transform this transcribed speech into engaging, well-structured content suitable for blog posts or articles. Fix grammar, improve flow, and make it more readable while preserving the original ideas and tone.

    [controls]
    basic_key = f1
    enhanced_key = f2

    [general]
    auto_paste = true

Developer Setup
~~~~~~~~~~~~~~~

For code documentation and technical writing:

.. code-block:: ini

    [transcription]
    mode = local

    [transcription.local]
    whisper_model = medium
    ollama_model = codellama
    enhanced_transcription_prompt = Convert this transcribed speech into clear technical documentation with proper grammar, precise terminology, and professional structure suitable for code comments and API documentation.

    [controls]
    basic_key = shift_r
    enhanced_key = ctrl_l

Privacy-Focused Setup
~~~~~~~~~~~~~~~~~~~~~

For complete offline operation:

.. code-block:: ini

    [transcription]
    mode = local

    [transcription.local]
    whisper_model = large
    ollama_model = llama3.1
    ollama_creativity = 0.2

    [controls]
    basic_key = shift_r
    enhanced_key = ctrl_l

    [general]
    auto_paste = true

Configuration Management
------------------------

Command Line Tools
~~~~~~~~~~~~~~~~~~

View current configuration::

    voice-recorder config show

Show configuration file path::

    voice-recorder config path

Reset to defaults::

    voice-recorder config reset

Programmatic Access
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from voice_recorder.infrastructure.config_manager import ConfigManager
    from voice_recorder.domain.models import ApplicationConfig
    
    # Load configuration
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    # Modify configuration
    config.general.auto_paste = False
    config.transcription.openai.gpt_creativity = 0.5
    
    # Save configuration
    config_manager.save_config(config)

Validation and Errors
----------------------

The configuration system validates all settings:

* **Invalid keys**: Unknown hotkeys are rejected
* **Invalid values**: Out-of-range values are corrected
* **Missing sections**: Default values are used
* **Malformed files**: Configuration is recreated with defaults

Common validation errors:

* API key format (must start with ``sk-``)
* Creativity values (must be 0.0-2.0)
* Sample rates (must be valid audio rates)
* File formats (must be supported formats)

Migration and Compatibility
---------------------------

Configuration files are automatically migrated between versions:

* New settings get default values
* Deprecated settings are removed
* Format changes are handled transparently
* Backup files are created during migration

The system maintains backward compatibility while evolving the configuration format.