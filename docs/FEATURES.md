# Darvis Voice Assistant - Features Documentation

## Overview

Darvis is a modern, interactive voice assistant featuring a sophisticated speech-bubble interface, advanced AI integration via a specialized darvis agent, and comprehensive visual feedback system. The assistant provides seamless voice and text input with intelligent command processing that automatically switches between local application launching and AI-powered responses.

## 🎯 Core Features

### 1. Advanced Voice Recognition & Wake Word Detection

- **Description**: Continuous listening for wake words with sophisticated speech processing
- **Supported Wake Words**: "hey darvis", "hey jarvis", "play darvis", "play jarvis", "hi darvis", "hi jarvis"
- **Technology**: Google Speech Recognition API with noise filtering
- **Visual Feedback**:
  - Logo glows green when wake word detected
  - Logo eyes glow red during AI processing
  - 8-second voice input timeout with countdown timer

### 2. Speech Bubble Interface

- **Description**: Modern chat-like interface replacing traditional console output
- **Message Types**: Color-coded speech bubbles for different content types
- **Color Scheme**:
  - 🟢 **Green Bubbles**: User voice input ("HEARD: open calculator")
  - 🔵 **Blue Bubbles**: AI responses from darvis agent
  - 🟡 **Yellow Bubbles**: System status messages
  - 🔴 **Red Bubbles**: Error messages and warnings
- **Layout**: Bubbles appear in chronological order with proper spacing

### 3. Darvis Agent AI Integration

- **Description**: Specialized AI agent with conversation context and session management
- **Session Continuity**: Use "@darvis" prefix for follow-up queries in ongoing conversations
- **Smart Timeouts**: 5-minute protection for AI operations with manual cancel option
- **Context Awareness**: Maintains conversation history within sessions
- **Fallback Processing**: Automatic AI invocation for unrecognized commands

### 4. Intelligent Command Processing

- **Local Commands**: Auto-detection and launching of 20+ web services and local applications
- **Web Services**: YouTube, Google, GitHub, Gmail, Slack, Notion, Jira, and more
- **System Apps**: Calculator, terminal, text editor, browser with intelligent detection
- **Smart Detection**: Automatic fallback from specific apps to generic categories
- **Error Handling**: Graceful degradation with clear user feedback

## 🎨 User Interface

### Speech Bubble Layout Structure

```
┌─────────────────────────────────────┐
│ [Manual Input Field]                │ ← Always visible text input
├─────────────────────────────────────┤
│ 🟢 HEARD: open calculator            │ ← Green bubble: voice input
│ 🟡 Opening calculator...             │ ← Yellow bubble: status
│ 🔵 Calculator launched successfully  │ ← Blue bubble: AI response
├─────────────────────────────────────┤
│              [TIMER]                │ ← Dynamic timer display
├─────────────────────────────────────┤
│           [CANCEL BUTTON]           │ ← Red button during AI ops
├─────────────────────────────────────┤
│                        [DARVIS LOGO]│ ← Animated with glow effects
└─────────────────────────────────────┘
```

### Visual Elements

