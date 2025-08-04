Installation
============

This guide covers installing the Voice Recorder application and its dependencies.

Requirements
------------

System Requirements
~~~~~~~~~~~~~~~~~~~

* **Operating System**: macOS 10.14+ (for full functionality)
* **Python**: 3.11 or higher
* **Memory**: 2GB RAM minimum, 4GB recommended
* **Disk Space**: 500MB for application and models

For **enhanced transcription** with local models:

* **Memory**: 8GB RAM recommended (for larger Whisper models)
* **Disk Space**: 2-10GB additional (depending on model size)

Python Dependencies
~~~~~~~~~~~~~~~~~~~

Core dependencies are automatically installed:

* **pydantic**: Data validation and settings management
* **pyaudio**: Cross-platform audio recording
* **openai**: OpenAI API client (for cloud transcription)
* **pynput**: Cross-platform input monitoring
* **requests**: HTTP client for API calls

Optional dependencies for enhanced features:

* **openai-whisper**: Local Whisper models (for offline transcription)
* **torch**: PyTorch (required by local Whisper)
* **ffmpeg**: Audio processing (required by local Whisper)

Installation Methods
--------------------

Method 1: Development Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For development or to get the latest features:

.. code-block:: bash

    # Clone the repository
    git clone https://github.com/your-username/voice-recorder.git
    cd voice-recorder

    # Create virtual environment
    python -m venv .venv
    source .venv/bin/activate  # On macOS/Linux
    # or
    .venv\\Scripts\\activate  # On Windows

    # Install in development mode
    pip install -e .

    # Or install with all development dependencies
    pip install -e ".[dev,test]"

Method 2: Package Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When available on PyPI:

.. code-block:: bash

    # Create virtual environment (recommended)
    python -m venv voice-recorder-env
    source voice-recorder-env/bin/activate

    # Install from PyPI
    pip install voice-recorder

System Dependencies
-------------------

macOS Setup
~~~~~~~~~~~

Install required system dependencies using Homebrew:

.. code-block:: bash

    # Install Homebrew if you haven't already
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    # Install PortAudio (required for PyAudio)
    brew install portaudio

    # Install FFmpeg (required for local Whisper models)
    brew install ffmpeg

    # Install Ollama (optional, for local enhanced transcription)
    brew install ollama

Ubuntu/Debian Setup
~~~~~~~~~~~~~~~~~~~

For Linux users (limited functionality):

.. code-block:: bash

    # Install system dependencies
    sudo apt update
    sudo apt install portaudio19-dev python3-dev ffmpeg

    # Install Ollama (optional)
    curl -fsSL https://ollama.ai/install.sh | sh

Local Whisper Models
--------------------

For offline transcription, install local Whisper:

.. code-block:: bash

    # Install openai-whisper
    pip install openai-whisper

    # Download models (optional - will download automatically on first use)
    python -c "import whisper; whisper.load_model('small')"
    python -c "import whisper; whisper.load_model('medium')"
    python -c "import whisper; whisper.load_model('large')"

Available model sizes:

* **tiny**: Fastest, lowest accuracy (~1GB VRAM)
* **small**: Good balance (~2GB VRAM)
* **medium**: Better accuracy (~5GB VRAM)
* **large**: Best accuracy (~10GB VRAM)

Local LLM Setup (Ollama)
-------------------------

For local enhanced transcription:

.. code-block:: bash

    # Start Ollama service
    ollama serve

    # Download a model (in another terminal)
    ollama pull llama3.1
    # or
    ollama pull mistral
    ollama pull codellama

Verify Installation
-------------------

Test Basic Installation
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Check if voice-recorder is installed
    voice-recorder --help

    # Initialize configuration
    voice-recorder init

    # Test with OpenAI transcription (requires API key)
    voice-recorder config show

Test Audio Recording
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Test PyAudio installation
    import pyaudio
    
    p = pyaudio.PyAudio()
    print(f"Available audio devices: {p.get_device_count()}")
    p.terminate()

Test Local Transcription
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Test Whisper installation
    import whisper
    
    model = whisper.load_model("small")
    print("Whisper model loaded successfully")

Test Enhanced Features
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Test Ollama connection
    curl http://localhost:11434/api/tags

    # Test with voice recorder
    voice-recorder config show

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**PyAudio Installation Failed**

On macOS:

.. code-block:: bash

    # Install PortAudio first
    brew install portaudio
    pip install pyaudio

On Ubuntu/Debian:

.. code-block:: bash

    sudo apt install portaudio19-dev python3-dev
    pip install pyaudio

**FFmpeg Not Found**

.. code-block:: bash

    # macOS
    brew install ffmpeg
    
    # Ubuntu/Debian
    sudo apt install ffmpeg

**Permission Denied on macOS**

The application needs accessibility permissions:

1. Open **System Preferences** → **Security & Privacy** → **Privacy**
2. Select **Accessibility** in the left panel
3. Click the lock icon and enter your password
4. Add your terminal application or Python interpreter
5. Restart the voice recorder

**Microphone Access Denied**

1. Open **System Preferences** → **Security & Privacy** → **Privacy**
2. Select **Microphone** in the left panel
3. Add your terminal application or Python interpreter

**Ollama Connection Failed**

.. code-block:: bash

    # Check if Ollama is running
    ollama list
    
    # Start Ollama service
    ollama serve
    
    # Check the service is accessible
    curl http://localhost:11434/api/version

Development Installation
------------------------

For contributors and developers:

.. code-block:: bash

    # Clone and install with development dependencies
    git clone https://github.com/your-username/voice-recorder.git
    cd voice-recorder
    
    # Create development environment
    python -m venv .venv
    source .venv/bin/activate
    
    # Install with development dependencies
    pip install -e ".[dev,test]"
    
    # Install pre-commit hooks
    pre-commit install
    
    # Run tests to verify installation
    pytest
    
    # Run type checking
    mypy src/
    
    # Run linting
    flake8 src/

Next Steps
----------

After installation:

1. **Initialize Configuration**: Run ``voice-recorder init`` to set up your preferences
2. **Configure API Keys**: Add your OpenAI API key for cloud transcription
3. **Test Recording**: Try the basic functionality with your chosen transcription mode
4. **Customize Hotkeys**: Adjust hotkey bindings to your preferences
5. **Explore Features**: Try both basic and enhanced transcription modes

See the :doc:`quickstart` guide for detailed setup instructions.