# Remote Access Design Specification

**Date:** 2026-03-17  
**Feature:** Remote Web UI Access with Voice I/O  
**Approach:** Browser WebRTC + Simple Auth

## Overview

Enable remote access to Darvis via a web browser, allowing the user to control and interact with the voice assistant from any machine on any network. The server runs on Linux, while the client (with voice I/O) runs in a browser on Mac/Windows.

## Architecture

### Operating Modes

| Mode | Desktop GUI | Web UI Binding | Access |
|------|-------------|---------------|--------|
| Local | Enabled | 127.0.0.1:5001 | Localhost only |
| Remote | Disabled | 0.0.0.0:5001 | Anywhere via browser |

A startup flag or config option selects the mode:
- `DARVIS_MODE=local` (default) - current behavior
- `DARVIS_MODE=remote` - remote access enabled

### Components

1. **Flask-SocketIO Server** - Handles HTTP and WebSocket connections
2. **Authentication Layer** - Session-based password protection
3. **Voice Pipeline** - WebSocket streaming for audio input/output
4. **Web Client** - Browser-based UI with WebRTC audio

## Server Changes

### Network Configuration

- Default binding: `127.0.0.1` (localhost only)
- Remote binding: `0.0.0.0` (all interfaces)
- Config: `WEB_APP_HOST` in `config.py`

### Authentication

- Simple session-based auth with Flask-Login
- Password stored as environment variable `DARVIS_WEB_PASSWORD`
- Hashed using Werkzeug security functions
- Login page: `GET /login` - renders password form
- Login handler: `POST /login` - validates credentials
- Protected routes redirect to login if not authenticated
- Session expires after 24 hours

### WebSocket Events

| Event | Direction | Description |
|-------|-----------|-------------|
| `voice_start` | Client→Server | Client began recording |
| `voice_data` | Client→Server | Audio chunk (PCM) |
| `voice_end` | Client→Server | Client stopped recording |
| `tts_start` | Server→Client | Server beginning TTS |
| `tts_audio` | Server→Client | TTS audio chunk |
| `tts_end` | Server→Client | TTS playback complete |

## Client (Browser) Changes

### Login Page

- Simple HTML form: password input + submit button
- POST to `/login` endpoint
- On success: redirect to main chat interface
- On failure: show error message, stay on login

### Main Chat Interface

- Existing chat UI enhanced with voice controls
- Login state checked on page load; redirect if not authenticated

### Voice Input (WebRTC)

Use `AudioWorklet` instead of deprecated `createScriptProcessor`:

```javascript
// In main thread
const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
const audioContext = new AudioContext();
const source = audioContext.createMediaStreamSource(stream);

// Load AudioWorklet processor
await audioContext.audioWorklet.addModule('/static/js/voice-processor.js');

const processor = new AudioWorkletNode(audioContext, 'voice-processor');
source.connect(processor);
processor.connect(audioContext.destination);

// voice-processor.js runs in worklet thread
class VoiceProcessor extends AudioWorkletProcessor {
    process(inputs, outputs, parameters) {
        const input = inputs[0];
        if (input.length > 0) {
            const channelData = input[0];
            // Convert Float32 to Int16 PCM and send via WebSocket
            const pcmData = new Int16Array(channelData.length);
            for (let i = 0; i < channelData.length; i++) {
                pcmData[i] = Math.max(-1, Math.min(1, channelData[i])) * 32767;
            }
            this.port.postMessage(pcmData);
        }
        return true;
    }
}
registerProcessor('voice-processor', VoiceProcessor);
```

### Voice Output (Web Audio API)

Reuse a single `AudioContext` for all TTS playback:

```javascript
// Create once at initialization
const ttsAudioContext = new AudioContext();
let audioQueue = [];
let isPlaying = false;

socket.on('tts_audio', (data) => {
    // Decode base64 audio data
    const binaryString = atob(data.audio);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
    }
    
    // Decode WAV format from server
    ttsAudioContext.decodeAudioData(bytes.buffer, (buffer) => {
        audioQueue.push(buffer);
        playNext();
    });
});

function playNext() {
    if (isPlaying || audioQueue.length === 0) return;
    isPlaying = true;
    const buffer = audioQueue.shift();
    const source = ttsAudioContext.createBufferSource();
    source.buffer = buffer;
    source.connect(ttsAudioContext.destination);
    source.onended = () => {
        isPlaying = false;
        playNext();
    };
    source.start();
}
```

### Visual Indicators

- Microphone icon: red when recording, gray when idle
- Speaker icon: animated when playing audio
- Status text: "Listening...", "Speaking...", "Processing..."

## Voice Pipeline

### Input Path

1. Browser captures audio via WebRTC `getUserMedia`
2. Audio processed through ScriptProcessor (4096 samples)
3. Converted to PCM16 format
4. Sent to server via WebSocket `voice_data` event
5. Server receives chunks, accumulates into buffer
6. Silence detection: client analyzes audio levels; when average amplitude < 0.01 for 1.5 seconds, sends `voice_end` event
7. Server processes accumulated audio through STT

### Processing

- Uses existing `darvis.speech` module for STT
- Uses existing `darvis.ai` module for query processing
- Uses existing TTS for response generation

### Output Path

1. TTS generates audio (PCM format)
2. Server chunks audio into 4096-sample segments
3. Sends each chunk via WebSocket `tts_audio` event
4. Client buffers and plays via Web Audio API
5. Server sends `tts_end` when complete

## Desktop GUI Integration

### Config Option

```python
# config.py
ENABLE_DESKTOP_GUI = os.getenv("DARVIS_ENABLE_DESKTOP_GUI", "true").lower() == "true"
```

### Behavior

- `ENABLE_DESKTOP_GUI=true`: Desktop GUI runs as before
- `ENABLE_DESKTOP_GUI=false`: Skip Tkinter initialization
- Remote mode can run with or without desktop GUI

### Dual Instance (Optional)

If both local GUI and remote access needed:
- Run two separate processes
- Local: `DARVIS_MODE=local python -m darvis.ui`
- Remote: `DARVIS_MODE=remote python -m darvis.ui`
- Different ports recommended to avoid conflicts

## Configuration Summary

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `DARVIS_MODE` | local | Operating mode (local/remote) |
| `DARVIS_WEB_PASSWORD` | (none) | Password for remote access |
| `DARVIS_ENABLE_DESKTOP_GUI` | true | Enable desktop GUI |
| `DARVIS_WEB_PORT` | 5001 | Web server port |

## Security Considerations

1. **Password** - Stored as hashed using Werkzeug's `generate_password_hash` (PBKDF2+SHA256), never transmitted in plain text
2. **Session** - Flask signed cookies, expires after 24 hours
3. **Network** - No HTTPS by default (add reverse proxy for production)
4. **Rate limiting** - Not implemented (single user, low risk)

## File Changes

| File | Change |
|------|--------|
| `darvis/config.py` | Add remote mode config options |
| `web_chat.py` | Add auth, WebSocket voice events, remote binding |
| `web_templates/login.html` | New login page |
| `web_templates/index.html` | Add voice I/O, auth check |
| `static/js/voice.js` | New WebRTC audio handling |

## Testing Plan

1. Login flow: password correct/incorrect handling
2. Voice input: capture and stream to server
3. Voice output: receive and play from server
4. Full round-trip: voice→STT→AI→TTS→voice
5. Session persistence: refresh page, maintain auth
6. Remote access: connect from different machine
