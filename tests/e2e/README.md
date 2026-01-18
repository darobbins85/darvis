# Darvis E2E Testing Suite

## Overview

This directory contains comprehensive end-to-end (E2E) tests for the Darvis Voice Assistant. These tests verify the complete user journey from voice commands through AI processing to GUI feedback and application launching.

## Test Structure

```
tests/e2e/
├── __init__.py              # Package initialization
├── conftest.py              # Pytest fixtures and configuration
├── test_voice_e2e.py        # Voice input and recognition tests
├── test_gui_e2e.py          # GUI interaction and visual feedback tests
├── test_ai_e2e.py           # AI query processing and response tests
└── test_apps_e2e.py         # Application launching and web service tests
```

## Prerequisites

### System Requirements
- Linux/macOS/Windows with audio support
- Python 3.8+ with virtual environment
- Working microphone and speakers (for full E2E testing)
- Sufficient disk space for test artifacts

### Dependencies
Install E2E testing dependencies:
```bash
pip install pytest>=7.0.0 psutil>=5.9.0
# Optional GUI automation:
# pip install pyautogui opencv-python pytesseract
```

### Environment Setup
1. Activate virtual environment:
   ```bash
   source venv/bin/activate
   ```

2. Ensure audio devices are available:
   ```bash
   python3 -c "import darvis.speech; darvis.speech.list_microphones()"
   ```

3. Verify OpenCode CLI setup (for AI testing):
   ```bash
   opencode --version
   ```

## Running E2E Tests

### Run All E2E Tests
```bash
pytest tests/e2e/
```

### Run Specific Test Categories
```bash
# Voice-related tests
pytest tests/e2e/ -m voice

# GUI-related tests
pytest tests/e2e/ -m gui

# AI-related tests
pytest tests/e2e/ -m ai

# Application launching tests
pytest tests/e2e/ -m apps
```

### Run Individual Test Files
```bash
pytest tests/e2e/test_voice_e2e.py
pytest tests/e2e/test_gui_e2e.py
pytest tests/e2e/test_ai_e2e.py
pytest tests/e2e/test_apps_e2e.py
```

### Run with Coverage
```bash
pytest tests/e2e/ --cov=darvis --cov-report=html
```

### Run Specific Test
```bash
pytest tests/e2e/test_voice_e2e.py::TestVoiceE2E::test_wake_word_detection -v
```

## Test Configuration

### Test Fixtures

**`darvis_process`** - Launches and manages Darvis application instance
- Starts Darvis in test mode
- Handles cleanup after tests
- Provides process monitoring

**`voice_simulator`** - Simulates voice input without audio hardware
- Injects wake words and commands
- Manages timing and sequencing
- Placeholder for actual audio simulation

**`gui_verifier`** - Verifies GUI state and visual feedback
- Checks speech bubble appearance
- Validates logo animations
- Monitors visual effects (requires pyautogui)

**`process_monitor`** - Monitors system processes for application launching
- Tracks process creation and termination
- Verifies application startup
- Provides baseline process comparison

### Configuration Options
Edit `tests/conftest.py` to modify:
- Test timeouts and delays
- Audio device selection
- GUI verification settings
- Process monitoring parameters

## Test Categories

### Voice Tests (`test_voice_e2e.py`)
- Wake word detection ("hey darvis", "play jarvis")
- Voice command processing
- Speech recognition timeout handling
- Background noise resistance
- Rapid activation handling

### GUI Tests (`test_gui_e2e.py`)
- Speech bubble display and content
- Logo animation effects (glow, processing)
- Visual feedback timing
- System tray integration
- Window management
- Performance and memory usage

### AI Tests (`test_ai_e2e.py`)
- Query processing and response generation
- Conversation continuity
- Response relevance and quality
- Error handling and timeouts
- Context awareness
- Response formatting

### Application Tests (`test_apps_e2e.py`)
- Local application launching (calculator, terminal, browser)
- Web service integration (YouTube, GitHub, Gmail)
- Process verification
- Launch performance
- Error handling for unknown apps
- Concurrent launch handling

## Test Execution Details

### Test Isolation
- Each test starts with clean application state
- Process monitoring prevents interference
- Automatic cleanup of launched applications
- State reset between test runs

### Performance Considerations
- Tests run sequentially to avoid resource conflicts
- Configurable timeouts prevent hanging
- Memory usage monitoring
- Process cleanup verification

### Error Handling
- Graceful handling of missing dependencies
- Skip tests when hardware unavailable
- Detailed error reporting
- Automatic retry mechanisms

## Debugging and Troubleshooting

### Common Issues

**Audio Device Problems**
```
Error: No audio devices available
Solution: Check microphone permissions and hardware connections
```

**GUI Automation Unavailable**
```
Error: pyautogui not available
Solution: Install pyautogui or run tests without GUI verification
```

**Application Launch Failures**
```
Error: Calculator not found
Solution: Verify application installation and PATH configuration
```

### Debug Mode
Run tests with detailed output:
```bash
pytest tests/e2e/ -v -s --tb=long
```

### Test Logs
Check generated log files:
- `pytest.log` - Test execution logs
- HTML coverage reports in `htmlcov/`
- Screenshots (if GUI automation enabled)

## CI/CD Integration

### GitHub Actions Example
```yaml
- name: Run E2E Tests
  run: |
    source venv/bin/activate
    pytest tests/e2e/ -m "not slow" --tb=short
- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

### Docker Testing
```dockerfile
FROM python:3.9-slim
# Install system dependencies for GUI testing
RUN apt-get update && apt-get install -y \
    xvfb \
    x11-utils \
    && rm -rf /var/lib/apt/lists/*
# Run tests with virtual display
CMD ["xvfb-run", "-a", "pytest", "tests/e2e/"]
```

## Extending the Test Suite

### Adding New Tests
1. Create test methods in appropriate files
2. Use existing fixtures for setup/teardown
3. Add appropriate pytest markers
4. Include docstrings with test purpose
5. Update this README

### Custom Fixtures
Add new fixtures in `conftest.py`:
```python
@pytest.fixture
def custom_fixture():
    # Setup code
    yield resource
    # Cleanup code
```

### Test Data Management
- Use parameterized tests for multiple inputs
- Store test data in separate files
- Mock external dependencies when possible

## Performance Benchmarks

### Expected Execution Times
- Voice tests: 30-60 seconds per test
- GUI tests: 20-45 seconds per test
- AI tests: 45-90 seconds per test (network dependent)
- App tests: 15-40 seconds per test

### Resource Usage
- Memory: < 200MB per test process
- CPU: < 50% during execution
- Disk: < 50MB for logs and artifacts

## Contributing

### Test Development Guidelines
- Write descriptive test names and docstrings
- Include both positive and negative test cases
- Use appropriate assertion methods
- Clean up resources properly
- Document test prerequisites

### Code Review Checklist
- [ ] Tests run without external dependencies
- [ ] Appropriate use of fixtures and markers
- [ ] Clear test isolation and cleanup
- [ ] Comprehensive error handling
- [ ] Performance considerations addressed

---

**Note**: These E2E tests require a complete Darvis installation and may interact with system resources. Run in isolated environments to avoid conflicts with production systems.</content>
<parameter name="filePath">tests/e2e/README.md