# 🤖 Darvis Voice Assistant

A modern, cross-platform voice assistant with intelligent command processing, featuring system tray integration and optional waybar status display.

## ✨ Features

- **🎤 Voice Recognition**: Wake word detection ("hey darvis") and speech-to-text
- **🧠 AI Integration**: Powered by opencode CLI for intelligent responses
- **💻 Cross-Platform**: Works on Linux, macOS, and Windows
- **🎨 Modern UI**: Dark-themed tkinter interface with visual feedback
- **📱 System Tray**: Native system tray icon with show/hide functionality
- **📊 Waybar Integration**: Real-time status display for Linux/Hyprland users
- **🚀 Smart Commands**: Automatic local app detection with AI fallback

## 🏗️ Project Structure

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
├── README.md              # This file
├── requirements.txt       # Core dependencies
├── requirements-dev.txt   # Development dependencies
├── pytest.ini            # Test configuration
├── darvis.desktop        # Desktop integration
├── install-desktop.sh    # Desktop installer
└── launch-darvis.sh      # Application launcher
```

## 🚀 Quick Start

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

### Launch
```bash
./launch-darvis.sh  # Linux/macOS
```

### Voice Commands
- Say **"hey darvis"** to wake the assistant
- Try commands like:
  - "open calculator"
  - "open firefox"
  - "what is 2 + 2"

## 📊 Waybar Integration (Linux Only)

Darvis provides real-time status integration with waybar.

### Setup
```bash
# Configure waybar for Darvis integration
python3 scripts/configure-waybar.py

# Restart waybar
omarchy-restart-waybar
```

### Status Indicators
- 🤖 **Idle**: Ready for commands
- 🎤 **Listening**: Voice input detected
- ⚙️ **Processing**: AI/command execution
- ✅ **Success**: Command completed
- ❌ **Error**: Command failed

## 🛠️ Development

```bash
# Run tests
pytest

# Lint code
flake8 darvis/
black darvis/ --check

# Format code
black darvis/
isort darvis/
```

## 📋 Platform Support

### Linux
- **System Tray**: GTK/AppIndicator backends
- **Waybar**: Optional custom module with styled states
- **Display**: X11 and Wayland support

### macOS
- **System Tray**: Native macOS menubar integration
- **Display**: Native macOS display detection

### Windows
- **System Tray**: Win32 API integration
- **Display**: Native Windows display detection

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure cross-platform compatibility
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

---

**Built with ❤️ for the voice assistant community**