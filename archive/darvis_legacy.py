import os
#!/usr/bin/env python3
"""
Darvis Voice Assistant

A modern, interactive voice assistant with both voice and manual text input capabilities.
Features a sleek dark-themed GUI with real-time visual feedback and intelligent command processing.

Main Components:
- Voice Recognition: Google Speech API with wake word detection
- Manual Input: Always-available text input with Enter key submission
- AI Mode: Optional AI-powered responses via opencode CLI
- Smart Commands: Web services, system applications, and custom commands
- Visual Feedback: Dynamic glow effects for user interactions

Author: Darvis Development Team
Version: 1.0.0
"""

import os
import queue
import subprocess
import sys
import threading
import tkinter as tk
from typing import Optional, List

import pyaudio
import pyttsx3
import speech_recognition as sr

# Suppress ALSA warnings for cleaner output
os.environ["ALSA_LOG_LEVEL"] = "0"

conversation_history = []
current_session_id = None

def speak(text: str) -> None:
    """
    Convert text to speech using pyttsx3 TTS engine.

    Args:
        text: The text to speak aloud

    Note:
        Silently ignores TTS errors to prevent application interruption.
        Text feedback is still provided through the GUI.
    """
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        # Silently ignore TTS errors - text feedback is still shown
        pass


def list_microphones():
    p = pyaudio.PyAudio()
    print("Available microphones:")
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info["maxInputChannels"] > 0:
            print(f"Index {i}: {info['name']}")
    p.terminate()


def listen(device_index: Optional[int] = None) -> str:
    """
    Capture and transcribe voice input using Google Speech Recognition.

    Args:
        device_index: Specific microphone device index to use.
                     If None, uses system default.

    Returns:
        Lowercase transcribed text from speech, or empty string on errors.

    Raises:
        No exceptions - gracefully handles all audio/speech errors.

    Note:
        Manual input is handled separately through the GUI input field.
        This function focuses solely on voice-to-text conversion.
    """
    # Manual input is always available through the GUI input field
    # This function now only handles voice recognition
    r = sr.Recognizer()
    r.energy_threshold = 400
    try:
        with sr.Microphone(device_index=device_index) as source:
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
        try:
            return r.recognize_google(audio).lower()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            print(f"API error: {e}")
            return ""
    except OSError as e:
        print(f"Microphone error: {e}")
        return ""
    except sr.WaitTimeoutError:
        return ""


def get_latest_session_id():
    try:
        result = subprocess.run(["opencode", "session", "list"], capture_output=True, text=True, timeout=10)
        lines = result.stdout.strip().split('\n')
        if len(lines) > 2:  # Skip header and separator
            # Latest session is the first data line (lines[2])
            data_line = lines[2].strip()
            if data_line:
                # Session ID is the first field
                session_id = data_line.split()[0]
                return session_id
        return None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None

