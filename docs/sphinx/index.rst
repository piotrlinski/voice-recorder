Voice Recorder Documentation
=============================

Welcome to the Voice Recorder documentation. This is a professional voice recording
command-line application for macOS that provides real-time speech-to-text transcription
with AI-powered text enhancement capabilities.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   overview
   installation
   quickstart
   configuration
   api/index

Features
--------

* **Dual Transcription Modes**: OpenAI Whisper (cloud) or local Whisper models
* **Enhanced Transcription**: AI-powered grammar and punctuation improvement
* **Hotkey Support**: Hands-free recording with customizable hotkeys
* **Auto-paste**: Automatic text insertion at cursor position
* **Interactive Setup**: Configuration wizard for easy setup
* **Privacy Options**: Complete offline operation with local models

Quick Start
-----------

1. **Install the package**::

    pip install -e .

2. **Initialize configuration**::

    voice-recorder init

3. **Start recording**::

    voice-recorder

4. **Use hotkeys**:
   
   * **Right Shift**: Basic transcription (speech → text)
   * **Left Ctrl**: Enhanced transcription (speech → text → AI improvement)

Architecture Overview
=====================

The application follows Clean Architecture principles with clear separation of concerns:

.. code-block:: text

    src/voice_recorder/
    ├── domain/           # Core business logic and models
    ├── services/         # Application business logic
    ├── infrastructure/   # External dependencies (adapters)
    │   └── transcription/  # Transcription services module
    ├── cli/             # Command-line interface
    └── api/             # Application entry points

Key design patterns include:

* **Dependency Injection**: All components are injected via interfaces
* **Protocol/Interface Segregation**: Clear contracts between layers
* **Factory Pattern**: Application factory for dependency setup
* **Observer Pattern**: Hotkey event handling

Transcription Modes
===================

Basic Transcription
-------------------

* **Process**: Audio → Whisper → Raw text
* **Speed**: Fast
* **Quality**: Good transcription accuracy
* **Example**: "um so i think we should uh maybe consider the new approach" → "Um, so I think we should, uh, maybe consider the new approach."

Enhanced Transcription
----------------------

* **Process**: Audio → Whisper → AI improvement → Polished text
* **Speed**: Slower (requires additional AI processing)
* **Quality**: Professional, polished text
* **Example**: "um so i think we should uh maybe consider the new approach" → "I think we should consider the new approach."

Enhanced transcription benefits:

* Removes filler words (um, uh, like)
* Fixes grammar and punctuation
* Improves sentence structure
* Makes text more professional and readable
* Maintains original meaning

Support
-------

For issues and questions:

* Check the troubleshooting guide in the main README
* Review the API documentation
* Open an issue on GitHub

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`