# Contributing to Voice Recorder

We welcome contributions to the Voice Recorder project! This document provides guidelines for contributing.

## Development Setup

### Prerequisites

- Python 3.11 or higher
- macOS (for full functionality)
- Git

### Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/your-username/voice-recorder.git
   cd voice-recorder
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install development dependencies:**
   ```bash
   pip install -e ".[dev,test,docs]"
   ```

4. **Install system dependencies:**
   ```bash
   brew install portaudio ffmpeg
   ```

5. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/voice_recorder

# Run specific test categories
pytest tests/unit/        # Unit tests only
pytest tests/integration/ # Integration tests only
```

### Code Quality

We maintain high code quality standards:

```bash
# Type checking
mypy src/

# Code formatting
black src/ tests/

# Linting
flake8 src/ tests/

# Import sorting
isort src/ tests/

# Run all quality checks
pytest && mypy src/ && black --check src/ && flake8 src/ && isort --check-only src/
```

### Documentation

Build and test documentation locally:

```bash
# Build documentation
make docs-html

# Serve locally
cd docs && python -m http.server 8000
```

## Code Standards

### Architecture

The project follows Clean Architecture principles:

- **Domain Layer**: Core business logic and models
- **Services Layer**: Application orchestration
- **Infrastructure Layer**: External service adapters
- **CLI Layer**: User interface components

### Code Style

- **Type Hints**: All code must include comprehensive type hints
- **Docstrings**: Use Google-style docstrings for all public methods
- **Error Handling**: Provide clear, actionable error messages
- **Testing**: Write tests for all new functionality

### Example Code Structure

```python
"""Module docstring describing purpose."""

from typing import Optional, Protocol

from voice_recorder.domain.models import SomeModel


class SomeInterface(Protocol):
    """Interface docstring."""
    
    def some_method(self, param: str) -> Optional[SomeModel]:
        """Method docstring.
        
        Args:
            param: Description of parameter
            
        Returns:
            Description of return value
            
        Raises:
            ValueError: When param is invalid
        """
        ...


class SomeImplementation:
    """Implementation docstring."""
    
    def __init__(self, dependency: SomeInterface) -> None:
        """Initialize with dependency injection."""
        self._dependency = dependency
    
    def some_method(self, param: str) -> Optional[SomeModel]:
        """Implementation of interface method."""
        if not param:
            raise ValueError("Parameter cannot be empty")
        
        return self._dependency.some_method(param)
```

## Contribution Process

### Issues

1. **Search existing issues** before creating new ones
2. **Use issue templates** when available
3. **Provide clear reproduction steps** for bugs
4. **Include system information** (OS, Python version, etc.)

### Pull Requests

1. **Create feature branch** from main:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following code standards

3. **Add tests** for new functionality

4. **Update documentation** if needed

5. **Run quality checks**:
   ```bash
   pytest && mypy src/ && black --check src/ && flake8 src/
   ```

6. **Commit with clear messages**:
   ```bash
   git commit -m "Add feature: description of what was added"
   ```

7. **Push and create PR**:
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Fill out PR template** with:
   - Clear description of changes
   - Related issue numbers
   - Testing performed
   - Breaking changes (if any)

### Commit Messages

Follow conventional commit format:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test additions/changes
- `chore:` Maintenance tasks

Examples:
```
feat: add local Whisper transcription support
fix: resolve audio recording memory leak
docs: update configuration guide
test: add integration tests for transcription service
```

## Areas for Contribution

### High Priority

- **Cross-platform support**: Linux and Windows compatibility
- **Performance optimizations**: Reduce memory usage and latency
- **Additional transcription providers**: Support for more services
- **Enhanced error handling**: Better recovery and user feedback
- **Accessibility features**: Screen reader support, keyboard navigation

### Medium Priority

- **GUI interface**: Desktop application interface
- **Plugin system**: Extensible architecture for custom providers
- **Batch processing**: Process multiple audio files
- **Cloud storage integration**: Direct upload to cloud services
- **Advanced audio processing**: Noise reduction, audio enhancement

### Documentation

- **Tutorial videos**: Step-by-step setup guides
- **Use case examples**: Real-world usage scenarios
- **Configuration recipes**: Common setup patterns
- **Troubleshooting guides**: Solutions for common issues
- **API examples**: More code examples

## Community

### Communication

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community support
- **Pull Request Reviews**: Code review and discussion

### Code of Conduct

We are committed to providing a welcoming and inclusive environment. All contributors are expected to:

- Be respectful and constructive in all interactions
- Focus on what is best for the community
- Show empathy towards other community members
- Accept constructive criticism gracefully
- Help newcomers and less experienced contributors

### Recognition

Contributors are recognized in:

- **CHANGELOG.md**: Major contributions noted in release notes
- **README.md**: Active contributors acknowledged
- **Git history**: All commits properly attributed

## Security

If you discover a security vulnerability, please:

1. **Do not open a public issue**
2. **Email security concerns** to: security@voicerecorder.app
3. **Include detailed information** about the vulnerability
4. **Allow time for response** before public disclosure

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

If you have questions about contributing:

1. Check existing **GitHub Issues** and **Discussions**
2. Review this **CONTRIBUTING.md** guide
3. Look at **existing code** for examples
4. **Open a GitHub Discussion** for general questions
5. **Open a GitHub Issue** for specific bugs or feature requests

Thank you for contributing to Voice Recorder! 🎙️