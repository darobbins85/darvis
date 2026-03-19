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
from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    flash,
    session,
    request,
    jsonify,
)
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
from darvis.database import (
    init_db,
    create_user,
    get_user_by_username,
    get_user_by_id,
    get_or_create_default_session,
    get_user_sessions,
    create_session,
    get_session_by_id,
    update_session_name,
    delete_session,
    get_next_session_number,
    add_message,
    get_session_messages,
)

# Initialize database on startup
init_db()

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
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username


@login_manager.user_loader
def load_user(user_id):
    user = get_user_by_id(user_id)
    if user:
        return User(user["id"], user["username"])
    return None


# =============================================================================
# Global State
# =============================================================================

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

    # POST - validate username and password
    username = request.form.get("username", "")
    password = request.form.get("password", "")

    if not username or not password:
        flash("Username and password required")
        return render_template("login.html")

    user = get_user_by_username(username)

    if user and check_password_hash(user["password_hash"], password):
        login_user(User(user["id"], user["username"]))

        # Create default session if none exists
        get_or_create_default_session(user["id"])

        # Redirect to main chat
        next_page = request.args.get("next")
        return redirect(next_page or url_for("index"))

    flash("Invalid username or password")
    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Handle user registration."""
    if request.method == "GET":
        return render_template("signup.html")

    username = request.form.get("username", "")
    password = request.form.get("password", "")
    confirm = request.form.get("confirm", "")

    if not username or not password:
        flash("Username and password required")
        return render_template("signup.html")

    if password != confirm:
        flash("Passwords do not match")
        return render_template("signup.html")

    if len(password) < 6:
        flash("Password must be at least 6 characters")
        return render_template("signup.html")

    # Check if username exists
    if get_user_by_username(username):
        flash("Username already taken")
        return render_template("signup.html")

    # Create user
    password_hash = generate_password_hash(password)
    user_id = create_user(username, password_hash)

    # Auto-login after signup
    login_user(User(user_id, username))

    # Create default session
    get_or_create_default_session(user_id)

    return redirect(url_for("index"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# =============================================================================
# API Endpoints
# =============================================================================


@app.route("/api/user")
@login_required
def get_current_user():
    """Get current user info."""
    return jsonify(
        {
            "id": current_user.id,
            "username": current_user.username,
        }
    )


@app.route("/api/sessions")
@login_required
def get_sessions():
    """Get all sessions for current user."""
    sessions = get_user_sessions(current_user.id)
    return jsonify(
        [
            {
                "id": s["id"],
                "name": s["name"],
                "session_number": s["session_number"],
                "created_at": s["created_at"],
                "updated_at": s["updated_at"],
            }
            for s in sessions
        ]
    )


@app.route("/api/sessions", methods=["POST"])
@login_required
def create_session_api():
    """Create a new session for current user."""
    session_num = get_next_session_number(current_user.id)
    name = f"Session {session_num}"
    session_id = create_session(current_user.id, name, session_num)
    session = get_session_by_id(session_id)
    return jsonify(
        {
            "id": session["id"],
            "name": session["name"],
            "session_number": session["session_number"],
        }
    )


@app.route("/api/sessions/<int:session_id>", methods=["PUT"])
@login_required
def update_session_api(session_id):
    """Update a session (rename)."""
    session = get_session_by_id(session_id)
    if session and session["user_id"] == current_user.id:
        data = request.get_json()
        update_session_name(session_id, data.get("name", session["name"]))
        return jsonify({"success": True})
    return jsonify({"error": "Not found"}), 404


@app.route("/api/sessions/<int:session_id>", methods=["DELETE"])
@login_required
def delete_session_api(session_id):
    """Delete a session."""
    session = get_session_by_id(session_id)
    if session and session["user_id"] == current_user.id:
        delete_session(session_id)
        return jsonify({"success": True})
    return jsonify({"error": "Not found"}), 404


@app.route("/api/sessions/<int:session_id>/messages")
@login_required
def get_session_messages_api(session_id):
    """Get all messages for a session."""
    session = get_session_by_id(session_id)
    if session and session["user_id"] == current_user.id:
        messages = get_session_messages(session_id)
        return jsonify(
            [
                {
                    "id": m["id"],
                    "role": m["role"],
                    "content": m["content"],
                    "created_at": m["created_at"],
                }
                for m in messages
            ]
        )
    return jsonify({"error": "Not found"}), 404


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
