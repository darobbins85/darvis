#/usr/bin/env python3
"""
Web-based Chat Interface for Darvis Voice Assistant
Provides perfect chat bubbles with real-time communication
"""

import os
import sys
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import threading
import queue

# Add the parent directory to the path so we can import darvis modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import existing darvis functionality
from darvis.ai import process_ai_query
from darvis.speech import listen
from darvis.apps import open_app
from darvis.waybar_status import update_waybar_status

# Global variables for communication between threads
message_queue = queue.Queue()
response_queue = queue.Queue()

app = Flask(__name__,
            template_folder='web_templates')
app.config['SECRET_KEY'] = 'darvis_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
listening_mode = False
current_ai_thread = None

@app.route('/')
def index():
    """Serve the main chat interface."""
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print("Client connected")
    emit('status', {'message': 'Connected to Darvis', 'type': 'success'})

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
    """Handle listening mode toggle."""
    global listening_mode
    listening_mode = data.get('enabled', False)

    if listening_mode:
        print("🎤 Listening mode ENABLED - browser will handle speech recognition")
        emit('status', {'message': 'Listening mode enabled - say "hey darvis"', 'type': 'info'})
    else:
        print("🔇 Listening mode DISABLED")
        emit('status', {'message': 'Listening mode disabled', 'type': 'info'})

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
    print("Open http://localhost:5000 in your browser")
    print("📱 Open your browser to http://localhost:5000")
    print("🎤 Use the listening toggle for voice commands")
    print("❌ Press Ctrl+C to stop")
    print("")

    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)