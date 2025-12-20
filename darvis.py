import speech_recognition as sr
import subprocess
import os
import pyttsx3
import pyaudio
import tkinter as tk

os.environ['ALSA_LOG_LEVEL'] = '0'

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
        if info['maxInputChannels'] > 0:
            print(f"Index {i}: {info['name']}")
    p.terminate()

def listen(device_index=None):
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

def open_app(app_name):
    try:
        subprocess.Popen([app_name])
        return f"Opening {app_name}"
    except FileNotFoundError:
        return f"Sorry, I don't know how to open {app_name}"

def main():
    root = tk.Tk()
    root.title("Darvis Voice Assistant")
    header = tk.Label(root, text="🤖 Darvis", font=("Arial", 20))
    header.pack(pady=10)
    ai_mode = tk.BooleanVar()
    ai_checkbox = tk.Checkbutton(root, text="AI Mode", variable=ai_mode, font=("Arial", 12))
    ai_checkbox.pack(pady=5)
    status_label = tk.Label(root, text="Status: Listening", fg="red", font=("Arial", 14))
    status_label.pack(pady=5)
    text = tk.Text(root, height=10, width=50, font=("Arial", 12))
    text.pack(pady=10)
    text.insert(tk.END, "Starting Darvis...\n")
    root.update()

    list_microphones()  # This will print to console, but GUI hides it

    wake_words = ["hey darvis", "hey jarvis", "play darvis", "play jarvis", "hi darvis", "hi jarvis"]
    while True:
        text_widget = listen()
        if text_widget:
            activated = any(wake in text_widget.lower() for wake in wake_words)
            if activated:
                status_label.config(text="Status: Activated", fg="green")
                text.insert(tk.END, "Activated!\n")
                text.see(tk.END)
                root.update()
                speak("Activated!")
                if ai_mode.get():
                    # AI Mode: listen for query and run opencode
                    query = listen()
                    if query:
                        text.insert(tk.END, f"Query: {query}\n")
                        text.see(tk.END)
                        root.update()
                        try:
                            result = subprocess.run(["opencode", "run", query], capture_output=True, text=True, timeout=30)
                            response = result.stdout.strip() or "No response"
                            text.insert(tk.END, f"AI Response: {response}\n")
                            text.see(tk.END)
                            root.update()
                            speak("Response received")
                        except subprocess.TimeoutExpired:
                            text.insert(tk.END, "AI query timed out\n")
                            text.see(tk.END)
                            root.update()
                        except FileNotFoundError:
                            text.insert(tk.END, "opencode command not found\n")
                            text.see(tk.END)
                            root.update()
                    else:
                        text.insert(tk.END, "No query heard\n")
                        text.see(tk.END)
                        root.update()
                else:
                    # Normal Mode
                    command = listen()
                    if command:
                        if "open" in command:
                            app = command.split("open")[-1].strip()
                            response = open_app(app)
                            text.insert(tk.END, f"{response}\n")
                            text.see(tk.END)
                            root.update()
                            speak(response)
                        else:
                            text.insert(tk.END, f"Heard: {command}\n")
                            text.see(tk.END)
                            root.update()
                    else:
                        text.insert(tk.END, "No command heard\n")
                        text.see(tk.END)
                        root.update()
                status_label.config(text="Status: Listening", fg="red")
            else:
                text.insert(tk.END, f"Darvis heard: {text_widget}\n")
                text.see(tk.END)
                root.update()
        # Silent if no speech
        root.update_idletasks()

if __name__ == "__main__":
    main()