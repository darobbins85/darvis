# 🤖 Darvis Voice Assistant

A modern, cross-platform voice assistant with intelligent command processing, featuring a sleek speech-bubble interface, advanced AI integration via specialized darvis agent, and comprehensive visual feedback system.

## ✨ Features

- **🎤 Voice Recognition**: Wake word detection ("hey darvis") with real-time speech-to-text
- **🧠 Advanced AI**: Integrated with specialized darvis agent for context-aware conversations
- **💬 Speech Bubbles**: Modern chat-like interface with color-coded message bubbles
- **⏰ Smart Timeouts**: 5-minute AI session protection with cancel functionality
- **🎨 Visual Effects**: Glowing logo, pulsing animations, and dynamic visual feedback
- **📱 System Tray**: Native system tray with show/hide and quit options
- **📊 Waybar Integration**: Real-time status display for Linux/Hyprland users
- **🚀 Intelligent Commands**: Auto-detection of 20+ web services and local applications

## 🏗️ Project Structure

```
darvis/
├── assets/                 # Logo and visual assets
│   ├── darvis-black.png       # Original high-res logo
│   ├── darvis-logo-hires.png  # High-res transparent version
│   └── darvis-logo.png        # UI-sized logo (150x150)
├── darvis/                 # Main package
│   ├── __init__.py
│   ├── ai.py              # Advanced AI integration with darvis agent
│   ├── apps.py            # Intelligent app detection and launching
│   ├── config.py          # Configuration constants and app mappings
│   ├── speech.py          # Voice recognition and TTS
│   ├── ui.py              # Speech-bubble GUI with visual effects
│   └── waybar_status.py   # Waybar IPC communication
├── docs/                   # Comprehensive documentation
├── scripts/                # Utility scripts
│   ├── configure-waybar.py
│   └── darvis-waybar-status
├── tests/                  # Complete test suite (23/23 passing)
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
  - "open calculator" or "open firefox"
  - "what is 2 + 2" (AI-powered)
  - "@darvis explain this further" (continued conversations)

### Advanced Usage Examples

#### AI Conversations with Context
```bash
# Start a conversation
"hey darvis, what is recursion in programming?"

# Continue the conversation (maintains context)
"@darvis can you show me a python example?"

# Ask follow-up questions
"@darvis how does this compare to loops?"
```

#### Complex Multi-step Tasks
```bash
# Code review request
"hey darvis, review this python function: def factorial(n): return n * factorial(n-1) if n > 1 else 1"

# Follow-up questions
"@darvis what are the potential issues with this implementation?"
"@darvis how would you fix the recursion limit problem?"
```

#### Development Assistance
```bash
# Debugging help
"hey darvis, my python script is giving a recursion error"

# Get specific help
"@darvis show me how to add a recursion limit check"
"@darvis explain what sys.setrecursionlimit does"
```

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
- 🤖 **Idle**: Ready for voice/text commands
- 🎤 **Listening**: Voice input active (8-second timeout)
- ⚙️ **Processing**: Command execution in progress
- 🧠 **AI Active**: Darvis agent processing (5-minute timeout)
- ✅ **Success**: Command completed successfully
- ❌ **Error**: Command failed or timed out
- 🔄 **Cancel**: User cancelled long-running operation

## 🧠 Advanced AI Features

### Darvis Agent Integration
- **Context-Aware Conversations**: Specialized darvis agent maintains conversation context
- **Session Continuity**: Use "@darvis" prefix for follow-up queries within 5-minute windows
- **Smart Timeouts**: 5-minute protection for AI operations with manual cancel button
- **Intelligent Processing**: Automatic switching between local commands and AI responses

#### Using the @darvis Prefix
The `@darvis` prefix enables continued conversations with full context preservation:

- **Follow-up Questions**: `@darvis can you elaborate on that?`
- **Code Examples**: `@darvis show me the implementation`
- **Clarification**: `@darvis what do you mean by X?`
- **Session Management**: Each conversation maintains context for ~5 minutes

### Speech Bubble Interface
- **Modern UI**: Chat-like message bubbles instead of traditional console output
- **Color Coding**: Green for user input, blue for AI responses, yellow for system messages
- **Visual Effects**: Glowing logo, pulsing animations, and dynamic feedback
- **Responsive Design**: Scales appropriately across different screen sizes

## 🛠️ Development

```bash
# Run tests (23/23 passing)
pytest

# Lint code
flake8 darvis/
black darvis/ --check

# Format code
black darvis/
isort darvis/
```

## 📋 Platform Support

### Linux ✅ **Fully Implemented**
- **System Tray**: Native GTK integration with show/hide functionality
- **Waybar**: Complete IPC integration with real-time status updates
- **Display**: X11 and Wayland support with proper window management
- **Desktop Integration**: .desktop file with menu integration

### macOS 🔄 **Framework Ready**
- **System Tray**: Native macOS menubar integration hooks
- **Display**: Native macOS display detection framework
- **Architecture**: Ready for macOS-specific implementations

### Windows 🔄 **Framework Ready**
- **System Tray**: Win32 API integration framework
- **Display**: Native Windows display detection framework
- **Architecture**: Ready for Windows-specific implementations

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