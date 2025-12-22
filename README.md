# Darvis Voice Assistant

A cross-platform voice assistant with intelligent command processing, featuring system tray integration and optional waybar status display.

## Features

- **Cross-Platform**: Works on Linux, macOS, and Windows
- **Voice Recognition**: Wake word detection and speech-to-text
- **Intelligent Commands**: Automatic local app detection with AI fallback
- **Modern UI**: Dark-themed tkinter interface with visual feedback
- **System Tray**: Native system tray icon on all platforms
- **Waybar Integration**: Real-time status display for Linux/Hyprland users
- **Waybar Integration**: Optional enhanced status display for Linux/waybar users
- **Modern UI**: Dark-themed tkinter interface with visual feedback

## Platform Support

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

## Waybar Integration (Linux Only)

Darvis provides real-time status integration with waybar, showing live updates of the assistant's state in your status bar.

### Setup
```bash
# Configure waybar for Darvis integration
python3 scripts/configure-waybar.py

# Restart waybar to apply changes
omarchy-restart-waybar
```

### Status Indicators
- 🤖 **Idle**: Ready for commands
- 🎤 **Listening**: Processing voice input
- ⚙️ **Processing**: Executing commands or AI queries
- ✅ **Success**: Command completed successfully
- ❌ **Error**: Command failed or error occurred

### Manual Configuration
Add to your `~/.config/waybar/config.jsonc`:
```jsonc
"custom/darvis": {
  "exec": "python3 /path/to/darvis/scripts/darvis-waybar-status",
  "return-type": "json",
  "restart-interval": 0,
  "tooltip-format": "{tooltip}"
}
```

And add `"custom/darvis"` to your `modules-right` array.

## Installation

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

## Usage

### Basic Launch
```bash
./launch-darvis.sh  # Linux/macOS
python darvis.py    # Windows
```

### Voice Commands
- Say "hey darvis" to wake the assistant
- Follow with commands like:
  - "open calculator"
  - "open firefox"
  - "what time is it?"

### System Tray
- Right-click the tray icon for menu options
- Left-click to show/hide the main window

### Waybar Integration (Linux only)
The application automatically detects waybar and provides enhanced status display with states:
- `idle`: Default state
- `listening`: When processing voice input
- `processing`: When executing commands
- `success`: Command completed successfully
- `error`: Command failed

## Configuration

### Waybar Custom Module
Add to your `~/.config/waybar/config.jsonc`:

```jsonc
"custom/darvis": {
  "exec": "echo '🤖'",
  "return-type": "string",
  "interval": 1,
  "on-click": "pkill -USR1 waybar"  // Toggle visibility
}
```

### Waybar Styling
Add to your `~/.config/waybar/style.css`:

```css
#custom-darvis {
  color: #9CBB6C;
  font-size: 22px;
  min-width: 100px;
}

#custom-darvis.listening {
  color: #FFA500;
  animation: pulse 1.5s infinite;
}

#custom-darvis.processing,
#custom-darvis.thinking {
  color: #87CEEB;
}

#custom-darvis.speaking {
  color: #98FB98;
}

#custom-darvis.success {
  color: #90EE90;
}

#custom-darvis.error {
  color: #FF6B6B;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.6; }
  100% { opacity: 1; }
}
```

## Architecture

```
darvis/
├── ui.py           # Cross-platform GUI and system tray
├── speech.py       # Voice recognition and TTS
├── apps.py         # Application detection and launching
├── ai.py           # AI integration and processing
├── config.py       # Configuration constants
├── waybar_status.py # Waybar IPC communication
└── __init__.py

scripts/
├── darvis-waybar-status   # Waybar custom module script
└── configure-waybar.py    # Waybar configuration tool
```

## Development

```bash
# Run tests
pytest

# Lint code
black darvis/
flake8 darvis/

# Format code
black darvis/
isort darvis/
```

## Cross-Platform Compatibility

The system tray implementation uses `pystray` which provides:
- **Linux**: GTK, AppIndicator, and Xorg backends
- **macOS**: Native macOS system tray
- **Windows**: Win32 API integration

Waybar integration is Linux-only but optional - the core functionality works without it on all platforms.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure cross-platform compatibility
5. Submit a pull request

## License

MIT License - see LICENSE file for details.