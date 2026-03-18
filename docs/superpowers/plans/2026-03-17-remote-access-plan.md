# Remote Access Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enable remote web access to Darvis with password auth and full voice I/O via browser

**Architecture:** Flask-SocketIO server with session-based auth, WebRTC audio streaming, Web Audio API playback

**Tech Stack:** Flask, Flask-SocketIO, Flask-Login, WebRTC, Web Audio API, Werkzeug password hashing

---

## Task 1: Add Config Options

**Files:**
- Modify: `darvis/config.py`

- [ ] **Step 1: Add remote mode config options**

Add to `darvis/config.py`:

```python
# Remote access configuration
DARVIS_MODE = os.getenv("DARVIS_MODE", "local")
DARVIS_WEB_PASSWORD = os.getenv("DARVIS_WEB_PASSWORD")
DARVIS_ENABLE_DESKTOP_GUI = os.getenv("DARVIS_ENABLE_DESKTOP_GUI", "true").lower() == "true"
DARVIS_WEB_PORT = int(os.getenv("DARVIS_WEB_PORT", "5001"))

# Auto-set host based on mode
if DARVIS_MODE == "remote":
    WEB_APP_HOST = "0.0.0.0"
else:
    WEB_APP_HOST = "127.0.0.1"
```

- [ ] **Step 2: Run config test**

Run: `python3 -c "from darvis.config import DARVIS_MODE, DARVIS_WEB_PASSWORD, DARVIS_ENABLE_DESKTOP_GUI, WEB_APP_HOST; print(f'Mode: {DARVIS_MODE}, Host: {WEB_APP_HOST}')"`
Expected: Output showing default values

- [ ] **Step 3: Commit**

```bash
git add darvis/config.py
git commit -m "feat: add remote access config options"
```

---

## Task 2: Add Flask-Login Auth

**Files:**
- Modify: `web_chat.py`

- [ ] **Step 1: Add auth imports and setup**

Add imports to `web_chat.py`:

```python
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
import os

# Validate remote mode password requirement
from darvis.config import DARVIS_MODE
if DARVIS_MODE == "remote" and not os.getenv('DARVIS_WEB_PASSWORD'):
    raise ValueError("DARVIS_WEB_PASSWORD must be set when DARVIS_MODE=remote")

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.session_protection = "strong"

# Session configuration (24 hour expiry)
app.config['PERMANENT_SESSION_LIFETIME'] = 3600 * 24  # 24 hours

# Simple user class
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)
```

- [ ] **Step 2: Add login route**

Add to `web_chat.py` after the `@app.route('/')` section:

```python
# Store hashed password at startup
_hashed_password = None

def get_hashed_password():
    """Get or create hashed password from env."""
    global _hashed_password
    if _hashed_password is None:
        raw_password = os.getenv('DARVIS_WEB_PASSWORD', '')
        if raw_password:
            _hashed_password = generate_password_hash(raw_password)
    return _hashed_password

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle login page and authentication."""
    from flask import request, render_template, redirect, url_for, flash
    
    if request.method == 'GET':
        return render_template('login.html')
    
    # POST - validate password
    password = request.form.get('password', '')
    hashed = get_hashed_password()
    
    if not hashed:
        flash('Server not configured for remote access')
        return render_template('login.html')
    
    if check_password_hash(hashed, password):
        login_user(User('remote_user'))
        return redirect(url_for('index'))
    
    flash('Invalid password')
    return render_template('login.html')
```

- [ ] **Step 3: Add auth check decorator to index route**

Modify `@app.route('/')`:

```python
@app.route('/')
@login_required
def index():
    return render_template('index.html')
```

- [ ] **Step 4: Run test**

Run: `DARVIS_WEB_PASSWORD=test python3 -c "from web_chat import app; print('Auth imports OK')"`
Expected: No errors

- [ ] **Step 5: Commit**

```bash
git add web_chat.py
git commit -m "feat: add Flask-Login authentication"
```

---

## Task 3: Create Login Template

**Files:**
- Create: `web_templates/login.html`

- [ ] **Step 1: Create login page**

