# Enhanced Transcription Guide

This guide explains how to use enhanced transcription features that combine speech-to-text with AI-powered text improvement.

## Overview

Enhanced transcription goes beyond basic speech-to-text by using Large Language Models (LLMs) to improve the transcribed text. This can:

- Fix grammar and punctuation errors
- Improve sentence structure and coherence
- Make the text more readable and professional
- Preserve the original meaning while enhancing clarity

## Available Providers

### OpenAI Enhanced Service
- **Transcription**: OpenAI Whisper API
- **Enhancement**: OpenAI GPT (gpt-3.5-turbo or gpt-4)
- **Requirements**: OpenAI API key
- **Best for**: High accuracy, professional use

### Local Enhanced Service
- **Transcription**: Local Whisper model
- **Enhancement**: Ollama LLM (local)
- **Requirements**: Ollama running locally
- **Best for**: Privacy, offline use

## Configuration

### Basic Setup

1. **Initialize Configuration**:
   ```bash
   voice-recorder init
   ```

2. **Choose Enhanced Mode**: During setup, select enhanced transcription when prompted.

3. **Configure Providers**: Set up your chosen provider (OpenAI or Local).

### Advanced Configuration

#### Enhanced Transcription Prompt

You can customize how the AI enhances your text by configuring the enhancement prompt:

**Default Prompt**:
```
Please improve the following transcribed text by fixing grammar, punctuation, and making it more coherent while preserving the original meaning. Only return the improved text without any explanations or additional commentary.
```

**Custom Prompts Examples**:

1. **Formal Business Style**:
   ```
   Please convert the following transcribed text into formal business language with proper grammar and punctuation. Maintain the original meaning while making it professional and clear.
   ```

2. **Academic Style**:
   ```
   Please improve the following transcribed text to academic writing standards with proper grammar, punctuation, and formal language. Maintain the original meaning while enhancing clarity and scholarly tone.
   ```

3. **Creative Writing**:
   ```
   Please enhance the following transcribed text with more vivid language and creative expression while maintaining the original meaning and improving flow and readability.
   ```

4. **Technical Documentation**:
   ```
   Please improve the following transcribed text to technical documentation standards with clear, precise language and proper technical terminology while maintaining accuracy.
   ```

#### Sound Configuration

You can customize the audio feedback sounds to distinguish between basic and enhanced transcription:

**Current Configuration** (Distinct Sounds):
```ini
[sound]
enabled = True
volume = 5

# Basic transcription - Lower pitched tone
basic_sound_type = tone
basic_start_frequency = 600.0
basic_end_frequency = 800.0

# Enhanced transcription - Higher pitched tone
enhanced_sound_type = tone
enhanced_start_frequency = 1200.0
enhanced_end_frequency = 1600.0

duration = 0.3
```

**Alternative Configuration** (Mixed Sound Types):
```ini
[sound]
enabled = True
volume = 5

# Basic transcription - Simple beep
basic_sound_type = beep
basic_start_frequency = 800.0
basic_end_frequency = 800.0

# Enhanced transcription - Ascending tone
enhanced_sound_type = tone
enhanced_start_frequency = 1000.0
enhanced_end_frequency = 1400.0

duration = 0.3
```

**Sound Type Options**:
- `tone` - Custom frequency sweep (ascending/descending)
- `beep` - Simple system beep
- `none` - No sound feedback

**Frequency Guidelines**:
- **Low (400-800 Hz)**: Deep, bass-like sounds
- **Medium (800-1200 Hz)**: Standard notification sounds
- **High (1200-2000 Hz)**: Bright, attention-grabbing sounds

#### Configuration File Example

```ini
[transcription]
mode = openai

[transcription.openai]
api_key = your_openai_api_key_here
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
enhanced_key = ctrl

[audio]
sample_rate = 16000
channels = 1
format = wav
chunk_size = 1024

[sound]
enabled = True
volume = 5
basic_sound_type = tone
basic_start_frequency = 600.0
basic_end_frequency = 800.0
enhanced_sound_type = tone
enhanced_start_frequency = 1200.0
enhanced_end_frequency = 1600.0
duration = 0.3

[general]
auto_paste = True
```

## Usage

### Hotkeys

- **Basic Transcription**: Press your configured basic key (default: Right Shift)
- **Enhanced Transcription**: Press your configured enhanced key (default: Left Ctrl)

### Example Workflow

1. **Start Recording**: Press your enhanced transcription hotkey
2. **Speak**: Dictate your content naturally
3. **Stop Recording**: Press the hotkey again
4. **Processing**: The system will:
   - Transcribe your speech to text
   - Send the text to the LLM for enhancement
   - Paste the improved text at your cursor position

### Example Results

**Original Transcription**:
```
"um so i was thinking about the project and uh we need to like maybe change the approach because the current one isn't working very well"
```

**Enhanced Version**:
```
"I was thinking about the project, and we need to change our approach because the current one isn't working very well."
```

## Tips for Best Results

### Prompt Design

1. **Be Specific**: Clearly state what you want the AI to do
2. **Set Constraints**: Specify what the AI should NOT do
3. **Maintain Context**: Ensure the prompt preserves your intent
4. **Test and Iterate**: Try different prompts to find what works best

### Recording Quality

1. **Clear Speech**: Speak clearly and at a moderate pace
2. **Minimize Background Noise**: Use a quiet environment
3. **Proper Distance**: Position microphone at appropriate distance
4. **Consistent Volume**: Maintain steady speaking volume

### Provider Selection

**Choose OpenAI if**:
- You need high accuracy
- You have reliable internet
- You're comfortable with cloud processing
- You need professional-quality results

**Choose Local if**:
- You prioritize privacy
- You work offline frequently
- You have a powerful local machine
- You want to avoid API costs

## Troubleshooting

### Common Issues

1. **Empty Enhanced Text**: Check your API key and internet connection
2. **Poor Enhancement**: Try adjusting the creativity/temperature setting
3. **Slow Processing**: Consider using a smaller model or local processing
4. **Incorrect Enhancements**: Review and refine your custom prompt

### Performance Optimization

1. **Model Selection**: Smaller models are faster but less accurate
2. **Creativity Settings**: Lower values (0.1-0.3) for more conservative improvements
3. **Prompt Length**: Shorter prompts are processed faster
4. **Batch Processing**: Consider processing multiple recordings together

## Advanced Features

### Custom Prompts

You can create highly specialized prompts for different use cases:

- **Legal Documents**: Focus on precision and formal language
- **Creative Writing**: Emphasize style and flow
- **Technical Content**: Prioritize accuracy and clarity
- **Casual Communication**: Maintain natural tone while improving grammar

### Provider-Specific Settings

**OpenAI Settings**:
- `gpt_model`: Choose between gpt-3.5-turbo (faster) or gpt-4 (better quality)
- `gpt_creativity`: Control how creative the improvements are (0.0-2.0)

**Local Settings**:
- `ollama_model`: Choose from available local models
- `ollama_creativity`: Control creativity level (0.0-2.0)
- `ollama_base_url`: Customize Ollama server location

## Configuration Examples

See the `examples/` directory for complete configuration examples:

- `config_enhanced_transcription.ini` - Basic enhanced transcription setup
- `config_enhanced_transcription_prompt.ini` - Custom prompt examples
- `config_distinct_sounds.ini` - Different frequencies for basic/enhanced
- `config_mixed_sounds.ini` - Different sound types for basic/enhanced
- `config_high_quality.ini` - High-quality settings for professional use 