def find_app_command(app_name: str) -> str:
    """
    Find the correct command to launch an application.

    Checks .desktop files, PATH, and common command variations.

    Args:
        app_name: Name of the application to find

    Returns:
        Command string to execute, or empty string if not found
    """
    import os
    import glob

    app_name_lower = app_name.lower()

    # Extended app mapping with common variations
    app_map = {
        "chrome": ["chromium", "google-chrome", "chrome"],
        "browser": ["firefox", "chromium", "chrome"],
        "firefox": ["firefox"],
        "chromium": ["chromium"],
        "terminal": ["xterm", "gnome-terminal", "konsole", "terminator"],
        "editor": ["gedit", "kate", "mousepad", "leafpad", "nano", "vim"],
        "gedit": ["gedit"],
        "calculator": ["galculator", "gnome-calculator", "kcalc", "speedcrunch"],
        "galculator": ["galculator"],
        "steam": ["steam"],
        "signal": ["signal-desktop", "signal"],
        "discord": ["discord"],
        "slack": ["slack"],
        "spotify": ["spotify"],
        "vlc": ["vlc"],
        "code": ["code", "vscode"],
        "sublime": ["subl", "sublime-text"],
        "atom": ["atom"],
        "thunderbird": ["thunderbird"],
        "libreoffice": ["libreoffice", "lowriter"],
        "gimp": ["gimp"],
        "inkscape": ["inkscape"],
        "blender": ["blender"],
        "krita": ["krita"],
    }

    # Check if we have a direct mapping
    if app_name_lower in app_map:
        for cmd in app_map[app_name_lower]:
            if is_command_available(cmd):
                return cmd

    # Check .desktop files in standard locations
    desktop_dirs = [
        "/usr/share/applications/",
        "/usr/local/share/applications/",
        os.path.expanduser("~/.local/share/applications/"),
        "/var/lib/snapd/desktop/applications/"
    ]

    for desktop_dir in desktop_dirs:
        if os.path.exists(desktop_dir):
            # Look for .desktop files that match the app name
            for desktop_file in glob.glob(os.path.join(desktop_dir, f"*{app_name_lower}*.desktop")):
                try:
                    exec_cmd = parse_desktop_file(desktop_file)
                    if exec_cmd and is_command_available(exec_cmd.split()[0]):
                        return exec_cmd
                except:
                    continue

            # Also check for exact matches
            exact_desktop = os.path.join(desktop_dir, f"{app_name_lower}.desktop")
            if os.path.exists(exact_desktop):
                try:
                    exec_cmd = parse_desktop_file(exact_desktop)
                    if exec_cmd and is_command_available(exec_cmd.split()[0]):
                        return exec_cmd
                except:
                    continue

    # Check if the app name itself is a valid command
    if is_command_available(app_name_lower):
        return app_name_lower

    # Try some common variations
    variations = [
        app_name_lower,
        f"{app_name_lower}-desktop",
        f"{app_name_lower}.bin",
        f"{app_name_lower}.sh"
    ]

    for variation in variations:
        if is_command_available(variation):
            return variation

    return ""  # Not found

def is_command_available(cmd: str) -> bool:
    """Check if a command is available in PATH."""
    try:
        subprocess.run([cmd], capture_output=True, check=False)
        return True
    except FileNotFoundError:
        return False

