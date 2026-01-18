# Darvis Voice Assistant - E2E Testing Guide

## Overview

This guide provides comprehensive end-to-end testing procedures for the Darvis voice assistant, featuring both **automated E2E tests** and **manual testing procedures**. The automated tests provide continuous regression testing, while manual tests validate user experience and edge cases.

### Testing Levels

1. **Automated E2E Tests** - Continuous integration, regression testing (49 tests)
2. **Manual E2E Tests** - User experience validation, exploratory testing
3. **Unit Tests** - Component-level testing (pytest suite)

All tests should be conducted in a Linux environment with microphone access and internet connectivity.

## 🤖 Automated E2E Testing Framework

### Overview
The automated E2E testing framework provides comprehensive, continuous testing of all Darvis functionality. Built with pytest, it includes 49 tests covering voice input, GUI interactions, AI responses, and application launching.

### Test Structure
```
tests/e2e/
├── conftest.py              # Test fixtures and configuration
├── test_voice_e2e.py        # Voice input and recognition (12 tests)
├── test_gui_e2e.py          # GUI interactions and feedback (10 tests)
├── test_ai_e2e.py           # AI query processing and responses (15 tests)
└── test_apps_e2e.py         # Application launching and web services (12 tests)
```

### Running Automated Tests

#### Run All E2E Tests
```bash
source venv/bin/activate
pytest tests/e2e/
# Expected: 49 passed ✅
```

#### Run Specific Test Categories
```bash
# Voice functionality tests
pytest tests/e2e/ -m voice

# GUI interaction tests
pytest tests/e2e/ -m gui

# AI response tests
pytest tests/e2e/ -m ai

# Application launching tests
pytest tests/e2e/ -m apps
```

#### Development and Debugging
```bash
# Verbose output with failure details
pytest tests/e2e/ -v --tb=short

# Run specific test
pytest tests/e2e/test_voice_e2e.py::TestVoiceE2E::test_wake_word_detection -v

# Stop on first failure
pytest tests/e2e/ -x

# Generate coverage report
pytest tests/e2e/ --cov=darvis --cov-report=html
```

### Test Fixtures

**`darvis_process`** - Launches and manages Darvis application instances
- Starts Darvis in test mode
- Handles cleanup between tests
- Provides process monitoring

**`voice_simulator`** - Simulates voice input without hardware
- Injects wake words and commands
- Manages timing and sequencing

**`gui_verifier`** - Validates GUI state and visual feedback
- Checks speech bubble appearance
- Verifies logo animations

**`process_monitor`** - Monitors system processes
- Tracks application launches
- Verifies process creation

### Test Coverage

#### Voice Tests (12 tests)
- Wake word detection ("hey darvis", "play jarvis")
- Voice command processing and AI routing
- Speech recognition timeout handling
- Background noise resistance
- Rapid activation scenarios

#### GUI Tests (10 tests)
- Speech bubble display and color coding
- Logo animation effects (glow, processing)
- Visual feedback timing and transitions
- System tray integration
- Window management and performance

#### AI Tests (15 tests)
- Query processing and response generation
- Conversation continuity and context
- Response relevance and quality validation
- Error handling and timeout scenarios
- Multi-turn conversation flows

#### Application Tests (12 tests)
- Local application launching (calculator, terminal, browser)
- Web service integration (YouTube, GitHub, Gmail)
- Process verification and launch timing
- Unknown application error handling
- Concurrent launch scenarios

### CI/CD Integration

The automated tests are designed for continuous integration:

```yaml
# Example GitHub Actions
- name: Run E2E Tests
  run: |
    source venv/bin/activate
    pytest tests/e2e/ -x --tb=short
- name: Generate Coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

### Test Reliability Features

- **Process Cleanup**: Automatic cleanup of Darvis processes between tests
- **Mock Integration**: Realistic simulation of external dependencies
- **Error Resilience**: Graceful handling of GUI environment issues
- **Cross-Platform**: Works with or without display/GUI automation
- **Fast Execution**: ~3-4 minutes for full test suite

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

### Automated E2E Tests
```bash
# Run full automated E2E test suite
source venv/bin/activate
pytest tests/e2e/

# Run with coverage reporting
pytest tests/e2e/ --cov=darvis --cov-report=html
```

### Manual Regression Checks
```bash
# Syntax validation
python3 -m py_compile darvis.py

# Import validation
python3 -c "import darvis; print('Import successful')"

# Basic functionality
python3 -c "import darvis; print(darvis.list_microphones())"

# Unit tests
pytest tests/ -v
```

### Performance Benchmarks
- **Application Startup**: < 3 seconds
- **E2E Test Suite**: < 4 minutes (49 tests)
- **Voice Command Response**: < 5 seconds
- **Memory Usage**: < 100MB during normal operation
- **CPU Usage**: < 10% during idle listening
- **Test Reliability**: 100% pass rate in CI/CD

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

### Automated Test Issues
For automated E2E test failures:
1. Check pytest output for specific failure details
2. Run with verbose logging: `pytest tests/e2e/ -v -s`
3. Verify virtual environment is activated
4. Check for missing dependencies: `pip install -r requirements.txt`
5. Review test fixtures in `tests/e2e/conftest.py`

### Manual Test Issues
For manual testing failures:
1. Check console output for error messages
2. Verify microphone and internet connectivity
3. Test manual input as fallback
4. Check system logs for additional errors
5. Ensure GUI environment supports visual effects

### Common Issues
- **GUI tests fail**: May be running in headless environment
- **Voice tests fail**: Microphone permissions or hardware issues
- **AI tests fail**: Network connectivity or OpenCode CLI issues
- **App tests fail**: Target applications not installed on system

### Getting Help
- Automated tests: Check `tests/e2e/README.md` for detailed documentation
- Manual tests: Follow the step-by-step procedures in this guide
- Report issues: Include pytest output, system info, and reproduction steps