- **Theme**: Modern dark theme (#0f0f23 primary, #1a1a2e secondary)
- **Speech Bubbles**: Rounded rectangles with color-coded backgrounds
- **Message Types**:
  - 🟢 **Green Bubbles**: Voice input recognition ("HEARD: [text]")
  - 🔵 **Blue Bubbles**: AI responses from darvis agent
  - 🟡 **Yellow Bubbles**: System status and command execution
  - 🔴 **Red Bubbles**: Errors, warnings, and cancel notifications
- **Timer Display**: Large, prominent countdown/count-up above logo
- **Cancel Button**: Red button appears during AI operations (5+ minute timeout)
- **Logo Animation**: Glowing effects with pulsing brightness variations

### Interactive Feedback

- **Typing**: Manual input field with blinking cursor and focus highlighting
- **Speech Recognition**: Green speech bubble appears when voice input is recognized
- **System Messages**: Yellow bubbles for status updates, red bubbles for errors
- **AI Responses**: Blue speech bubbles contain darvis agent responses
- **Voice Timer**: Green countdown (8 seconds) during voice input activation
- **AI Timer**: Red count-up during darvis agent processing (5-minute timeout)
- **Cancel Button**: Appears during AI operations for manual interruption
- **Logo Effects**:
  - Green glow on wake word detection
  - Red glowing eyes during AI processing
  - Pulsing animation (1-second intervals) when active

## 🔧 Technical Specifications

### Dependencies

- **Python 3.13+**
- **speech_recognition**: Google Speech Recognition API integration
- **pyttsx3**: Text-to-speech synthesis (gracefully handles failures)
- **Pillow**: Image processing for logo transparency and animations
- **tkinter**: Cross-platform GUI framework with custom theming
- **opencode**: CLI integration for darvis agent AI functionality

### Architecture Overview

```
User Input (Voice/Text)
    ↓
Speech Recognition / Text Processing
    ↓
Command Classification:
├── Local Apps → App Detection → Launch
├── Web Services → URL Mapping → Browser Launch
└── AI Queries → Darvis Agent → Response
    ↓
Speech Bubble Display (Color-coded)
    ↓
Visual Feedback (Glows, Timers, Animations)
```

### Audio & System Requirements

- **Microphone**: Required for voice input (auto-detection with fallback)
- **Audio System**: ALSA/PulseAudio on Linux (warnings are normal)
- **Speech API**: Internet connection for Google Speech Recognition
- **Display**: X11/Wayland support with proper window management
- **System Tray**: GTK integration for Linux desktop environments

## 🚀 Usage Workflow

### Voice Commands

1. **Launch**: `./launch-darvis.sh` or `python -m darvis.ui`
2. **Wake**: Say "hey darvis" (logo glows green)
3. **Command**: Speak clearly "open calculator" or "what is recursion?"
4. **Response**: Speech bubble appears with result or AI processing begins
5. **AI Continuation**: Use "@darvis explain this further" for follow-up questions

### Manual Text Input

1. **Launch**: Start the application
2. **Type**: Enter command in text field (always visible)
3. **Submit**: Press Enter to process
4. **Response**: Speech bubble displays result immediately

### Darvis Agent Conversations

- **Session Continuity**: AI conversations maintain context within 5-minute windows
- **Follow-up Queries**: Prefix with "@darvis" to continue previous conversations
- **Smart Timeouts**: 5-minute protection prevents runaway AI operations
- **Manual Cancel**: Red cancel button appears for long-running queries
- **Visual Feedback**: Red glowing eyes and count-up timer during AI processing

## 📝 Command Examples

### Local Commands (Instant Processing)

- **"open youtube"** → Green bubble: "Opening YouTube..." → Browser launches
- **"open calculator"** → Yellow bubble: "Launching calculator..." → App opens
- **"open github"** → Blue bubble: "Opening GitHub..." → Browser navigates
- **"open terminal"** → System detects and launches appropriate terminal emulator

### Darvis Agent AI Commands

- **"what is recursion?"** → Blue bubble with detailed explanation from darvis agent
- **"@darvis can you give a code example?"** → Continued conversation with context
- **"explain quantum computing in simple terms"** → Comprehensive AI response
- **"help me debug this python code: [paste code]"** → AI analysis and suggestions

### Web Services (20+ Supported)

- **Communication**: "open slack", "open gmail", "open discord"
- **Development**: "open github", "open gitlab", "open jira"
- **Productivity**: "open notion", "open trello", "open calendar"
- **Entertainment**: "open netflix", "open spotify", "open youtube"

## 🔍 Troubleshooting

### Common Issues

- **Microphone Issues**: Run `python3 -c "import darvis.speech; darvis.speech.list_microphones()"`
- **Speech Recognition**: Requires internet for Google Speech API
- **Logo Display**: Check PIL/Pillow installation and asset file permissions
- **Glow Effects**: May not work on all tkinter themes or window managers
- **AI Timeouts**: 5-minute limit prevents runaway operations (use cancel button)
- **Session Continuity**: Use "@darvis" prefix for continued conversations

### Debug Information

- **Console Output**: Run `python3 -m darvis.ui` for detailed logging
- **Microphone Test**: Use the built-in microphone listing function
- **Manual Input**: Always available as fallback to voice recognition
- **AI Testing**: Test darvis agent with simple queries first

