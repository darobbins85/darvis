#/usr/bin/env python3
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
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading

# Add the parent directory to the path so we can import darvis modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import darvis modules
from darvis.ai import process_ai_query
from darvis.apps import open_app
from darvis.waybar_status import update_waybar_status


# =============================================================================
# Flask Application Setup
# =============================================================================

app = Flask(__name__, template_folder='web_templates')
app.config['SECRET_KEY'] = 'darvis_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")


# =============================================================================
# Global State
# =============================================================================

# Track if voice listening mode is active
listening_mode = False

@app.route('/')
def index():
    """Serve the main chat interface."""
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print("Client connected")


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print("Client disconnected")

@socketio.on('chat_message')
def handle_message(data):
    """Handle incoming messages from the web interface."""
    message = data.get('message', '').strip()
    if not message:
        return

    print(f"Received message: {message}")

    # Emit the user message to all clients
    emit('user_message', {'message': message}, broadcast=True)

    # Signal AI processing start (red eyes)
    emit('ai_processing', {}, broadcast=True)

    # Process the message (this will be done asynchronously)
    def process_message_async():
        try:
            # Check if it's a local app command
            command_lower = message.lower()
            if command_lower.startswith("open "):
                app_name = command_lower.split("open")[-1].strip()
                response = open_app(app_name)
                socketio.emit('ai_message', {'message': f"Opening: {response}"})
                return

            # Check for other local commands
            local_commands = ["calculator", "terminal", "editor", "browser"]
            if any(cmd in command_lower for cmd in local_commands):
                response = open_app(command_lower)
                if "not installed" in response or "not found" in response:
                    # Fall back to AI
                    update_waybar_status("thinking", f"Thinking about: {message[:30]}...")
                    response, session_id = process_ai_query(message)
                    update_waybar_status("success", "Response delivered")
                    socketio.emit('ai_message', {'message': response})
                else:
                    socketio.emit('ai_message', {'message': f"Result: {response}"})
                return

            # Default to AI processing
            update_waybar_status("thinking", f"Thinking about: {message[:30]}...")
            response, session_id = process_ai_query(message)
            update_waybar_status("success", "Response delivered")
            socketio.emit('ai_message', {'message': response})

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            socketio.emit('ai_message', {'message': error_msg})
            update_waybar_status("error", f"Error: {str(e)[:50]}")

    # Start processing in a background thread
    thread = threading.Thread(target=process_message_async, daemon=True)
    thread.start()

@socketio.on('toggle_listening')
def handle_toggle_listening(data):
    """Handle listening mode toggle from browser.
    
    The browser handles speech recognition directly using the Web Speech API.
    This just tracks the listening state on the server.
    """
    global listening_mode
    listening_mode = data.get('enabled', False)

    if listening_mode:
        print("🎤 Listening mode ENABLED - browser will handle speech recognition")
    else:
        print("🔇 Listening mode DISABLED")

@socketio.on('speech_recognized')
def handle_speech_recognized(data):
    """Handle speech recognized from browser."""
    text = data.get('text', '').strip()
    if not text:
        return

    print(f"🎤 Browser speech recognized: '{text}'")

    # Always send back to browser for client-side wake word detection
    emit('speech_recognized_response', {'text': text})

if __name__ == '__main__':
    print("Starting Darvis Web Chat Interface...")
    print("Open http://localhost:5001 in your browser")
    print("📱 Open your browser to http://localhost:5001")
    print("🎤 Use the listening toggle for voice commands")
    print("❌ Press Ctrl+C to stop")
    print("")

    try:
        print("🌐 Starting Flask-SocketIO server on 127.0.0.1:5001...")
        socketio.run(app, host='127.0.0.1', port=5001, debug=True, allow_unsafe_werkzeug=True)
    except Exception as e:
        print(f"❌ Failed to start web server: {e}")
        import traceback
        traceback.print_exc()