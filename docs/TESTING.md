# Darvis Voice Assistant - E2E Testing Guide

## Overview

This guide provides comprehensive end-to-end testing procedures for the Darvis voice assistant, featuring speech-bubble interface, darvis agent AI integration, and advanced visual feedback. All tests should be conducted in a Linux environment with microphone access and internet connectivity.

## 🧪 Test Environment Setup

### Prerequisites
- **OS**: Linux (Ubuntu/Debian/Arch recommended)
- **Python**: 3.13+
- **Microphone**: Working audio input device
- **Internet**: Required for speech recognition and AI features
- **Browser**: Firefox/Chromium for web service testing

### Installation Verification
```bash
# Verify Python environment
python3 --version  # Should be 3.13+

# Install dependencies
pip install -r requirements.txt

# Test microphone access
python3 -c "import darvis; darvis.list_microphones()"

# Test basic launch
python3 darvis.py  # Should start GUI without errors
```

## 🎯 Feature Test Cases

### 1. Application Launch & UI Elements

#### Test Case: UI-001 - Application Startup
**Objective**: Verify application launches correctly with speech-bubble interface

**Steps**:
1. Run `python3 -m darvis.ui`
2. Verify window appears with title "Darvis Voice Assistant"
3. Confirm presence of:
    - Manual input text field (top, always visible)
    - Speech bubble area (middle) initially empty
    - Timer display area (above logo, initially hidden)
    - Darvis logo (bottom-center) with animation capabilities
    - System tray icon (minimize to tray functionality)

