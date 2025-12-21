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
        print(f"TTS error: {e}")


def list_microphones():
    p = pyaudio.PyAudio()
    print("Available microphones:")
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info["maxInputChannels"] > 0:
            print(f"Index {i}: {info['name']}")
    p.terminate()


def listen(device_index=None):
    global manual_input_mode
    if manual_input_mode.get():
        try:
            return input("Manual input: ").lower()
        except EOFError:
            return ""
    else:
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
    # Map common app names to commands
    app_map = {
        "chrome": "chromium",
        "browser": "firefox",
        "terminal": "xterm",
        "editor": "gedit",
        "calculator": "galculator"
    }
    app_command = app_map.get(app_name.lower(), app_name)
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

def restart_app():
    os.execv(sys.executable, [sys.executable] + sys.argv)


def update_gui():
    global msg_queue, root, text, status_label
    try:
        msg = msg_queue.get_nowait()
        if msg["type"] == "insert":
            text.insert(tk.END, msg["text"])
            text.see(tk.END)
        elif msg["type"] == "status":
            status_label.config(text=msg["text"], fg=msg["color"])
    except queue.Empty:
        pass
    root.after(100, update_gui)


def listen_loop():
    global wake_words, ai_mode, msg_queue
    while True:
        text_widget = listen()
        if text_widget:
            activated = any(wake in text_widget.lower() for wake in wake_words)
            if activated:
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
            else:
                msg_queue.put(
                    {"type": "insert", "text": "Darvis heard: " + text_widget + "\n"}
                )


def main():
    global msg_queue, wake_words, ai_mode, ai_button, text, status_label, root
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
    header = tk.Label(root, text="🤖 Darvis", font=("Arial", 20))
    header.pack(pady=10)
    ai_mode = tk.BooleanVar()
    ai_button = tk.Button(
        root, text="AI Mode: OFF", command=toggle_ai, font=("Arial", 12),
        bg="red", fg="white", width=15, relief="raised"
    )
    ai_button.pack(pady=5)
    restart_button = tk.Button(
        root, text="Restart", command=restart_app, font=("Arial", 12),
        bg="blue", fg="white", width=15, relief="raised"
    )
    restart_button.pack(pady=5)
    status_label = tk.Label(
        root, text="Status: Listening", fg="red", font=("Arial", 14)
    )
    status_label.pack(pady=5)
    text = tk.Text(root, height=10, width=50, font=("Arial", 12))
    text.pack(pady=10)
    text.insert(tk.END, "Starting Darvis...\n")

    list_microphones()

    threading.Thread(target=listen_loop, daemon=True).start()
    update_gui()
    root.mainloop()


if __name__ == "__main__":
    main()
