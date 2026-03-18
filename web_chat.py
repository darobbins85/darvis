# /usr/bin/env python3
"""
Web-based Chat Interface for Darvis Voice Assistant.

This module provides the Flask-SocketIO server that serves the web-based
chat interface. It handles real-time communication between the browser
and Darvis backend services.

Routes:
    - GET /: Serves the main chat interface (index.html)

Socket Events:
    - connect: Handle client connection
    - disconnect: Handle client disconnection
    - chat_message: Process user messages (text input or voice commands)
    - toggle_listening: Handle microphone toggle
    - speech_recognized: Handle browser speech recognition results

Dependencies:
    - Flask: Web framework
    - flask-socketio: Real-time communication
    - darvis.ai: AI query processing
    - darvis.apps: Application launching
    - darvis.waybar_status: Status updates for waybar

Usage:
    python web_chat.py
    # Then open http://localhost:5001 in browser
"""

import sys
import os
from flask import Flask, render_template, redirect, url_for, flash, session, request
from flask_socketio import SocketIO, emit
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
import threading

# Add the parent directory to the path so we can import darvis modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import darvis modules
from darvis.ai import process_ai_query
from darvis.apps import open_app
from darvis.waybar_status import update_waybar_status
from darvis.config import DARVIS_MODE, WEB_APP_HOST, WEB_APP_PORT

# Validate remote mode password requirement
if DARVIS_MODE == "remote" and not os.getenv("DARVIS_WEB_PASSWORD"):
    raise ValueError("DARVIS_WEB_PASSWORD must be set when DARVIS_MODE=remote")


# =============================================================================
# Flask Application Setup
# =============================================================================

app = Flask(__name__, template_folder="web_templates")
app.config["SECRET_KEY"] = "darvis_secret_key"
app.config["PERMANENT_SESSION_LIFETIME"] = 3600 * 24  # 24 hours
socketio = SocketIO(app, cors_allowed_origins="*")

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.session_protection = "strong"


# Simple user class
class User(UserMixin):
    def __init__(self, id):
        self.id = id


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


# =============================================================================
# Global State
# =============================================================================

# Store hashed password at startup
_hashed_password = None


def get_hashed_password():
    """Get or create hashed password from env."""
    global _hashed_password
    if _hashed_password is None:
        raw_password = os.getenv("DARVIS_WEB_PASSWORD", "")
        if raw_password:
            _hashed_password = generate_password_hash(raw_password)
    return _hashed_password


listening_mode = False


@app.route("/")
@login_required
def index():
    """Serve the main chat interface."""
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle login page and authentication."""
    if request.method == "GET":
        return render_template("login.html")

    # POST - validate password
    password = request.form.get("password", "")
    hashed = get_hashed_password()

    if not hashed:
        flash("Server not configured for remote access")
        return render_template("login.html")

    if check_password_hash(hashed, password):
        login_user(User("remote_user"))
        return redirect(url_for("index"))

    flash("Invalid password")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@socketio.on("connect")
def handle_connect():
    """Handle client connection."""
    print("Client connected")


@socketio.on("disconnect")
def handle_disconnect():
    """Handle client disconnection."""
    print("Client disconnected")


@socketio.on("chat_message")
def handle_message(data):
    """Handle incoming messages from the web interface."""
    message = data.get("message", "").strip()
    if not message:
        return

    print(f"Received message: {message}")

    # Emit the user message to all clients
    emit("user_message", {"message": message}, broadcast=True)

    # Signal AI processing start (red eyes)
    emit("ai_processing", {}, broadcast=True)

    # Process the message (this will be done asynchronously)
    def process_message_async():
        try:
            # Check if it's a local app command
            command_lower = message.lower()
            if command_lower.startswith("open "):
                app_name = command_lower.split("open")[-1].strip()
                response = open_app(app_name)
                socketio.emit("ai_message", {"message": f"Opening: {response}"})
                return

            # Check for other local commands
            local_commands = ["calculator", "terminal", "editor", "browser"]
            if any(cmd in command_lower for cmd in local_commands):
                response = open_app(command_lower)
                if "not installed" in response or "not found" in response:
                    # Fall back to AI
                    update_waybar_status(
                        "thinking", f"Thinking about: {message[:30]}..."
                    )
                    response, session_id = process_ai_query(message)
                    update_waybar_status("success", "Response delivered")
                    socketio.emit("ai_message", {"message": response})
                else:
                    socketio.emit("ai_message", {"message": f"Result: {response}"})
                return

            # Default to AI processing
            update_waybar_status("thinking", f"Thinking about: {message[:30]}...")
            response, session_id = process_ai_query(message)
            update_waybar_status("success", "Response delivered")
            socketio.emit("ai_message", {"message": response})

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            socketio.emit("ai_message", {"message": error_msg})
            update_waybar_status("error", f"Error: {str(e)[:50]}")

    # Start processing in a background thread
    thread = threading.Thread(target=process_message_async, daemon=True)
    thread.start()


@socketio.on("toggle_listening")
def handle_toggle_listening(data):
    """Handle listening mode toggle from browser.

    The browser handles speech recognition directly using the Web Speech API.
    This just tracks the listening state on the server.
    """
    global listening_mode
    listening_mode = data.get("enabled", False)

    if listening_mode:
        print("🎤 Listening mode ENABLED - browser will handle speech recognition")
    else:
        print("🔇 Listening mode DISABLED")


@socketio.on("speech_recognized")
def handle_speech_recognized(data):
    """Handle speech recognized from browser."""
    text = data.get("text", "").strip()
    if not text:
        return

    print(f"🎤 Browser speech recognized: '{text}'")

    # Always send back to browser for client-side wake word detection
    emit("speech_recognized_response", {"text": text})


# =============================================================================
# Voice Processing WebSocket Handlers
# =============================================================================

voice_buffer = []


@socketio.on("voice_start")
def handle_voice_start():
    """Client started recording."""
    global voice_buffer
    voice_buffer = []
    print("Voice recording started")


@socketio.on("voice_data")
def handle_voice_data(data):
    """Receive audio chunk from client."""
    global voice_buffer
    audio_bytes = data.get("audio")
    if audio_bytes:
        voice_buffer.append(audio_bytes)


@socketio.on("voice_end")
def handle_voice_end():
    """Client stopped recording, process audio."""
    global voice_buffer
    print(f"Voice recording ended, {len(voice_buffer)} chunks")

    if not voice_buffer:
        return

    try:
        all_data = b"".join(voice_buffer)

        emit(
            "speech_recognized",
            {"text": "[Voice input received, STT integration pending]"},
        )
    except Exception as e:
        print(f"Error processing voice: {e}")

    voice_buffer = []


@socketio.on("request_tts")
def handle_tts_request(data):
    """Generate TTS for given text."""
    text = data.get("text", "")
    if not text:
        return

    emit("tts_start", {})
    emit("tts_end", {})


if __name__ == "__main__":
    print("Starting Darvis Web Chat Interface...")
    print(f"Open http://localhost:{WEB_APP_PORT} in your browser")
    print(f"Server binding: {WEB_APP_HOST}")
    print("")
    print("❌ Press Ctrl+C to stop")

    try:
        print(f"🌐 Starting Flask-SocketIO server on {WEB_APP_HOST}:{WEB_APP_PORT}...")
        socketio.run(
            app,
            host=WEB_APP_HOST,
            port=WEB_APP_PORT,
            debug=True,
            allow_unsafe_werkzeug=True,
        )
    except Exception as e:
        print(f"❌ Failed to start web server: {e}")
        import traceback

        traceback.print_exc()