**Expected Results**:
- ✅ Window opens with modern dark theme (#0f0f23)
- ✅ Speech bubble interface ready for messages
- ✅ Manual input field has blinking cursor
- ✅ Logo displays with glow effect capabilities
- ✅ System tray integration functional
- ✅ No console errors or warnings

### 2. Manual Input Functionality

#### Test Case: INPUT-001 - Manual Text Commands
**Objective**: Verify manual input processes commands with speech bubble feedback

**Steps**:
1. Start application
2. Click in manual input field (blinking cursor appears)
3. Type "open youtube" and press Enter
4. Observe speech bubble response and browser launch

**Expected Results**:
- ✅ Manual input field accepts text input
- ✅ Enter key submission triggers processing
- ✅ Input field clears after submission
- ✅ Yellow speech bubble: "Opening YouTube..."
- ✅ Browser opens YouTube successfully
- ✅ Green speech bubble: "YouTube opened successfully"

#### Test Case: INPUT-002 - Darvis Agent Manual Input
**Objective**: Test manual input with darvis agent AI processing

**Steps**:
1. Type "@darvis what is the capital of France?" and press Enter
2. Observe darvis agent processing with visual feedback
3. Wait for AI response in speech bubble

**Expected Results**:
- ✅ Red glowing eyes appear on logo during processing
- ✅ Red count-up timer starts (0:00, increments)
- ✅ Blue speech bubble appears with AI response
- ✅ Response contains accurate information
- ✅ Timer stops when response received
- ✅ No timeout errors within 5-minute limit

### 3. Voice Recognition & Wake Words

#### Test Case: VOICE-001 - Wake Word Detection
**Objective**: Verify wake word triggers activation

**Steps**:
1. Ensure microphone is working
2. Clearly say "hey darvis"
3. Observe logo glow and activation

**Expected Results**:
- ✅ Logo glows green when wake word detected
- ✅ Glow lasts for activation duration
- ✅ No false positives from similar words

#### Test Case: VOICE-002 - Voice Command Processing
**Objective**: Test complete voice command workflow with speech bubbles

**Steps**:
1. Say "hey darvis" (logo glows green)
2. Wait for activation (green countdown timer appears)
3. Say "open calculator" clearly
4. Observe speech bubble feedback and application launch

**Expected Results**:
- ✅ Wake word triggers green logo glow
- ✅ Green countdown timer appears (8 seconds, decreasing)
- ✅ Green speech bubble: "HEARD: open calculator"
- ✅ Yellow speech bubble: "Launching calculator..."
- ✅ Calculator application opens successfully
- ✅ Timer stops when command processed
- ✅ Success confirmation in speech bubble

### 4. AI Mode Functionality

#### Test Case: AI-001 - Darvis Agent Basic Query
**Objective**: Test basic darvis agent functionality

**Steps**:
1. Say "hey darvis" then "what is 2 + 2?"
2. Observe AI processing indicators
3. Wait for response in speech bubble

**Expected Results**:
- ✅ Wake word activates voice input
- ✅ Red glowing eyes during AI processing
- ✅ Red count-up timer during processing
- ✅ Blue speech bubble with correct answer (4)
- ✅ Processing completes within reasonable time
- ✅ No errors or timeouts

#### Test Case: AI-002 - Darvis Agent Complex Query
**Objective**: Test complex darvis agent responses with speech bubbles

**Steps**:
1. Say "hey darvis" then "explain recursion in programming"
2. Observe processing indicators and speech bubble response
3. Follow up with "@darvis can you give a python example?"

**Expected Results**:
- ✅ Red glowing eyes during AI processing
- ✅ Red count-up timer increments during processing
- ✅ Blue speech bubble with comprehensive explanation
- ✅ Follow-up query maintains conversation context
- ✅ Second blue speech bubble with code example
- ✅ 5-minute timeout protection active
- ✅ Cancel button appears for long queries
- ✅ Responses are accurate and helpful

### 5. Web Service Integration

#### Test Case: WEB-001 - YouTube Launch
**Objective**: Verify web service commands work

**Steps**:
1. Use manual input: "open youtube"
2. Or voice: "hey darvis" → "open youtube"

**Expected Results**:
- ✅ Default browser opens
- ✅ YouTube homepage loads
- ✅ Success confirmation in system messages

#### Test Case: WEB-002 - Multiple Web Services
**Objective**: Test various supported web services

**Test Commands**:
- "open google"
- "open github"
- "open gmail"
- "open netflix"
- "open spotify"

**Expected Results**:
- ✅ Each service opens in browser
- ✅ Correct URLs load
- ✅ Error handling for unavailable services

### 6. System Application Launch

#### Test Case: APP-001 - System Applications
**Objective**: Verify local application launching with intelligent detection

**Steps**:
1. Test installed applications:
   - "open signal" (should find signal-desktop)
   - "open calculator" (should find galculator or gnome-calculator)
   - "open terminal" (should find xterm, gnome-terminal, etc.)
   - "open editor" (should find gedit, kate, etc.)

2. Test unavailable applications:
   - "open steam" (should show "not installed" message)
   - "open photoshop" (should show "not found" message)

**Expected Results**:
- ✅ Installed applications launch successfully
- ✅ Uninstalled applications show clear "not installed" messages
- ✅ Intelligent detection finds correct command names
- ✅ Desktop file parsing works for GUI applications

### 7. Visual Feedback & Effects

#### Test Case: AI-003 - Cancel Button Functionality
**Objective**: Test manual cancellation of AI operations

**Steps**:
1. Submit a complex AI query that will take time
2. Observe cancel button appears (red)
3. Click cancel button during processing
4. Verify operation stops gracefully

**Expected Results**:
- ✅ Cancel button appears during AI operations
- ✅ Red button is clearly visible and clickable
- ✅ Clicking cancel stops AI processing
- ✅ Red speech bubble: "Operation cancelled by user"
- ✅ Timer stops and resets
- ✅ Logo eyes stop glowing
- ✅ No hanging processes or errors

#### Test Case: GFX-001 - Visual Effects & Animations
**Objective**: Verify glow effects, animations, and visual feedback

**Steps**:
1. Type in manual input field → observe cursor and focus
2. Say "hey darvis" → observe green logo glow
3. Submit AI query → observe red glowing eyes and pulsing
4. Receive response → observe speech bubble appearance

**Expected Results**:
- ✅ Logo glows green on wake word detection
- ✅ Logo eyes glow red during AI processing
- ✅ Pulsing animation (1-second intervals) when active
- ✅ Speech bubbles appear with smooth transitions
- ✅ Timer displays correctly (countdown/count-up)
- ✅ Visual effects don't impact performance

#### Test Case: GFX-002 - Timer System
**Objective**: Verify countdown and count-up timers with timeout protection

**Steps**:
1. Say "hey darvis" → observe green countdown timer (8 seconds)
2. Speak command before timeout → timer stops
3. Say "hey darvis" then ask complex AI question → observe red count-up
4. Wait for AI response or test 5-minute timeout behavior

**Expected Results**:
- ✅ Green countdown: 8 seconds decreasing by 1 each second
- ✅ Timer stops when voice command processed
- ✅ Red count-up: starts at 0:00, increments during AI processing
- ✅ 5-minute timeout protection prevents runaway operations
- ✅ Cancel button appears for operations over 5 seconds
- ✅ Timer displays prominently above logo

#### Test Case: GFX-003 - Speech Bubble System
**Objective**: Verify speech bubble creation, color coding, and message routing

**Steps**:
1. Say "hey darvis open youtube" → check green bubble
2. Submit manual command → check yellow status bubbles
3. Trigger AI query → check blue AI response bubbles
4. Cause error (invalid command) → check red error bubbles

**Expected Results**:
- ✅ Green bubbles: Voice input ("HEARD: [text]")
- ✅ Yellow bubbles: System status and command execution
- ✅ Blue bubbles: Darvis agent AI responses
- ✅ Red bubbles: Errors and cancellation messages
- ✅ Bubbles appear in chronological order
- ✅ Proper spacing and visual hierarchy

### 8. Error Handling

#### Test Case: ERROR-001 - Network Issues
**Objective**: Test behavior when internet unavailable

**Steps**:
1. Disconnect internet
2. Try voice commands
3. Try AI queries

**Expected Results**:
- ✅ Graceful degradation
- ✅ Clear error messages
- ✅ Manual input still works
- ✅ No application crashes

#### Test Case: ERROR-002 - Audio Issues
**Objective**: Test behavior with audio problems

**Steps**:
1. Disable microphone
2. Try voice commands
3. Verify manual input still works

**Expected Results**:
- ✅ Clear error messages for audio issues
- ✅ Manual input remains functional
- ✅ No crashes from audio failures

## 🔄 Regression Testing

### Automated Checks
```bash
# Syntax validation
python3 -m py_compile darvis.py

# Import validation
python3 -c "import darvis; print('Import successful')"

# Basic functionality
python3 -c "import darvis; print(darvis.list_microphones())"
```

### Performance Benchmarks
- **Startup Time**: < 3 seconds
- **Response Time**: Voice commands < 5 seconds
- **Memory Usage**: < 100MB during normal operation
- **CPU Usage**: < 10% during idle listening

## 📊 Test Results Template

```
Test Case: [ID]
Status: [PASS/FAIL]
Date: [YYYY-MM-DD]
Tester: [Name]
Environment: [OS/Python Version]
Steps Taken: [Detailed steps]
Expected Results: [What should happen]
Actual Results: [What actually happened]
Issues Found: [Any bugs or deviations]
Screenshots: [If applicable]
```

## 🚨 Known Issues & Limitations

- TTS may fail on some systems (gracefully handled)
- Speech recognition requires internet connection for Google API
- Some system applications may not be available on all Linux distributions
- Visual effects may vary across different window managers/themes
- AI operations limited to 5-minute timeout for safety
- Cancel button may not appear instantly for very quick operations

## 📞 Support

For test failures or issues:
1. Check console output for error messages
2. Verify microphone and internet connectivity
3. Test manual input as fallback
4. Check system logs for additional errors