def parse_desktop_file(desktop_file: str) -> str:
    """Parse a .desktop file to extract the Exec command."""
    try:
        with open(desktop_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Look for the Exec line
        for line in content.split('\n'):
            if line.startswith('Exec='):
                exec_cmd = line.split('=', 1)[1].strip()
                # Remove field codes like %f, %F, %u, %U, etc.
                exec_cmd = exec_cmd.split()[0]  # Take just the command, not args
                return exec_cmd
    except:
        pass
    return ""

def open_app(app_name: str) -> str:
    """
    Launch applications or open web services based on user commands.

    Supports both local system applications and web services. Uses intelligent
    app detection to find installed applications and their correct launch commands.

    Args:
        app_name: Name of application or web service to launch

    Returns:
        Success message or error description

    Supported Web Services:
        - youtube, google, gmail, github, netflix, spotify

    App Detection:
        - Checks .desktop files in standard locations
        - Searches PATH for executable commands
        - Supports common application name variations
    """
    app_name_lower = app_name.lower()

    # Handle web services that should open in browser
    web_services = {
        "youtube": "https://youtube.com",
        "google": "https://google.com",
        "gmail": "https://gmail.com",
        "github": "https://github.com",
        "netflix": "https://netflix.com",
        "spotify": "https://spotify.com"
    }

    if app_name_lower in web_services:
        # Use xdg-open for cross-desktop compatibility
        try:
            subprocess.Popen(["xdg-open", web_services[app_name_lower]])
            return f"Opening {app_name}"
        except FileNotFoundError:
            # Fallback to trying browsers directly
            browsers = ["chromium", "firefox"]
            for browser in browsers:
                try:
                    subprocess.Popen([browser, web_services[app_name_lower]])
                    return f"Opening {app_name} in {browser}"
                except FileNotFoundError:
                    continue
            return f"Couldn't find a way to open {app_name}"
        except Exception as e:
            return f"Error opening {app_name}: {str(e)}"
    else:
        # Try to find the app command
        app_command = find_app_command(app_name)

        if app_command:
            try:
                subprocess.Popen([app_command])
                return f"Opening {app_name}"
            except Exception as e:
                return f"Error launching {app_name}: {str(e)}"
        else:
            return f"'{app_name}' is not installed or not found on this system"


def toggle_ai() -> None:
    """
    Toggle between local command processing and AI-powered responses.

    Switches the assistant between two modes:
    - AI Mode OFF: Commands processed locally (apps, web services)
    - AI Mode ON: Commands sent to AI system for intelligent responses

    Visual Feedback:
        - Button text: "AI Mode: ON/OFF"
        - Button color: Green (ON) / Red (OFF)
    """
    global ai_mode, ai_button
    ai_mode.set(not ai_mode.get())
    ai_button.config(text="AI Mode: ON" if ai_mode.get() else "AI Mode: OFF",
                     bg="green" if ai_mode.get() else "red",
                     fg="white",
                     width=15,
                     relief="raised")



def manual_activate() -> None:
    """
    Manually trigger voice assistant activation sequence.

    Simulates the wake word detection process without requiring voice input.
    Activates the assistant and begins listening for commands.

    Process:
        1. Show activation status
        2. Listen for voice command (or accept manual input)
        3. Process command based on AI mode setting
        4. Return to listening state

    Note: Typically triggered by voice wake words, but can be called manually
          for testing or when voice detection fails.
    """
    global msg_queue, ai_mode, current_session_id
    msg_queue.put(
        {"type": "status", "text": "Status: Activated", "color": "green"}
    )
    msg_queue.put({"type": "insert", "text": "Activated!\n"})
    speak("Activated!")

    # Intelligent voice command processing
    command = listen()
    if command:
        command_lower = command.lower()

        # Check if it's a local command first
        if command_lower.startswith("open "):
            # Handle open commands locally
            app = command_lower.split("open")[-1].strip()
            response = open_app(app)
            msg_queue.put({"type": "insert", "text": f"Command: {command}\n{response}\n"})
            speak(response)
        else:
            # Check if it looks like a command we can handle locally
            local_commands = ["calculator", "terminal", "editor", "browser"]
            if any(cmd in command_lower for cmd in local_commands):
                # Try to handle as local command
                app = command_lower  # Pass the full input to open_app
                response = open_app(app)
                if "Sorry, I don't know how to open" in response:
                    # Fall back to AI
                    msg_queue.put({"type": "insert", "text": f"Local command failed, using AI assistance...\nAI Query: {command}\n"})
                    glow_logo(True, True)  # Red glow for AI
                    try:
                        global current_session_id
                        if current_session_id is None:
                            # First query: start new session
                            result = subprocess.run(["opencode", "run", command], capture_output=True, text=True, timeout=60)
                            response = (result.stdout or "").strip() or "No response"
                            # Get the session ID
                            current_session_id = get_latest_session_id()
                            if current_session_id:
                                msg_queue.put({'type': 'insert', 'text': "New AI session started (ID: " + current_session_id + ")" + chr(10)})
                            else:
                                msg_queue.put({'type': 'insert', 'text': "Warning: Could not retrieve session ID" + chr(10)})
                        else:
                            # Subsequent queries: use existing session
                            result = subprocess.run(["opencode", "run", "--session", current_session_id, command], capture_output=True, text=True, timeout=60)
                            response = (result.stdout or "").strip() or "No response"
                        msg_queue.put({"type": "insert", "text": "AI Response: " + response + "\n"})
                        speak("Response received")
                    except subprocess.TimeoutExpired:
                        msg_queue.put({"type": "insert", "text": "AI query timed out\n"})
                    except FileNotFoundError:
                        msg_queue.put({"type": "insert", "text": "AI assistance not available\n"})
                    finally:
                        root.after(1000, lambda: glow_logo(False, False))  # Stop red glow
                else:
                    msg_queue.put({"type": "insert", "text": f"Command: {command}\n{response}\n"})
                    speak(response)
            else:
                # Default to AI for unrecognized voice inputs
                msg_queue.put({"type": "insert", "text": f"Using AI assistance...\nAI Query: {command}\n"})
                glow_logo(True, True)  # Red glow for AI
                try:
                    if current_session_id is None:
                        # First query: start new session
                        result = subprocess.run(["opencode", "run", command], capture_output=True, text=True, timeout=60)
                        response = (result.stdout or "").strip() or "No response"
                        # Get the session ID
                        current_session_id = get_latest_session_id()
                        if current_session_id:
                            msg_queue.put({'type': 'insert', 'text': "New AI session started (ID: " + current_session_id + ")" + chr(10)})
                        else:
                            msg_queue.put({'type': 'insert', 'text': "Warning: Could not retrieve session ID" + chr(10)})
                    else:
                        # Subsequent queries: use existing session
                        result = subprocess.run(["opencode", "run", "--session", current_session_id, command], capture_output=True, text=True, timeout=60)
                        response = (result.stdout or "").strip() or "No response"
                    msg_queue.put({"type": "insert", "text": "AI Response: " + response + "\n"})
                    speak("Response received")
                except subprocess.TimeoutExpired:
                    msg_queue.put({"type": "insert", "text": "AI query timed out\n"})
                except FileNotFoundError:
                    msg_queue.put({"type": "insert", "text": "AI assistance not available\n"})
                finally:
                    root.after(1000, lambda: glow_logo(False, False))  # Stop red glow
    else:
        msg_queue.put({"type": "insert", "text": "No command heard\n"})
    msg_queue.put(
        {"type": "status", "text": "Status: Listening", "color": "red"}
    )
    msg_queue.put({"type": "insert", "text": "Activated!\n"})
    speak("Activated!")

    # Get the command/query
    input_text = listen()

    if not input_text:
        msg_queue.put({"type": "insert", "text": "No input heard\n"})
        speak("No input heard")
    elif ai_mode.get():
        # AI Mode: check if it's a basic command first, otherwise send to AI
        input_lower = input_text.lower()
        if input_lower.startswith("open "):
            # Handle open commands even in AI mode
            app = input_lower.split("open")[-1].strip()
            response = open_app(app)
            msg_queue.put({"type": "insert", "text": f"Command: {input_text}\n{response}\n"})
            speak(response)
        else:
            # Send to AI
            msg_queue.put({"type": "insert", "text": "AI Query: " + input_text + "\n"})
            try:
                if current_session_id is None:
                    # First query: start new session
                    result = subprocess.run(["opencode", "run", input_text], capture_output=True, text=True, timeout=60)
                    response = (result.stdout or "").strip() or "No response"
                    # Get the session ID
                    current_session_id = get_latest_session_id()
                    if current_session_id:
                        msg_queue.put({'type': 'insert', 'text': "New AI session started (ID: " + current_session_id + ")" + chr(10)})
                    else:
                        msg_queue.put({'type': 'insert', 'text': "Warning: Could not retrieve session ID" + chr(10)})
                else:
                    # Subsequent queries: use existing session
                    result = subprocess.run(["opencode", "run", "--session", current_session_id, input_text], capture_output=True, text=True, timeout=60)
                    response = (result.stdout or "").strip() or "No response"
                msg_queue.put({"type": "insert", "text": "AI Response: " + response + "\n"})
                speak("Response received")
            except subprocess.TimeoutExpired:
                msg_queue.put({"type": "insert", "text": "AI query timed out\n"})
            except FileNotFoundError:
                msg_queue.put({"type": "insert", "text": "opencode command not found\n"})
    else:
        # Normal Mode: process commands directly
        command = input_text
        if "open" in command.lower():
            app = command.lower().split("open")[-1].strip()
            response = open_app(app)
            msg_queue.put({"type": "insert", "text": f"Command: {command}\n{response}\n"})
            speak(response)
        else:
            msg_queue.put({"type": "insert", "text": "Heard: " + command + "\n"})
    msg_queue.put(
        {"type": "status", "text": "Status: Listening", "color": "red"}
    )

def listen_loop():
    global wake_words, msg_queue
    listening_for_command = False
    while True:
        text_widget = listen()
        if text_widget:
            activated = any(wake in text_widget.lower() for wake in wake_words)
            if activated:
                # Trigger wake word glow
                msg_queue.put({"type": "wake_word_detected"})
                listening_for_command = True
                # Trigger manual activation when wake word is detected
                manual_activate()
                # Stop glowing after activation completes
                msg_queue.put({"type": "wake_word_end"})
                listening_for_command = False
            else:
                msg_queue.put(
                    {"type": "insert", "text": "Darvis heard: " + text_widget + "\n"}
                )
def restart_app():
    os.execv(sys.executable, [sys.executable] + sys.argv)


def update_gui():
    global msg_queue, root, text_heard, text_info
    try:
        msg = msg_queue.get_nowait()
        if msg["type"] == "insert":
            # Route messages to appropriate text widgets
            if msg["text"].startswith("Darvis heard:"):
                # Remove the "Darvis heard:" prefix and just show the text
                clean_text = msg["text"].replace("Darvis heard: ", "", 1)
                # Start glow effect during insertion
                glow_textbox(text_heard, True)
                text_heard.insert(tk.END, clean_text)
                text_heard.see(tk.END)
                # Keep glowing for a moment then stop
                root.after(1500, lambda: glow_textbox(text_heard, False))
            elif msg["text"].startswith("Heard:"):
                # Remove the "Heard:" prefix and just show the text
                clean_text = msg["text"].replace("Heard: ", "", 1)
                # Start glow effect during insertion
                glow_textbox(text_heard, True)
                text_heard.insert(tk.END, clean_text)
                text_heard.see(tk.END)
                # Keep glowing for a moment then stop
                root.after(1500, lambda: glow_textbox(text_heard, False))
            elif msg["text"].startswith("Command:") or msg["text"].startswith("AI Query:") or msg["text"].startswith("AI Response:"):
                text_info.insert(tk.END, msg["text"])
                text_info.see(tk.END)
                # Glow effect for info text
                glow_textbox(text_info, True, "#FFFF00")  # Yellow glow
                root.after(1000, lambda: glow_textbox(text_info, False))
            else:
                # General info messages
                text_info.insert(tk.END, msg["text"])
                text_info.see(tk.END)
                # Glow effect for info text
                glow_textbox(text_info, True, "#FFFF00")  # Yellow glow
                root.after(1000, lambda: glow_textbox(text_info, False))
        elif msg["type"] == "wake_word_detected":
            # Glow logo when wake word is detected
            glow_logo(True)
        elif msg["type"] == "wake_word_end":
            # Stop glowing logo
            glow_logo(False)
    except queue.Empty:
        pass

    root.after(100, update_gui)


def glow_textbox(widget, enable_glow, color="#00FF00"):
    """Add or remove glow effect from text widgets"""
    if enable_glow:
        widget.config(highlightbackground=color, highlightcolor=color, highlightthickness=2)
    else:
        widget.config(highlightbackground="black", highlightcolor="black", highlightthickness=0)

def glow_logo(enable_glow, ai_active=False):
    """Add or remove glow effect from logo"""
    try:
        if enable_glow:
            if ai_active:
                # Red glow for AI processing
                logo_label.config(highlightbackground="#FF0000", highlightcolor="#FF0000", highlightthickness=3)
            else:
                # Green glow for wake word
                logo_label.config(highlightbackground="#00FF00", highlightcolor="#00FF00", highlightthickness=3)
        else:
            logo_label.config(highlightbackground="black", highlightcolor="black", highlightthickness=0)
    except NameError:
        pass  # logo_label not yet defined

def submit_manual_input() -> None:
    """
    Process manual text input from the GUI input field.

    Handles both AI queries and direct commands based on current mode.
    Provides visual feedback and clears input field after processing.

    Triggers:
        - Enter key press in manual input field
        - Submit button click (if implemented)

    Effects:
        - Input field flashes green
        - Text is processed as command or AI query
        - Input field is cleared
        - Results displayed in appropriate text areas
    """
    global manual_input_entry, msg_queue, ai_mode, current_session_id
    input_text = manual_input_entry.get().strip()
    if input_text:
        # Change text color to green when submitted
        manual_input_entry.config(fg="green")
        root.after(1000, lambda: manual_input_entry.config(fg="white"))  # Reset after 1 second

        # Intelligent command processing with automatic AI fallback
        input_lower = input_text.lower()

        # Check if it's a local command first
        if input_lower.startswith("open "):
            # Handle open commands locally
            app = input_lower.split("open")[-1].strip()
            response = open_app(app)
            msg_queue.put({"type": "insert", "text": f"Command: {input_text}\n{response}\n"})
            speak(response)
        else:
            # Check if it looks like a command we can handle locally
            local_commands = ["calculator", "terminal", "editor", "browser"]
            if any(cmd in input_lower for cmd in local_commands):
                # Try to handle as local command
                app = input_lower  # Pass the full input to open_app
                response = open_app(app)
                if "Sorry, I don't know how to open" in response:
                    # Fall back to AI
                    msg_queue.put({"type": "insert", "text": f"Local command failed, using AI assistance...\nAI Query: {input_text}\n"})
                    glow_logo(True, True)  # Red glow for AI
                    try:
                        if current_session_id is None:
                            # First query: start new session
                            result = subprocess.run(["opencode", "run", input_text], capture_output=True, text=True, timeout=60)
                            response = (result.stdout or "").strip() or "No response"
                            # Get the session ID
                            current_session_id = get_latest_session_id()
                            if current_session_id:
                                msg_queue.put({'type': 'insert', 'text': "New AI session started (ID: " + current_session_id + ")" + chr(10)})
                            else:
                                msg_queue.put({'type': 'insert', 'text': "Warning: Could not retrieve session ID" + chr(10)})
                        else:
                            # Subsequent queries: use existing session
                            result = subprocess.run(["opencode", "run", "--session", current_session_id, input_text], capture_output=True, text=True, timeout=60)
                            response = (result.stdout or "").strip() or "No response"
                        msg_queue.put({"type": "insert", "text": "AI Response: " + response + "\n"})
                        speak("Response received")
                    except subprocess.TimeoutExpired:
                        msg_queue.put({"type": "insert", "text": "AI query timed out\n"})
                    except FileNotFoundError:
                        msg_queue.put({"type": "insert", "text": "AI assistance not available\n"})
                    finally:
                        root.after(1000, lambda: glow_logo(False, False))  # Stop red glow
                else:
                    msg_queue.put({"type": "insert", "text": f"Command: {input_text}\n{response}\n"})
                    speak(response)
            else:
                # Default to AI for unrecognized inputs
                msg_queue.put({"type": "insert", "text": f"Using AI assistance...\nAI Query: {input_text}\n"})
                glow_logo(True, True)  # Red glow for AI
                try:
                    if current_session_id is None:
                        # First query: start new session
                        result = subprocess.run(["opencode", "run", input_text], capture_output=True, text=True, timeout=60)
                        response = (result.stdout or "").strip() or "No response"
                        # Get the session ID
                        current_session_id = get_latest_session_id()
                        if current_session_id:
                            msg_queue.put({'type': 'insert', 'text': "New AI session started (ID: " + current_session_id + ")" + chr(10)})
                        else:
                            msg_queue.put({'type': 'insert', 'text': "Warning: Could not retrieve session ID" + chr(10)})
                    else:
                        # Subsequent queries: use existing session
                        result = subprocess.run(["opencode", "run", "--session", current_session_id, input_text], capture_output=True, text=True, timeout=60)
                        response = (result.stdout or "").strip() or "No response"
                    msg_queue.put({"type": "insert", "text": "AI Response: " + response + "\n"})
                    speak("Response received")
                except subprocess.TimeoutExpired:
                    msg_queue.put({"type": "insert", "text": "AI query timed out\n"})
                except FileNotFoundError:
                    msg_queue.put({"type": "insert", "text": "AI assistance not available\n"})
                finally:
                    root.after(1000, lambda: glow_logo(False, False))  # Stop red glow

        manual_input_entry.delete(0, tk.END)  # Clear the input field

def main():
    global msg_queue, wake_words, ai_mode, ai_button, text_heard, text_info, manual_input_entry, root
    msg_queue = queue.Queue()
    wake_words = [
        "hey darvis",
        "hey jarvis",
        "play darvis",
        "play jarvis",
        "hi darvis",
        "hi jarvis",
    ]

    root = tk.Tk()
    root.title("Darvis Voice Assistant")
    root.configure(bg="black")

    # Top frame for input (no header)
    top_frame = tk.Frame(root, bg="black")
    top_frame.pack(fill=tk.X, padx=10, pady=5)

    # Initialize variables after Tk root
    ai_mode = tk.BooleanVar()





    # Manual input section
    input_frame = tk.Frame(root, bg="black")
    input_frame.pack(fill=tk.X, padx=10, pady=5)

    manual_input_entry = tk.Entry(input_frame, font=("Arial", 16), bg="#333333", fg="white", insertbackground="white")
    manual_input_entry.pack(fill=tk.X, pady=2)
    manual_input_entry.bind("<Return>", lambda e: submit_manual_input())
    manual_input_entry.bind("<Key>", lambda e: glow_textbox(manual_input_entry, True, "#FFFFFF"))
    manual_input_entry.bind("<FocusOut>", lambda e: glow_textbox(manual_input_entry, False))

    # Heard text section
    heard_frame = tk.Frame(root, bg="black")
    heard_frame.pack(fill=tk.X, padx=10, pady=5)

    text_heard = tk.Text(heard_frame, height=4, width=50, font=("Arial", 16), bg="#333333", fg="green")
    text_heard.pack(fill=tk.X, pady=2)

    # Info messages section
    info_frame = tk.Frame(root, bg="black")
    info_frame.pack(fill=tk.X, padx=10, pady=5)

    text_info = tk.Text(info_frame, height=6, width=50, font=("Arial", 16), bg="#333333", fg="yellow")
    text_info.pack(fill=tk.X, pady=2)

    # Initialize info text


    list_microphones()

    threading.Thread(target=listen_loop, daemon=True).start()
    text_info.insert(tk.END, "Darvis is Listening...\n")
    update_gui()

    # Logo centered at bottom
    try:
        logo_image = tk.PhotoImage(file="darvis-logo.png")
        logo_label = tk.Label(root, image=logo_image, bg="black")
        logo_label.image = logo_image  # Keep a reference to prevent garbage collection
        logo_label.pack(side=tk.BOTTOM, pady=20)
    except Exception as e:
        # Fallback if image fails to load
        logo_label = tk.Label(root, text="DARVIS", font=("Arial", 24), bg="black", fg="white")
        logo_label.pack(side=tk.BOTTOM, pady=20)

    root.mainloop()


if __name__ == "__main__":
    main()
    msg_queue = queue.Queue()
    wake_words = [
        "hey darvis",
        "hey jarvis",
        "play darvis",
        "play jarvis",
        "hi darvis",
        "hi jarvis",
    ]

    root = tk.Tk()
    root.title("Darvis Voice Assistant")
    root.configure(bg="black")
    header = tk.Label(root, text="🤖 Darvis", font=("Arial", 20), bg="black", fg="white")
    header.pack(pady=10)

    # Initialize variables after Tk root
    ai_mode = tk.BooleanVar()

    ai_button = tk.Button(
        root, text="AI Mode: OFF", command=toggle_ai, font=("Arial", 12),
        bg="red", fg="white", width=15, relief="raised"
    )
    ai_button.pack(pady=5)
