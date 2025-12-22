# Darvis Voice Assistant - Features Documentation

## Overview

Darvis is a modern, interactive voice assistant with both voice and manual input capabilities. It features a sleek dark-themed interface with real-time visual feedback and intelligent command processing that automatically switches between local and AI-powered responses.

## 🎯 Core Features

### 1. Voice Recognition & Wake Word Detection

- **Description**: Continuous listening for wake words to activate voice commands
- **Supported Wake Words**: "hey darvis", "hey jarvis", "play darvis", "play jarvis", "hi darvis", "hi jarvis"
- **Technology**: Google Speech Recognition API
- **Visual Feedback**:
  - Logo glows green when wake word detected
  - Logo eyes glow red when AI processing is active

### 2. Manual Text Input

- **Description**: Always-available text input field for commands
- **Activation**: Press Enter to submit commands
- **Visual Feedback**: Input field glows white while typing, blinking cursor until selected
- **Processing**: Same command processing as voice input

### 3. Intelligent Command Processing

- **Description**: Automatic switching between local and AI-powered responses
- **Default Behavior**: Local command processing for known applications and web services
- **AI Fallback**: Automatically invokes AI when local processing fails
- **User Feedback**: Info messages indicate when AI is being used
- **AI Integration**: Uses opencode CLI for intelligent responses

### 4. Smart Command Processing

- **Web Services**: Open YouTube, Google, GitHub, Gmail, Netflix, Spotify
- **System Apps**: Launch calculator, terminal, text editor, browser
- **Fallback**: Direct command execution or AI assistance for unrecognized commands

## 🎨 User Interface

### Layout Structure

```
┌─────────────────────────────────────┐
│ [Manual Input Field]                │ ← White glow when typing
├─────────────────────────────────────┤
│ [Speech Recognition Display]        │ ← Green glow during updates
├─────────────────────────────────────┤
│ [System Messages & Responses]       │ ← Yellow glow on new messages
├─────────────────────────────────────┤
│                        [DARVIS LOGO]│ ← Green glow on wake, red eyes for AI
└─────────────────────────────────────┘
```

### Visual Elements

- **Theme**: Dark background (#000000) with styled components
- **Text Areas**: Dark grey backgrounds (#333333) with colored text
- **Glow Effects**: Dynamic highlights (2-3px border) for active elements
- **Typography**: Arial 16pt for inputs, Arial 24pt for branding
- **Cursor**: Blinking cursor in manual input field until selected

### Interactive Feedback

- **Typing**: Manual input field glows white during text entry
- **Speech Recognition**: Heard text area glows green while being updated
- **System Responses**: Info area glows yellow when new messages arrive
- **Wake Word**: Logo glows green when activation phrases detected
- **AI Processing**: Logo eyes glow red when AI (opencode) is being invoked

## 🔧 Technical Specifications

### Dependencies

- **Python 3.13+**
- **speech_recognition**: Voice input processing
- **pyttsx3**: Text-to-speech (optional, silenced on errors)
- **Pillow**: Image processing for logo transparency
- **tkinter**: GUI framework (built-in)

### File Structure

```
darvis/
├── darvis.py              # Main application
├── darvis-logo.png        # UI logo (150x150)
├── darvis-logo-hires.png  # High-res source (1024x1024)
├── darvis-black.png       # Original logo
├── AGENTS.md             # Development guide
├── requirements.txt      # Python dependencies
└── run.sh               # Launch script
```

### Audio Requirements

- **Microphone**: Required for voice input
- **Audio System**: ALSA (Linux) - warnings are normal
- **Speech API**: Internet connection for Google Speech Recognition

## 🚀 Usage Workflow

### Voice Commands

1. Start application: `./run.sh` or `python darvis.py`
2. Say wake word: "hey darvis"
3. Speak command: "open youtube"
4. Assistant responds and executes (uses AI automatically if needed)

### Manual Input

1. Start application
2. Type command in input field: "open youtube"
3. Press Enter
4. Assistant processes and executes (uses AI automatically if needed)

### Intelligent Processing

- **Local Commands**: Web services and apps are handled locally by default
- **AI Fallback**: When local processing fails, AI is automatically invoked
- **User Feedback**: Info messages indicate when AI processing is active
- **Seamless Experience**: No manual mode switching required

## 📝 Command Examples

### Local Commands (Processed Locally)

- "open youtube" → Opens YouTube in browser
- "open google" → Opens Google search
- "open github" → Opens GitHub
- "open calculator" → Launches calculator
- "open terminal" → Opens terminal window
- "open editor" → Launches text editor

### AI Commands (Processed by AI)

- "what is the weather today?" → AI provides weather information
- "explain quantum computing" → AI explains the concept
- "write a hello world program" → AI generates code
- Any unrecognized commands → Automatically sent to AI for processing

## 🔍 Troubleshooting

### Common Issues

- **No microphone detected**: Check audio devices with `list_microphones()`
- **Speech not recognized**: Ensure internet connection for Google API
- **Logo not loading**: Check file permissions and PIL installation
- **Glow effects not working**: Requires tkinter with proper theme support

### Debug Mode

- Run with `python darvis.py` to see console output
- Check microphone list with `list_microphones()` function
- Manual input bypasses voice recognition entirely

