# Voice Recorder Documentation

This directory contains comprehensive documentation for the Voice Recorder project.

## Architecture Documentation

### [Transcription Architecture Comparison](./TRANSCRIPTION_ARCHITECTURE_COMPARISON.md)
Detailed comparison between the old and new transcription module architectures, highlighting improvements and benefits.

### [Proposed Transcription Architecture](./PROPOSED_TRANSCRIPTION_ARCHITECTURE.md)
Comprehensive proposal for the new transcription module architecture with detailed implementation examples.

### [Enhanced Transcription Guide](./ENHANCED_TRANSCRIPTION.md)
Guide for using enhanced transcription features with LLM post-processing.

## Project Management

### [Housekeeping Summary](./HOUSEKEEPING_SUMMARY.md)
Comprehensive summary of the housekeeping work performed to improve code organization, maintainability, and architecture.

## Troubleshooting

### [Hotkey Troubleshooting](./HOTKEY_TROUBLESHOOTING.md)
Common issues and solutions for hotkey functionality on macOS.

## Development

### [Claude Development Notes](./CLAUDE.md)
Development notes and insights from working with Claude AI assistant.

## Project Structure

```
voice-recorder/
├── docs/                          # Documentation
├── examples/                      # Configuration examples
├── src/voice_recorder/           # Source code
│   ├── api/                      # Application entry points
│   ├── cli/                      # Command-line interface
│   ├── domain/                   # Core business logic
│   ├── infrastructure/           # External dependencies
│   └── services/                 # Application services
├── tests/                        # Test suite
└── README.md                     # Main project README
```

## Quick Links

- [Main README](../README.md) - Project overview and setup
- [Configuration Examples](../examples/) - Sample configuration files
- [Source Code](../src/voice_recorder/) - Application source code
- [Tests](../tests/) - Test suite 