# 🤖 Darvis Voice Assistant - Project Context

## Overview
Darvis is a modern, cross-platform voice assistant with intelligent command processing. It features system tray integration, optional waybar status display, and both desktop and web interfaces. The application uses wake word detection ("hey darvis") and integrates with the opencode CLI for AI-powered responses.

## Architecture
The application follows a modular design with these main components:

- **`ui.py`**: User interface and GUI components using tkinter with system tray support
- **`speech.py`**: Speech recognition and text-to-speech functionality
- **`ai.py`**: AI integration using opencode CLI for intelligent responses
- **`apps.py`**: Application detection and launching functionality
- **`config.py`**: Configuration constants and settings
- **`waybar_status.py`**: Waybar IPC communication for Linux status updates

## Key Features
- **Voice Recognition**: Wake word detection ("hey darvis") and speech-to-text
- **AI Integration**: Powered by opencode CLI for intelligent responses
- **Cross-Platform**: Works on Linux, macOS, and Windows
- **Modern UI**: Dark-themed tkinter interface with visual feedback
- **System Tray**: Native system tray icon with show/hide functionality
- **Waybar Integration**: Real-time status display for Linux/Hyprland users
- **Smart Commands**: Automatic local app detection with AI fallback
- **Web Interface**: Synchronized chat interface using Flask and SocketIO

## Building and Running

### Prerequisites
- Python 3.8+
- opencode CLI (for AI functionality)

### Installation
```bash
# Clone the repository
git clone https://github.com/darobbins85/darvis.git
cd darvis

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# For Linux system tray support
pip install PyGObject

# For desktop integration (Linux)
./install-desktop.sh
```

### Launching
```bash
./launch-darvis.sh  # Linux/macOS
```

Or for development:
```bash
source venv/bin/activate && python3 -m darvis.ui
```

### Web Interface
```bash
python3 web_chat.py  # Starts web interface on http://localhost:5001
```

## Voice Commands
- Say **"hey darvis"** to wake the assistant
- Try commands like:
  - "open calculator"
  - "open firefox"
  - "what is 2 + 2"

## Waybar Integration (Linux Only)
Darvis provides real-time status integration with waybar:
- Configure with: `python3 scripts/configure-waybar.py`
- Status indicators: 🤖 Idle, 🎤 Listening, ⚙️ Processing, ✅ Success, ❌ Error

## Development Conventions

### Code Style
- **Imports**: Standard library first, then third-party, one per line
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_CASE` for constants
- **Formatting**: 4-space indentation, ~100 character line length
- **Strings**: Double quotes

### Testing
- Run complete test suite: `python -m pytest tests/`
- With coverage: `python -m pytest tests/ --cov=darvis --cov-report=html`
- Lint with: `flake8 darvis/`, `black darvis/ --check`
- Format with: `black darvis/`, `isort darvis/`

### Error Handling
- Use try/except blocks for external operations
- Print error messages to console for debugging
- Handle specific exceptions appropriately

## Project Structure
```
darvis/
├── assets/                 # Logo and visual assets
├── darvis/                 # Main package
│   ├── __init__.py
│   ├── ai.py              # AI integration (opencode CLI)
│   ├── apps.py            # Application detection and launching
│   ├── config.py          # Configuration constants
│   ├── speech.py          # Voice recognition and TTS
│   ├── ui.py              # Cross-platform GUI and system tray
│   └── waybar_status.py   # Waybar IPC communication
├── docs/                   # Documentation
├── scripts/                # Utility scripts
│   ├── configure-waybar.py
│   └── darvis-waybar-status
├── tests/                  # Unit tests
├── archive/                # Legacy code (darvis_legacy.py)
├── AGENTS.md              # Development guidelines
├── LICENSE                # MIT License
├── README.md              # Project documentation
├── requirements.txt       # Core dependencies
├── requirements-dev.txt   # Development dependencies
├── pytest.ini            # Test configuration
├── darvis.desktop        # Desktop integration
├── install-desktop.sh    # Desktop installer
└── launch-darvis.sh      # Application launcher
```

## Dependencies
Core dependencies include:
- `pyaudio`, `pyttsx3`, `SpeechRecognition` for voice functionality
- `Pillow` for image handling
- `pystray` for system tray
- `flask`, `flask-socketio`, `python-socketio` for web interface
- `pytest` for testing

## Platform Support
- **Linux**: Full support with system tray (GTK/AppIndicator), Waybar integration, X11/Wayland
- **macOS**: System tray and display detection
- **Windows**: System tray and display detection

## Contributing
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure cross-platform compatibility
5. Submit a pull request