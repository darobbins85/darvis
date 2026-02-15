# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Darvis is a cross-platform voice assistant with intelligent command processing, system tray integration, and optional waybar status display. It features wake word detection ("hey darvis"), speech-to-text, AI-powered responses via OpenCode CLI, and local/web application launching.

## Build/Lint/Test Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Run the application
./launch-darvis.sh

# Run both web and desktop interfaces (web-desktop sync)
./run.sh

# Run all tests
pytest tests/

# Run unit tests
pytest tests/ --cov=darvis --cov-report=html

# Run specific test categories (E2E)
pytest tests/e2e/ -m voice    # Voice tests
pytest tests/e2e/ -m gui      # GUI tests
pytest tests/e2e/ -m ai       # AI tests
pytest tests/e2e/ -m apps     # Application tests

# Lint code
flake8 darvis/
black darvis/ --check
pylint darvis/

# Format code
black darvis/
isort darvis/

# Desktop installation (Linux)
./install-desktop.sh
```

## Architecture

The codebase is organized into a modular structure:

```
darvis/
├── darvis/
│   ├── __init__.py      # Package init, exports list_microphones()
│   ├── config.py        # Constants, platform detection, web services mapping
│   ├── speech.py        # Voice recognition and TTS
│   ├── apps.py          # Local app detection and launching
│   ├── ai.py            # OpenCode CLI integration for AI responses
│   ├── ui.py            # Tkinter GUI, system tray, message handling
│   └── waybar_status.py # Waybar IPC for Linux status display
├── tests/
│   ├── test_*.py        # Unit tests
│   └── e2e/             # End-to-end tests (49 tests)
├── scripts/             # Waybar configuration scripts
└── docs/                # Feature and testing documentation
```

### Key Components

- **speech.py**: Handles microphone input, wake word detection ("hey darvis", "hey jarvis"), speech recognition via Google API, and text-to-speech
- **apps.py**: Parses .desktop files to detect installed applications, handles both local apps and web services (YouTube, GitHub, Gmail, etc.)
- **ai.py**: Routes queries to OpenCode CLI for AI-powered responses with session management
- **ui.py**: Tkinter-based GUI with speech bubbles, logo animations (green wake glow, red AI processing), timers, and system tray integration
- **waybar_status.py**: Provides real-time status updates for Linux waybar (idle, listening, processing, success, error states)

### Web-Desktop Sync

The app supports running both web and desktop interfaces simultaneously. The desktop app automatically detects if a web instance is running on localhost:5001 and establishes a SocketIO connection for real-time message sync. Use `./run.sh` to launch both.

### Configuration

- Wake words, web services, and GUI settings are in `darvis/config.py`
- Platform-specific app directories are auto-detected (Linux: /usr/share/applications, macOS: /Applications)
- Default working directory is the user's home folder (not project root)

## Platform-Specific Notes

- **Linux**: GTK/AppIndicator for system tray, optional waybar integration, xdg-open for URLs
- **macOS**: Native menubar integration, app mappings in config.py, 'open' command for URLs
- **Windows**: Win32 API integration, native display detection

## Testing Strategy

The project has comprehensive test coverage:
- Unit tests for individual modules (speech, apps, ai, waybar_status)
- E2E tests organized by category (voice, gui, ai, apps)
- Tests use pytest with fixtures for process management, voice simulation, and GUI verification
- Some tests require a display environment; headless testing has limited coverage
