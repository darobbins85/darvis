import os
import queue
import subprocess
import threading
import tkinter as tk

import pyaudio
import pyttsx3
import speech_recognition as sr
import os
import sys

os.environ["ALSA_LOG_LEVEL"] = "0"

conversation_history = []
current_session_id = None

def speak(text):
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


def listen(device_index=None):
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

def open_app(app_name):
    app_name_lower = app_name.lower()

    # Map common app names to commands
    app_map = {
        "chrome": "chromium",
        "browser": "firefox",
        "firefox": "firefox",
        "chromium": "chromium",
        "terminal": "xterm",
        "editor": "gedit",
        "gedit": "gedit",
        "calculator": "galculator",
        "galculator": "galculator"
    }

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
        # Try direct app launch
        app_command = app_map.get(app_name_lower, app_name)
        try:
            subprocess.Popen([app_command])
            return "Opening " + app_name
        except FileNotFoundError:
            return "Sorry, I don't know how to open " + app_name


def toggle_ai():
    global ai_mode
    ai_mode.set(not ai_mode.get())
    ai_button.config(text="AI Mode: ON" if ai_mode.get() else "AI Mode: OFF",
                      bg="green" if ai_mode.get() else "red",
                      fg="white",
                      width=15,
                      relief="raised")



def manual_activate():
    global msg_queue, ai_mode
    msg_queue.put(
        {"type": "status", "text": "Status: Activated", "color": "green"}
    )
    msg_queue.put({"type": "insert", "text": "Activated!\n"})
    speak("Activated!")

    if ai_mode.get():
        # AI Mode: listen for query and run opencode
        query = listen()
        if query:
            msg_queue.put(
                {"type": "insert", "text": "Query: " + query + chr(10)}
            )
            try:
                global current_session_id
                if current_session_id is None:
                    # First query: start new session
                    result = subprocess.run(["opencode", "run", query], capture_output=True, text=True, timeout=60)
                    response = (result.stdout or "").strip() or "No response"
                    # Get the session ID
                    current_session_id = get_latest_session_id()
                    if current_session_id:
                        msg_queue.put({'type': 'insert', 'text': "New AI session started (ID: " + current_session_id + ")" + chr(10)})
                    else:
                        msg_queue.put({'type': 'insert', 'text': "Warning: Could not retrieve session ID" + chr(10)})
                else:
                    # Subsequent queries: use existing session
                    result = subprocess.run(["opencode", "run", "--session", current_session_id, query], capture_output=True, text=True, timeout=60)
                    response = (result.stdout or "").strip() or "No response"
                msg_queue.put(
                    {
                        "type": "insert",
                        "text": "AI Response: " + response + chr(10),
                    }
                )
                speak("Response received")
            except subprocess.TimeoutExpired:
                msg_queue.put(
                    {"type": "insert", "text": "AI query timed out\n"}
                )
            except FileNotFoundError:
                msg_queue.put(
                    {
                        "type": "insert",
                        "text": "opencode command not found\n",
                    }
                )
        else:
            msg_queue.put({"type": "insert", "text": "No query heard\n"})
    else:
        # Normal Mode
        command = listen()
        if command:
            if "open" in command:
                app = command.split("open")[-1].strip()
                response = open_app(app)
                msg_queue.put({"type": "insert", "text": response + "\n"})
                speak(response)
            else:
                msg_queue.put(
                    {"type": "insert", "text": "Heard: " + command + "\n"}
                )
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
                text_heard.insert(tk.END, clean_text)
                text_heard.see(tk.END)
                # Glow effect for heard text
                glow_textbox(text_heard, True)
                root.after(1000, lambda: glow_textbox(text_heard, False))
            elif msg["text"].startswith("Heard:"):
                # Remove the "Heard:" prefix and just show the text
                clean_text = msg["text"].replace("Heard: ", "", 1)
                text_heard.insert(tk.END, clean_text)
                text_heard.see(tk.END)
                # Glow effect for heard text
                glow_textbox(text_heard, True)
                root.after(1000, lambda: glow_textbox(text_heard, False))
            elif msg["text"].startswith("Command:") or msg["text"].startswith("AI Query:") or msg["text"].startswith("AI Response:"):
                text_info.insert(tk.END, msg["text"])
                text_info.see(tk.END)
                # Glow effect for info text
                glow_textbox(text_info, True)
                root.after(1000, lambda: glow_textbox(text_info, False))
            else:
                # General info messages
                text_info.insert(tk.END, msg["text"])
                text_info.see(tk.END)
                # Glow effect for info text
                glow_textbox(text_info, True)
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


