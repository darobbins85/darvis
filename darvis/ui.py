"""
User interface and GUI components for Darvis Voice Assistant.
"""

import os
import queue
import tkinter as tk
from typing import Optional
from PIL import Image

try:
    import pystray
    HAS_PYSTRAY = True
except ImportError:
    HAS_PYSTRAY = False

from .config import (
    WAKE_WORDS, FONT_SIZE_NORMAL, FONT_SIZE_LARGE,
    GLOW_DURATION_MS, MSG_TYPES
)
from .speech import speak, listen
from .apps import open_app
from .ai import process_ai_query, is_ai_command


class DarvisGUI:
    """Main GUI class for the Darvis Voice Assistant."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Darvis Voice Assistant")
        self.root.configure(bg="black")

        # Initialize variables
        self.msg_queue = queue.Queue()
        self.manual_input_entry = None
        self.text_heard = None
        self.text_info = None
        self.logo_label = None
        self.tray_icon = None

        # Voice and AI variables
        self.wake_words = [
            "hey darvis",
            "hey jarvis",
            "play darvis",
            "play jarvis",
            "hi darvis",
            "hi jarvis",
        ]
        self.ai_mode = tk.BooleanVar()
        self.conversation_history = []
        self.current_session_id = None

        self.setup_ui()
        self.bind_events()
        self.setup_system_tray()
        self.start_voice_processing()
        self.start_message_processing()

    def setup_ui(self):
        """Set up the main UI components."""
        # Top frame for header and buttons (now just input)
        top_frame = tk.Frame(self.root, bg="black")
        top_frame.pack(fill=tk.X, padx=10, pady=5)

        # Manual input section
        input_frame = tk.Frame(self.root, bg="black")
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        self.manual_input_entry = tk.Entry(
            input_frame,
            font=("Arial", FONT_SIZE_NORMAL),
            bg="#333333",
            fg="white",
            insertbackground="white"
        )
        self.manual_input_entry.pack(fill=tk.X, pady=2)
        self.manual_input_entry.bind("<Return>", lambda e: self.submit_manual_input())

        # Heard text section
        heard_frame = tk.Frame(self.root, bg="black")
        heard_frame.pack(fill=tk.X, padx=10, pady=5)

        self.text_heard = tk.Text(
            heard_frame,
            height=4,
            width=50,
            font=("Arial", FONT_SIZE_NORMAL),
            bg="#333333",
            fg="green"
        )
        self.text_heard.pack(fill=tk.X, pady=2)

        # Info messages section
        info_frame = tk.Frame(self.root, bg="black")
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        self.text_info = tk.Text(
            info_frame,
            height=6,
            width=50,
            font=("Arial", FONT_SIZE_NORMAL),
            bg="#333333",
            fg="yellow"
        )
        self.text_info.pack(fill=tk.X, pady=2)

        # Logo centered at bottom
        try:
            logo_image = tk.PhotoImage(file="assets/darvis-logo.png")
            self.logo_label = tk.Label(self.root, image=logo_image, bg="black")
            self.logo_label.image = logo_image  # Keep a reference
            self.logo_label.pack(side=tk.BOTTOM, pady=20)
        except Exception as e:
            # Fallback if image fails to load
            self.logo_label = tk.Label(
                self.root,
                text="DARVIS",
                font=("Arial", FONT_SIZE_LARGE),
                bg="black",
                fg="white"
            )
            self.logo_label.pack(side=tk.BOTTOM, pady=20)

        # Initialize info text
        self.text_info.insert(tk.END, "Darvis is Listening...\n")

    def start_voice_processing(self):
        """Start the voice recognition processing thread."""
        import threading
        voice_thread = threading.Thread(target=self.listen_loop, daemon=True)
        voice_thread.start()

    def listen_loop(self):
        """Main voice processing loop - continuously listen for speech."""
        listening_for_command = False
        while True:
            try:
                text = listen()
                if text:
                    activated = any(wake in text.lower() for wake in self.wake_words)
                    if activated:
                        # Trigger wake word glow
                        self.msg_queue.put({"type": "wake_word_detected"})
                        listening_for_command = True
                        # Trigger manual activation when wake word is detected
                        self.manual_activate()
                        # Stop glowing after activation completes
                        self.msg_queue.put({"type": "wake_word_end"})
                        listening_for_command = False
                    else:
                        self.msg_queue.put(
                            {"type": "insert", "text": "Darvis heard: " + text + "\n"}
                        )
            except Exception as e:
                # Silently handle microphone errors to keep listening
                continue

    def manual_activate(self):
        """Manually activate command listening mode."""
        self.display_message("Activated!\n")
        speak("Activated!")

        # Listen for the actual command
        command = listen()
        if command:
            self.process_command(command, "voice")

    def process_ai_command(self, command: str):
        """Process a command using AI assistance."""
        self.glow_logo(True, True)  # Red glow for AI
        try:
            response, session_id = process_ai_query(command)
            if session_id:
                self.display_message(f"New AI session started (ID: {session_id})\n")
            self.display_message(f"AI Response: {response}\n")
            speak("Response received")
        except Exception as e:
            error_msg = str(e)
            if "opencode" in error_msg.lower():
                self.display_message("AI assistance not available (opencode not found)\n")
            else:
                self.display_message(f"AI error: {error_msg}\n")
        finally:
            self.root.after(1000, lambda: self.glow_logo(False, False))  # Stop red glow

    def start_message_processing(self):
        """Start processing messages from the queue."""
        import threading
        gui_thread = threading.Thread(target=self.update_gui, daemon=True)
        gui_thread.start()

    def update_gui(self):
        """Process messages from the queue and update GUI."""
        try:
            msg = self.msg_queue.get_nowait()
            if msg["type"] == "insert":
                # Route messages to appropriate text widgets
                if msg["text"].startswith("Darvis heard:"):
                    # Remove the "Darvis heard:" prefix and just show the text
                    clean_text = msg["text"].replace("Darvis heard: ", "", 1)
                    # Start glow effect during insertion
                    self.glow_textbox(self.text_heard, True)
                    self.text_heard.insert(tk.END, clean_text)
                    self.text_heard.see(tk.END)
                    # Keep glowing for a moment then stop
                    self.root.after(1500, lambda: self.glow_textbox(self.text_heard, False))
                elif msg["text"].startswith("Command:") or msg["text"].startswith("AI Query:") or msg["text"].startswith("AI Response:"):
                    self.text_info.insert(tk.END, msg["text"])
                    self.text_info.see(tk.END)
                    # Glow effect for info text
                    self.glow_textbox(self.text_info, True, "#FFFF00")  # Yellow glow
                    self.root.after(1000, lambda: self.glow_textbox(self.text_info, False))
                else:
                    # General info messages (like "Activated!")
                    self.text_info.insert(tk.END, msg["text"])
                    self.text_info.see(tk.END)
                    # Glow effect for info text
                    self.glow_textbox(self.text_info, True, "#FFFF00")  # Yellow glow
                    self.root.after(1000, lambda: self.glow_textbox(self.text_info, False))
            elif msg["type"] == "wake_word_detected":
                # Glow logo when wake word is detected
                self.glow_logo(True)
            elif msg["type"] == "wake_word_end":
                self.root.after(1000, lambda: self.glow_logo(False))
        except queue.Empty:
            pass
        # Schedule next check
        self.root.after(100, self.update_gui)

    def bind_events(self):
        """Bind UI events for interactive elements."""
        # Glow effects for manual input
        self.manual_input_entry.bind("<Key>", lambda e: self.glow_textbox(self.manual_input_entry, True, "#FFFFFF"))
        self.manual_input_entry.bind("<FocusOut>", lambda e: self.glow_textbox(self.manual_input_entry, False))

    def glow_textbox(self, widget, enable_glow, color="#00FF00"):
        """Add or remove glow effect from text widgets."""
        if enable_glow:
            widget.config(highlightbackground=color, highlightcolor=color, highlightthickness=2)
        else:
            widget.config(highlightbackground="black", highlightcolor="black", highlightthickness=0)

    def glow_logo(self, enable_glow, ai_active=False):
        """Add or remove glow effect from logo."""
        try:
            if enable_glow:
                if ai_active:
                    # Red glow for AI processing
                    self.logo_label.config(highlightbackground="#FF0000", highlightcolor="#FF0000", highlightthickness=3)
                else:
                    # Green glow for wake word
                    self.logo_label.config(highlightbackground="#00FF00", highlightcolor="#00FF00", highlightthickness=3)
            else:
                self.logo_label.config(highlightbackground="black", highlightcolor="black", highlightthickness=0)
        except AttributeError:
            pass  # logo_label not available

    def submit_manual_input(self):
        """Process manual text input from the GUI input field."""
        input_text = self.manual_input_entry.get().strip()
        if input_text:
            # Change text color to green when submitted
            self.manual_input_entry.config(fg="green")
            self.root.after(1000, lambda: self.manual_input_entry.config(fg="white"))

            # Intelligent command processing
            self.process_command(input_text, "manual")
            self.manual_input_entry.delete(0, tk.END)  # Clear the input field

    def process_command(self, command: str, source: str):
        """Process a command with intelligent AI fallback."""
        command_lower = command.lower()

        # Check if it's a local command first
        if command_lower.startswith("open "):
            # Handle open commands locally
            app = command_lower.split("open")[-1].strip()
            response = open_app(app)
            self.display_message(f"Command: {command}\n{response}\n")
            speak(response)
        else:
            # Check if it looks like a command we can handle locally
            local_commands = ["calculator", "terminal", "editor", "browser"]
            if any(cmd in command_lower for cmd in local_commands):
                # Try to handle as local command
                app = command_lower  # Pass the full input to open_app
                response = open_app(app)
                if "not installed" in response or "not found" in response:
                    # Fall back to AI
                    self.display_message(f"Local command failed, using AI assistance...\nAI Query: {command}\n")
                    self.process_ai_command(command)
                else:
                    self.display_message(f"Command: {command}\n{response}\n")
                    speak(response)
            else:
                # Default to AI for unrecognized inputs
                self.display_message(f"Using AI assistance...\nAI Query: {command}\n")
                self.process_ai_command(command)

    def process_ai_command(self, command: str):
        """Process a command using AI assistance."""
        self.glow_logo(True, True)  # Red glow for AI
        try:
            response, session_id = process_ai_query(command)
            if session_id:
                self.display_message(f"New AI session started (ID: {session_id})\n")
            self.display_message(f"AI Response: {response}\n")
            speak("Response received")
        except Exception as e:
            self.display_message(f"AI error: {str(e)}\n")
        finally:
            self.root.after(1000, lambda: self.glow_logo(False, False))  # Stop red glow

    def display_message(self, message: str):
        """Display a message in the appropriate text area."""
        if message.startswith("Darvis heard:") or message.startswith("Heard:"):
            # Remove prefix and show in heard area
            clean_text = message.replace("Darvis heard: ", "").replace("Heard: ", "")
            self.glow_textbox(self.text_heard, True)
            self.text_heard.insert(tk.END, clean_text)
            self.text_heard.see(tk.END)
            self.root.after(GLOW_DURATION_MS, lambda: self.glow_textbox(self.text_heard, False))
        else:
            # Show in info area
            if "AI Response:" in message or "Command:" in message:
                self.glow_textbox(self.text_info, True, "#FFFF00")  # Yellow glow
            else:
                self.glow_textbox(self.text_info, True, "#FFFF00")  # Yellow glow
            self.text_info.insert(tk.END, message)
            self.text_info.see(tk.END)
            self.root.after(GLOW_DURATION_MS, lambda: self.glow_textbox(self.text_info, False))

    def run(self):
        """Start the GUI event loop."""
        self.root.mainloop()

    def setup_system_tray(self):
        """Set up the system tray icon."""
        if not HAS_PYSTRAY:
            print("System tray not available - pystray not installed")
            return

        # Check if we have a display and system tray
        if not os.environ.get('DISPLAY'):
            print("No display detected - system tray not available")
            return

        try:
            # Load the icon
            icon_path = "assets/darvis-logo.png"
            if not os.path.exists(icon_path):
                print("Warning: assets/darvis-logo.png not found for system tray")
                return

            icon_image = Image.open(icon_path)
            icon_image = icon_image.resize((64, 64))

            # Create tray menu
            menu = pystray.Menu(
                pystray.MenuItem("Show/Hide", self.toggle_window),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Quit", self.quit_app)
            )

            # Create the tray icon
            self.tray_icon = pystray.Icon(
                "darvis",
                icon_image,
                "Darvis Voice Assistant",
                menu
            )

            # Run the tray icon in a separate thread
            import threading
            tray_thread = threading.Thread(target=self._run_tray_icon, daemon=True)
            tray_thread.start()

            print("System tray icon initialized successfully")

        except Exception as e:
            print(f"System tray not available: {e}")
            print("Application will run without system tray icon")

    def _run_tray_icon(self):
        """Run the tray icon with error handling."""
        try:
            self.tray_icon.run()
        except Exception as e:
            print(f"System tray icon failed: {e}")
            # Continue running the application without tray icon

    def toggle_window(self):
        """Toggle the main window visibility."""
        if self.root.state() == 'withdrawn':
            self.root.deiconify()
        else:
            self.root.withdraw()

    def quit_app(self):
        """Quit the application."""
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.quit()


# Global GUI instance for backward compatibility
_gui_instance = None

def init_gui():
    """Initialize the GUI instance."""
    global _gui_instance
    _gui_instance = DarvisGUI()
    return _gui_instance

def get_gui():
    """Get the current GUI instance."""
    return _gui_instance


def main():
    """Main entry point for running the GUI application."""
    # For now, just run the GUI - voice processing is handled differently
    # This allows the desktop launcher to work
    gui = DarvisGUI()
    gui.run()


if __name__ == "__main__":
    main()