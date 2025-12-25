# Darvis Chat Interface - Test Scenarios & User Experience

## Overview
This document outlines the expected behavior of the Darvis chat interface and provides testing procedures to verify functionality.

## Expected User Experience

### 1. Application Launch
- **Default State**: Listening mode is OFF, no messages displayed
- **UI Layout**:
  - Text conversation area (top, shows chat history)
  - Manual input field (middle, different background color)
  - Listening mode toggle (bottom, below input field)
  - Timer and logo (bottom)

### 2. Listening Mode Toggle
- **OFF by default**: No "Darvis is Listening..." message
- **When toggled ON**: Shows center-aligned "Darvis is Listening..." message
- **When toggled OFF**: Shows center-aligned "Darvis is not listening" message

### 3. Manual Input (Text Chat)
1. **User types message** in input field
2. **Presses Enter**
3. **Expected flow**:
   - User message appears immediately: right-aligned bubble with input field background color
   - AI processing begins (red glowing eyes, count-up timer)
   - AI response appears: left-aligned blue bubble
   - Timer stops, eyes stop glowing

### 4. Voice Input
1. **Enable listening mode**
2. **Say wake word**: "hey darvis"
3. **Expected flow**:
   - Shows "Darvis heard you - What's up?"
   - Green countdown timer (8 seconds)
   - User speaks command
   - Voice transcribed: right-aligned green bubble
   - AI processes: red eyes, count-up timer
   - AI response: left-aligned blue bubble

### 5. Message Ordering
- **Chronological flow**: Messages appear from top to bottom (oldest to newest)
- **User messages**: Right-aligned with input field background color
- **AI messages**: Left-aligned in blue
- **System messages**: Center-aligned (listening status, errors)
- **Latest messages visible**: Auto-scroll to bottom

## Test Scenarios

### Scenario 1: Basic Text Chat
**Steps**:
1. Launch application
2. Verify listening mode is OFF (no status message)
3. Type "hello" in input field
4. Press Enter

**Expected Results**:
- ✅ User message "hello" appears in right-aligned bubble with input field background
- ✅ Red glowing eyes and count-up timer start
- ✅ AI response appears in left-aligned blue bubble
- ✅ Timer stops, eyes return to normal
- ✅ Conversation flows chronologically

### Scenario 2: Listening Mode Toggle
**Steps**:
1. Launch application
2. Click listening mode toggle ON
3. Verify "Darvis is Listening..." appears center-aligned
4. Click listening mode toggle OFF
5. Verify "Darvis is not listening" appears center-aligned

**Expected Results**:
- ✅ Toggle changes state correctly
- ✅ Status messages appear center-aligned
- ✅ No voice processing when OFF

### Scenario 3: Voice Input
**Steps**:
1. Enable listening mode
2. Say "hey darvis"
3. Wait for activation
4. Say "what is 2+2"
5. Wait for response

**Expected Results**:
- ✅ Wake word triggers activation
- ✅ "Darvis heard you - What's up?" appears
- ✅ Green countdown timer starts
- ✅ Voice input appears in right-aligned green bubble
- ✅ AI response appears in left-aligned blue bubble
- ✅ No GUI freezing or blocking

### Scenario 4: Multiple Messages
**Steps**:
1. Send text message "hello"
2. Wait for AI response
3. Send text message "how are you"
4. Wait for AI response
5. Send text message "tell me a joke"

**Expected Results**:
- ✅ All user messages appear right-aligned with input background
- ✅ All AI responses appear left-aligned in blue
- ✅ Messages flow chronologically from top to bottom
- ✅ No message processing stops or freezes
- ✅ Each interaction completes properly

### Scenario 5: Error Handling
**Steps**:
1. Disable internet connection
2. Try sending a message

**Expected Results**:
- ✅ Error message appears in center-aligned red bubble
- ✅ No GUI freezing or crashes
- ✅ User can continue sending messages

## Known Issues to Verify Fixed

### Issue 1: GUI Freezing
- **Problem**: Interface froze during testing
- **Fix**: Made speak() calls asynchronous (background threads)
- **Test**: Send multiple messages rapidly, verify no freezing

### Issue 2: Message Ordering
- **Problem**: User text appeared "out of place and below AI response"
- **Fix**: Implemented chronological insertion at tk.END with scroll to bottom
- **Test**: Verify user message appears before AI response

### Issue 3: Message Processing Stops
- **Problem**: "next message seemed to never get processed"
- **Fix**: Added error handling in update_gui loop, made speak() non-blocking
- **Test**: Send multiple sequential messages, verify all are processed

## Performance Expectations

- **Response Time**: Text input should show user message immediately
- **AI Processing**: Should complete within 30 seconds for simple queries
- **GUI Responsiveness**: No blocking or freezing during AI processing
- **Message Display**: Instant visual feedback for all interactions

## Testing Checklist

- [ ] Application launches without default messages
- [ ] Listening mode toggle works correctly
- [ ] Manual input shows user message immediately
- [ ] AI responses appear in correct order and formatting
- [ ] Voice input works without freezing
- [ ] Multiple messages process sequentially
- [ ] Error conditions handled gracefully
- [ ] Chat bubbles display correctly (alignment, colors)
- [ ] Chronological message flow maintained
- [ ] No GUI blocking or freezing

## Debug Information

If issues occur, check:
1. Console output for error messages
2. Message queue processing (should be non-blocking)
3. Threading issues (speak() calls should be in background threads)
4. Text widget insertion and scrolling behavior
5. Timer and glow effect state management