def glow_textbox(widget, enable_glow):
    """Add or remove glow effect from text widgets"""
    if enable_glow:
        widget.config(highlightbackground="#00FF00", highlightcolor="#00FF00", highlightthickness=2)
    else:
        widget.config(highlightbackground="black", highlightcolor="black", highlightthickness=0)

def glow_logo(enable_glow):
    """Add or remove glow effect from logo"""
    try:
        if enable_glow:
            logo_label.config(highlightbackground="#00FF00", highlightcolor="#00FF00", highlightthickness=3)
        else:
            logo_label.config(highlightbackground="black", highlightcolor="black", highlightthickness=0)
    except NameError:
        pass  # logo_label not yet defined

def submit_manual_input():
    """Handle manual input submission from the input field"""
    global manual_input_entry, msg_queue, ai_mode, current_session_id
    input_text = manual_input_entry.get().strip()
    if input_text:
        # Change text color to green when submitted
        manual_input_entry.config(fg="green")
        root.after(1000, lambda: manual_input_entry.config(fg="white"))  # Reset after 1 second

        # Process the input the same way as voice/manual input
        if ai_mode.get():
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

    manual_input_entry = tk.Entry(input_frame, font=("Arial", 12), bg="#333333", fg="white", insertbackground="white")
    manual_input_entry.pack(fill=tk.X, pady=2)
    manual_input_entry.bind("<Return>", lambda e: submit_manual_input())
    manual_input_entry.bind("<Key>", lambda e: glow_textbox(manual_input_entry, True))
    manual_input_entry.bind("<FocusOut>", lambda e: glow_textbox(manual_input_entry, False))

    # Heard text section
    heard_frame = tk.Frame(root, bg="black")
    heard_frame.pack(fill=tk.X, padx=10, pady=5)

    text_heard = tk.Text(heard_frame, height=4, width=50, font=("Arial", 12), bg="#333333", fg="green")
    text_heard.pack(fill=tk.X, pady=2)

    # Info messages section
    info_frame = tk.Frame(root, bg="black")
    info_frame.pack(fill=tk.X, padx=10, pady=5)

    text_info = tk.Text(info_frame, height=6, width=50, font=("Arial", 12), bg="#333333", fg="yellow")
    text_info.pack(fill=tk.X, pady=2)

    # Initialize info text


    list_microphones()

    threading.Thread(target=listen_loop, daemon=True).start()
    text_info.insert(tk.END, "Darvis is Listening...\n")
    update_gui()

    # AI button in bottom left corner
    ai_button = tk.Button(
        root, text="AI Mode: OFF", command=toggle_ai, font=("Arial", 12),
        bg="red", fg="white", width=15, relief="raised"
    )
    ai_button.pack(side=tk.BOTTOM, anchor=tk.W, padx=10, pady=10)

    # Logo centered at bottom
    try:
        logo_image = tk.PhotoImage(file="darvis-logo.png")
        logo_label = tk.Label(root, image=logo_image, bg="black")
        logo_label.image = logo_image  # Keep a reference to prevent garbage collection
        logo_label.pack(side=tk.BOTTOM, pady=10)
    except Exception as e:
        # Fallback if image fails to load
        logo_label = tk.Label(root, text="DARVIS", font=("Arial", 20), bg="black", fg="white")
        logo_label.pack(side=tk.BOTTOM, pady=10)

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
