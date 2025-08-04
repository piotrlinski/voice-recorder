Quick Start
===========

This guide will get you up and running with the Voice Recorder in just a few minutes.

Prerequisites
-------------

* Python 3.11+ installed
* macOS 10.14+ (for full functionality)
* Microphone access permissions
* Internet connection (for OpenAI transcription) or local models setup

Installation
------------

1. **Install the package**::

    git clone https://github.com/your-username/voice-recorder.git
    cd voice-recorder
    pip install -e .

2. **Install system dependencies**::

    # Install PortAudio (required for PyAudio)
    brew install portaudio
    
    # Install FFmpeg (required for local Whisper)
    brew install ffmpeg

Initial Setup
-------------

1. **Initialize configuration**::

    voice-recorder init

   This will launch an interactive configuration wizard that will guide you through:
   
   * Choosing transcription mode (OpenAI cloud vs local)
   * Setting up API keys (if using OpenAI)
   * Configuring hotkeys
   * Setting preferences

2. **Configure API key** (for OpenAI mode):
   
   When prompted, enter your OpenAI API key. You can get one from:
   https://platform.openai.com/api-keys

3. **Test microphone permissions**:
   
   The app will request microphone access on first run. Grant permission
   when prompted by macOS.

First Recording
---------------

1. **Start the application**::

    voice-recorder

   You should see output like::

    2025-08-04 13:23:42,882 - voice_recorder - INFO - Voice recorder started successfully!
    2025-08-04 13:23:42,882 - voice_recorder - INFO - Press Ctrl+C to stop

2. **Try basic transcription**:
   
   * Press and hold **Right Shift**
   * Speak clearly: "Hello, this is a test recording"
   * Release **Right Shift**
   * The transcribed text should appear and be pasted automatically

3. **Try enhanced transcription**:
   
   * Press and hold **Left Ctrl**
   * Speak: "um so like i think we should maybe consider the new approach"
   * Release **Left Ctrl**
   * You should get polished text like: "I think we should consider the new approach."

Configuration Examples
----------------------

OpenAI Cloud Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

For highest accuracy with internet connection::

    [transcription]
    mode = openai

    [transcription.openai]
    api_key = sk-your-openai-key-here
    whisper_model = whisper-1
    gpt_model = gpt-3.5-turbo
    gpt_creativity = 0.3

    [controls]
    basic_key = shift_r
    enhanced_key = ctrl_l

    [general]
    auto_paste = true

Local Offline Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

For privacy and offline use::

    [transcription]
    mode = local

    [transcription.local]
    whisper_model = small
    ollama_base_url = http://localhost:11434
    ollama_model = llama3.1

    [controls]
    basic_key = shift_r
    enhanced_key = ctrl_l

    [general]
    auto_paste = true

Understanding Recording Modes
-----------------------------

Basic Mode (Right Shift)
~~~~~~~~~~~~~~~~~~~~~~~~~

* **What it does**: Converts speech directly to text
* **Speed**: Fast (~2-3 seconds)
* **Quality**: Good transcription accuracy
* **Use cases**: Quick notes, casual dictation
* **Example**: 
  
  * Input: "um so i think we should uh maybe consider the new approach"
  * Output: "Um, so I think we should, uh, maybe consider the new approach."

Enhanced Mode (Left Ctrl)
~~~~~~~~~~~~~~~~~~~~~~~~~~

* **What it does**: Transcribes speech then improves the text with AI
* **Speed**: Slower (~5-10 seconds)
* **Quality**: Professional, polished text
* **Use cases**: Business writing, formal documents, presentations
* **Example**:

  * Input: "um so i think we should uh maybe consider the new approach"
  * Output: "I think we should consider the new approach."

Enhanced mode improvements:

* Removes filler words (um, uh, like, you know)
* Fixes grammar and punctuation
* Improves sentence structure
* Makes text more professional
* Maintains original meaning

Common Usage Patterns
---------------------

Email Writing
~~~~~~~~~~~~~

1. Open your email client
2. Position cursor in the email body
3. Press **Left Ctrl** (enhanced mode)
4. Dictate your email naturally
5. Release key - polished text appears automatically

Meeting Notes
~~~~~~~~~~~~~

1. Open your note-taking app
2. Use **Right Shift** for quick, raw notes
3. Use **Left Ctrl** for polished action items
4. Mix both modes as needed

Code Documentation
~~~~~~~~~~~~~~~~~~

1. Position cursor in your code comments
2. Use **Left Ctrl** for professional documentation
3. Dictate explanations of complex logic
4. Get clean, readable documentation

Troubleshooting
---------------

No Text Appears
~~~~~~~~~~~~~~~

* Check microphone permissions in System Preferences
* Verify the app has Accessibility permissions
* Try speaking louder or closer to the microphone
* Check your API key (for OpenAI mode)

Hotkeys Don't Work
~~~~~~~~~~~~~~~~~~

* Grant Accessibility permissions:
  
  1. Open **System Preferences** → **Security & Privacy** → **Privacy**
  2. Select **Accessibility**
  3. Add your terminal or Python interpreter
  4. Restart the application

Poor Transcription Quality
~~~~~~~~~~~~~~~~~~~~~~~~~~

* Speak clearly and at moderate pace
* Reduce background noise
* Use a better microphone
* Try a larger Whisper model (medium/large) for local mode
* Check your internet connection (for OpenAI mode)

Application Won't Start
~~~~~~~~~~~~~~~~~~~~~~~

* Check Python version: ``python --version`` (must be 3.11+)
* Install system dependencies: ``brew install portaudio ffmpeg``
* Check configuration: ``voice-recorder config show``
* Recreate config: ``voice-recorder config reset``

Next Steps
----------

* **Customize hotkeys**: Edit ``~/.voicerecorder/config.ini`` to change key bindings
* **Try local models**: Set up Ollama for offline enhanced transcription
* **Adjust AI creativity**: Tune the ``gpt_creativity`` setting for different writing styles
* **Explore prompts**: Customize the enhancement prompt for specific use cases

For more detailed information, see:

* :doc:`configuration` - Detailed configuration options
* :doc:`api/index` - Programming interface documentation
* Troubleshooting guide in the main README - Common issues and solutions