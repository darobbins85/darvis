# Darvis Voice Assistant - E2E Testing Guide

## Overview

This guide provides comprehensive end-to-end testing procedures for all Darvis voice assistant features. Tests should be conducted in a Linux environment with microphone access and internet connectivity.

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
**Objective**: Verify application launches correctly with all UI elements

**Steps**:
1. Run `python3 darvis.py`
2. Verify window appears with title "Darvis Voice Assistant"
3. Confirm presence of:
   - Manual input text field (top)
   - Speech recognition text area (middle)
   - System messages text area (bottom)
   - AI Mode button (bottom-left)
   - Darvis logo (bottom-center)

**Expected Results**:
- ✅ Window opens with dark theme
- ✅ All UI elements visible and properly positioned
- ✅ "Darvis is Listening..." message appears in system area
- ✅ No console errors

### 2. Manual Input Functionality

#### Test Case: INPUT-001 - Manual Text Commands
**Objective**: Verify manual input processes commands correctly

**Steps**:
1. Start application
2. Click in manual input field
3. Type "open youtube" and press Enter
4. Observe visual feedback and browser launch

**Expected Results**:
- ✅ Input field glows green while typing
- ✅ Green flash when Enter pressed
- ✅ Input field clears after submission
- ✅ Browser opens YouTube
- ✅ "Opening youtube" appears in system messages

#### Test Case: INPUT-002 - AI Mode Manual Input
**Objective**: Test manual input with AI mode enabled

**Steps**:
1. Click "AI Mode" button (turns green)
2. Type "what is the capital of France?" and press Enter
3. Observe AI response

**Expected Results**:
- ✅ AI Mode button shows "AI Mode: ON"
- ✅ Query appears in system messages
- ✅ AI response appears after processing
- ✅ No errors in processing

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
**Objective**: Test complete voice command workflow

**Steps**:
1. Say "hey darvis"
2. Wait for activation (logo glow)
3. Say "open calculator"
4. Observe application launch

**Expected Results**:
- ✅ Wake word triggers activation
- ✅ Voice command recognized and displayed
- ✅ Calculator application opens
- ✅ Success message in system area

### 4. AI Mode Functionality

#### Test Case: AI-001 - AI Mode Toggle
**Objective**: Verify AI mode switching works correctly

**Steps**:
1. Click AI Mode button
2. Verify button changes to "AI Mode: ON" (green)
3. Click again to disable
4. Verify button changes to "AI Mode: OFF" (red)

**Expected Results**:
- ✅ Button toggles between ON/OFF states
- ✅ Visual feedback (color changes) works
- ✅ State persists during session

#### Test Case: AI-002 - AI Query Processing
**Objective**: Test AI-powered responses

**Steps**:
1. Enable AI Mode
2. Say "hey darvis" then "explain recursion in programming"
3. Wait for AI response

**Expected Results**:
- ✅ AI query sent to processing system
- ✅ Response appears in system messages
- ✅ No timeout errors
- ✅ Response is relevant to query

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
**Objective**: Verify local application launching

**Steps**:
1. Test each command:
   - "open calculator"
   - "open terminal"
   - "open editor"

**Expected Results**:
- ✅ Applications launch successfully
- ✅ Appropriate applications open (galculator, xterm, gedit)
- ✅ Error messages for unavailable applications

### 7. Visual Feedback & Effects

#### Test Case: GFX-001 - Glow Effects
**Objective**: Verify all glow effects work correctly

**Steps**:
1. Type in manual input field → observe green glow
2. Say "hey darvis" → observe logo glow
3. Submit command → observe text area glows
4. Receive response → observe info area glow

**Expected Results**:
- ✅ All glow effects trigger appropriately
- ✅ Green borders appear (2-3px)
- ✅ Effects last 1 second then disappear
- ✅ No performance impact from effects

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

- TTS may fail on some systems (silently ignored)
- Speech recognition requires internet connection
- Some system applications may not be available on all distributions
- Glow effects may not work on all tkinter themes

## 📞 Support

For test failures or issues:
1. Check console output for error messages
2. Verify microphone and internet connectivity
3. Test manual input as fallback
4. Check system logs for additional errors