Create `web_templates/login.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Darvis - Login</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0;
        }
        .login-container {
            background: rgba(255, 255, 255, 0.1);
            padding: 2rem;
            border-radius: 12px;
            backdrop-filter: blur(10px);
            width: 100%;
            max-width: 400px;
        }
        h1 {
            color: #fff;
            text-align: center;
            margin-bottom: 2rem;
        }
        .logo {
            display: block;
            margin: 0 auto 1rem;
            width: 100px;
            height: 100px;
        }
        input[type="password"] {
            width: 100%;
            padding: 12px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.1);
            color: #fff;
            font-size: 16px;
            box-sizing: border-box;
        }
        input[type="password"]:focus {
            outline: none;
            border-color: #00ff88;
        }
        button {
            width: 100%;
            padding: 12px;
            background: #00ff88;
            border: none;
            border-radius: 8px;
            color: #1a1a2e;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 1rem;
        }
        button:hover {
            background: #00cc6a;
        }
        .error {
            color: #ff6b6b;
            text-align: center;
            margin-top: 1rem;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <img src="/static/darvis-logo.png" alt="Darvis" class="logo">
        <h1>Darvis</h1>
        <form method="POST">
            <input type="password" name="password" placeholder="Enter password" required autofocus>
            <button type="submit">Login</button>
        </form>
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                <div class="error">{{ messages[0] }}</div>
            {% endif %}
        {% endwith %}
    </div>
</body>
</html>
```

- [ ] **Step 2: Commit**

```bash
git add web_templates/login.html
git commit -m "feat: add login page template"
```

---

## Task 4: Voice Processing - Server Side

**Files:**
- Modify: `web_chat.py`

- [ ] **Step 1: Add voice WebSocket handlers**

Add to `web_chat.py`:

```python
import base64
import io
import wave
import numpy as np

# Voice buffer for accumulating audio chunks
voice_buffer = []

@socketio.on('voice_start')
def handle_voice_start():
    """Client started recording."""
    global voice_buffer
    voice_buffer = []
    print("Voice recording started")

@socketio.on('voice_data')
def handle_voice_data(data):
    """Receive audio chunk from client."""
    global voice_buffer
    # Data is Int16Array, convert to bytes
    audio_bytes = data.get('audio')
    if audio_bytes:
        voice_buffer.append(audio_bytes)

@socketio.on('voice_end')
def handle_voice_end():
    """Client stopped recording, process audio."""
    global voice_buffer
    print(f"Voice recording ended, {len(voice_buffer)} chunks")
    
    if not voice_buffer:
        return
    
    # Process the audio (convert to format expected by speech recognition)
    try:
        # Combine all chunks
        all_data = b''.join(voice_buffer)
        
        # NOTE: STT integration with darvis.speech module is a follow-up task
        # For now, emit placeholder to test voice pipeline
        emit('speech_recognized', {'text': '[Voice input received, STT integration pending]'})
    except Exception as e:
        print(f"Error processing voice: {e}")
    
    voice_buffer = []

@socketio.on('request_tts')
def handle_tts_request(data):
    """Generate TTS for given text."""
    text = data.get('text', '')
    if not text:
        return
    
    # Emit TTS start
    emit('tts_start', {})
    
    # NOTE: TTS integration with darvis.speech module is a follow-up task
    # For now, emit placeholder to test voice pipeline
    # When implementing: wrap PCM in WAV container (44100 Hz, 16-bit, mono)
    emit('tts_end', {})
```

- [ ] **Step 2: Commit**

```bash
git add web_chat.py
git commit -m "feat: add voice WebSocket handlers"
```

---

## Task 5: Voice Processing - Client Side

**Files:**
- Create: `static/js/voice-processor.js`
- Modify: `static/js/chat.js` (create if needed)

- [ ] **Step 1: Create AudioWorklet processor**

Create `static/js/voice-processor.js`:

```javascript
class VoiceProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
        this.port.onmessage = (event) => {
            // Handle messages from main thread if needed
        };
    }

    process(inputs, outputs, parameters) {
        const input = inputs[0];
        if (input && input.length > 0) {
            const channelData = input[0];
            // Convert Float32 to Int16 PCM
            const pcmData = new Int16Array(channelData.length);
            for (let i = 0; i < channelData.length; i++) {
                const sample = Math.max(-1, Math.min(1, channelData[i]));
                pcmData[i] = Math.round(sample * 32767);
            }
            this.port.postMessage(pcmData);
        }
        return true;
    }
}
registerProcessor('voice-processor', VoiceProcessor);
```

- [ ] **Step 2: Create voice client module**

Create `static/js/voice.js`:

```javascript
class VoiceClient {
    constructor(socket) {
        this.socket = socket;
        this.audioContext = null;
        this.mediaStream = null;
        this.processor = null;
        this.isRecording = false;
        
        // Silence detection
        this.silenceThreshold = 0.01;
        this.silenceDuration = 1.5; // seconds
        this.silentChunks = 0;
        this.chunkDuration = 0.125; // 4096 samples / 32768 Hz ≈ 0.125s
        
        // TTS playback
        this.ttsAudioContext = null;
        this.audioQueue = [];
        this.isPlaying = false;
        
        // Status callbacks
        this.onStatusChange = null;
    }

    setStatusCallback(callback) {
        this.onStatusChange = callback;
    }

    updateStatus(status) {
        if (this.onStatusChange) {
            this.onStatusChange(status);
        }
    }

    // Analyze audio for silence detection
    analyzeAudioLevel(int16Data) {
        let sum = 0;
        for (let i = 0; i < int16Data.length; i++) {
            sum += Math.abs(int16Data[i]) / 32767;
        }
        return sum / int16Data.length;
    }

    async startRecording() {
        try {
            this.mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.audioContext = new AudioContext();
            const source = this.audioContext.createMediaStreamSource(this.mediaStream);
            
            // Load AudioWorklet
            await this.audioContext.audioWorklet.addModule('/static/js/voice-processor.js');
            
            this.processor = new AudioWorkletNode(this.audioContext, 'voice-processor');
            
            // Reset silence detection
            this.silentChunks = 0;
            
            // Send audio data to server with silence detection
            this.processor.port.onmessage = (event) => {
                if (this.isRecording) {
                    const audioLevel = this.analyzeAudioLevel(event.data);
                    
                    if (audioLevel < this.silenceThreshold) {
                        this.silentChunks++;
                        const silentTime = this.silentChunks * this.chunkDuration;
                        if (silentTime >= this.silenceDuration) {
                            // Stop after 1.5s of silence
                            this.stopRecording();
                            return;
                        }
                    } else {
                        this.silentChunks = 0;
                    }
                    
                    this.socket.emit('voice_data', { audio: event.data });
                }
            };
            
            source.connect(this.processor);
            this.processor.connect(this.audioContext.destination);
            
            this.isRecording = true;
            this.socket.emit('voice_start');
            this.updateStatus('listening');
            
        } catch (error) {
            console.error('Failed to start recording:', error);
        }
    }

    stopRecording() {
        if (this.isRecording) {
            this.isRecording = false;
            this.socket.emit('voice_end');
            
            if (this.mediaStream) {
                this.mediaStream.getTracks().forEach(track => track.stop());
            }
            if (this.audioContext) {
                this.audioContext.close();
            }
            
            this.updateStatus('processing');
        }
    }

    // TTS Playback
    initTTS() {
        this.ttsAudioContext = new AudioContext();
        
        this.socket.on('tts_start', () => {
            this.updateStatus('speaking');
        });
        
        this.socket.on('tts_audio', (data) => {
            this.playTTSChunk(data.audio);
        });
        
        this.socket.on('tts_end', () => {
            this.updateStatus('idle');
        });
    }

    playTTSChunk(base64Audio) {
        if (!this.ttsAudioContext) {
            this.initTTS();
        }
        
        // Decode base64
        const binaryString = atob(base64Audio);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }
        
        this.ttsAudioContext.decodeAudioData(bytes.buffer, (buffer) => {
            this.audioQueue.push(buffer);
            this.playNext();
        });
    }

    playNext() {
        if (this.isPlaying || this.audioQueue.length === 0) return;
        
        this.isPlaying = true;
        const buffer = this.audioQueue.shift();
        const source = this.ttsAudioContext.createBufferSource();
        source.buffer = buffer;
        source.connect(this.ttsAudioContext.destination);
        source.onended = () => {
            this.isPlaying = false;
            this.playNext();
        };
        source.start();
    }

    speak(text) {
        this.socket.emit('request_tts', { text: text });
    }
}

// Export for use in main app
window.VoiceClient = VoiceClient;
```

- [ ] **Step 3: Commit**

```bash
git add static/js/voice-processor.js static/js/voice.js
git commit -m "feat: add client-side voice processing"
```

---

## Task 6: Update Index Template

**Files:**
- Modify: `web_templates/index.html`

- [ ] **Step 1: Add voice controls and auth check**

Add before closing `</body>` tag in `web_templates/index.html`:

```html
<script src="/socket.io/socket.io.js"></script>
<script src="/static/js/voice.js"></script>
<script>
    // Initialize socket and voice client
    const socket = io();
    let voiceClient = null;
    
    // Check auth and init voice
    fetch('/')
        .then(response => {
            if (response.status === 401) {
                window.location.href = '/login';
                return null;
            }
            return response.text();
        })
        .then(html => {
            if (html) {
                initVoice();
            }
        });
    
    function initVoice() {
        voiceClient = new VoiceClient(socket);
        
        voiceClient.setStatusCallback((status) => {
            const micBtn = document.getElementById('mic-btn');
            const statusText = document.getElementById('voice-status');
            if (micBtn && statusText) {
                if (status === 'listening') {
                    micBtn.classList.add('recording');
                    statusText.textContent = 'Listening...';
                } else if (status === 'processing') {
                    micBtn.classList.remove('recording');
                    statusText.textContent = 'Processing...';
                } else if (status === 'speaking') {
                    statusText.textContent = 'Speaking...';
                } else {
                    micBtn.classList.remove('recording');
                    statusText.textContent = '';
                }
            }
        });
        
        voiceClient.initTTS();
    }
    
    function toggleMic() {
        if (!voiceClient) return;
        
        if (voiceClient.isRecording) {
            voiceClient.stopRecording();
        } else {
            voiceClient.startRecording();
        }
    }
</script>
```

- [ ] **Step 2: Add voice button to UI**

Add voice button near the chat input area in `web_templates/index.html`. Look for the input field or send button, and add the mic button beside it:

```html
<div class="chat-input-container">
    <input type="text" id="user-input" placeholder="Type a message...">
    <button id="mic-btn" onclick="toggleMic()" title="Click to talk">🎤</button>
    <button onclick="sendMessage()">Send</button>
</div>
<span id="voice-status"></span>
```

Also add this CSS for the recording state:

```css
#mic-btn.recording {
    background: #ff4444;
    animation: pulse 1s infinite;
}
```

- [ ] **Step 3: Commit**

```bash
git add web_templates/index.html
git commit -m "feat: add voice controls to web UI"
```

---

## Task 7: Update Server Binding

**Files:**
- Modify: `web_chat.py`

- [ ] **Step 1: Use config for host binding**

Modify the `if __name__ == '__main__'` section:

```python
if __name__ == '__main__':
    from darvis.config import WEB_APP_HOST, WEB_APP_PORT
    
    print("Starting Darvis Web Chat Interface...")
    print(f"Open http://localhost:{WEB_APP_PORT} in your browser")
    print(f"Server binding: {WEB_APP_HOST}")
    
    try:
        socketio.run(app, host=WEB_APP_HOST, port=WEB_APP_PORT, debug=True, allow_unsafe_werkzeug=True)
    except Exception as e:
        print(f"❌ Failed to start web server: {e}")
        import traceback
        traceback.print_exc()
```

- [ ] **Step 2: Test binding**

Run: `DARVIS_MODE=remote python3 web_chat.py` (should show binding to 0.0.0.0)

- [ ] **Step 3: Commit**

```bash
git add web_chat.py
git commit -m "feat: use config for server binding"
```

---

## Task 8: Integration Test

**Files:**
- Test manually

- [ ] **Step 1: Test local mode**

Run: `python3 web_chat.py`
- Open http://localhost:5001 - should redirect to login (but local mode may not require auth yet)

- [ ] **Step 2: Test remote mode with password**

Run: `DARVIS_WEB_PASSWORD=secret DARVIS_MODE=remote python3 web_chat.py`
- Open http://localhost:5001 - should show login page
- Enter wrong password - should show error
- Enter "secret" - should redirect to chat

- [ ] **Step 3: Test voice (manual)**

- Click microphone button
- Speak
- Should see "Listening..." status

- [ ] **Step 4: Commit**

```bash
git commit --allow-empty -m "test: manual integration testing complete"
```

---

## Summary

This plan implements the core remote access functionality:

1. Config options for mode, password, port (used by web_chat.py)
2. Flask-Login authentication with password validation
3. Login page template
4. Server-side voice WebSocket handlers
5. Client-side AudioWorklet with silence detection and voice.js
6. Updated index.html with voice controls
7. Configurable server binding

Note: `DARVIS_ENABLE_DESKTOP_GUI` config is used in `darvis/ui.py` to conditionally enable the Tkinter GUI. The web server can run with or without the desktop GUI.

Follow-up tasks (not in this plan):
- STT integration: Connect voice_end handler to darvis.speech module
- TTS integration: Connect request_tts handler to darvis.speech TTS, wrap output in WAV format
- HTTPS via reverse proxy (nginx)
