"""
User interface and GUI components for Darvis Voice Assistant.
"""

import os
import queue
import tkinter as tk
from typing import Optional
from PIL import Image, ImageTk, ImageFilter

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
from .waybar_status import init_waybar, update_waybar_status


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
        self.is_speaking = False

        # Visual effects variables
        self.base_logo_image = None
        self.wake_glow_image = None
        self.ai_glow_image = None
        self.current_logo_state = "normal"

    def load_logo_images(self):
        """Load and create enhanced logo images with glow effects."""
        try:
            # Load base image
            base_img = Image.open("assets/darvis-logo.png").convert("RGBA")

            # Create base PhotoImage for tkinter
            self.base_logo_image = ImageTk.PhotoImage(base_img)

            # Create wake word glow effect (green border)
            wake_glow = self.create_border_glow(base_img, (0, 255, 0, 255), blur_radius=3)
            self.wake_glow_image = ImageTk.PhotoImage(wake_glow)

            # Create AI glow effect (red eyes)
            ai_glow = self.create_eye_glow(base_img, (255, 0, 0, 255))
            self.ai_glow_image = ImageTk.PhotoImage(ai_glow)

        except Exception as e:
            print(f"Failed to create enhanced logo effects: {e}")
            # Fallback to basic image
            self.base_logo_image = ImageTk.PhotoImage(Image.open("assets/darvis-logo.png").convert("RGBA"))

    def create_border_glow(self, image, glow_color, blur_radius=3):
        """Create a glowing border effect around the image."""
        # Create a larger canvas for the glow
        width, height = image.size
        glow_size = blur_radius * 2
        canvas_size = (width + glow_size * 2, height + glow_size * 2)

        # Create glow layer
        glow_layer = Image.new("RGBA", canvas_size, (0, 0, 0, 0))

        # Draw the original image in the center
        glow_layer.paste(image, (glow_size, glow_size), image)

        # Create border glow effect
        border_glow = Image.new("RGBA", canvas_size, (0, 0, 0, 0))

        # Add glow around the edges
        for x in range(glow_size):
            for y in range(glow_size):
                if x == 0 or y == 0 or x == glow_size-1 or y == glow_size-1:
                    # Draw glow pixels around the border
                    glow_alpha = int(255 * (1 - (x + y) / (glow_size * 2)))
                    if glow_alpha > 0:
                        border_glow.putpixel((x, y), glow_color[:3] + (glow_alpha,))
                        border_glow.putpixel((width + glow_size + x, y), glow_color[:3] + (glow_alpha,))
                        border_glow.putpixel((x, height + glow_size + y), glow_color[:3] + (glow_alpha,))
                        border_glow.putpixel((width + glow_size + x, height + glow_size + y), glow_color[:3] + (glow_alpha,))

        # Apply gaussian blur to the glow
        border_glow = border_glow.filter(ImageFilter.GaussianBlur(radius=blur_radius/2))

        # Composite the original image over the glow
        result = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
        result.paste(border_glow, (0, 0), border_glow)
        result.paste(image, (glow_size, glow_size), image)

        return result

    def create_eye_glow(self, image, eye_color):
        """Create a red glow effect in the eyes of the face."""
        # This is a simplified implementation - in a real scenario,
        # you'd need to detect the eye regions in the image
        # For now, we'll create a general glow effect

        width, height = image.size
        eye_glow = image.copy()

        # Create eye glow regions (approximate positions - would need image analysis for precision)
        # Assuming eyes are in the upper portion of the face
        eye_regions = [
            (width//2 - 20, height//3 - 10, width//2 - 5, height//3 + 5),  # Left eye
            (width//2 + 5, height//3 - 10, width//2 + 20, height//3 + 5),  # Right eye
        ]

        # Apply glow to eye regions
        for x in range(width):
            for y in range(height):
                for eye_region in eye_regions:
                    ex1, ey1, ex2, ey2 = eye_region
                    if ex1 <= x <= ex2 and ey1 <= y <= ey2:
                        # Create glow effect around eyes
                        distance = min(abs(x - ex1), abs(x - ex2), abs(y - ey1), abs(y - ey2))
                        if distance <= 3:  # Within glow radius
                            alpha = int(180 * (1 - distance/3))  # Fade with distance
                            if alpha > 0:
                                r, g, b, a = eye_glow.getpixel((x, y))
                                # Blend with glow color
                                new_r = int((r * (255 - alpha) + eye_color[0] * alpha) / 255)
                                new_g = int((g * (255 - alpha) + eye_color[1] * alpha) / 255)
                                new_b = int((b * (255 - alpha) + eye_color[2] * alpha) / 255)
                                eye_glow.putpixel((x, y), (new_r, new_g, new_b, a))

        return eye_glow

        self.setup_ui()
        self.bind_events()
        self.setup_system_tray()
        self.start_voice_processing()
        self.start_message_processing()

        # Enhanced window management
        self.setup_window_positioning()

    def setup_window_positioning(self):
        """Set up enhanced window positioning and behavior."""
        # Center the window on the screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 600
        window_height = 400
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Make window visible and focused
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

        # Handle window close button (X) - minimize to tray instead of quit
        self.root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

        # Handle minimize events
        self.root.bind("<Unmap>", self.on_minimize)

    def minimize_to_tray(self):
        """Minimize to system tray instead of quitting."""
        if self.tray_icon:
            self.root.withdraw()
            # Could show a notification here
        else:
            # No tray icon available, quit normally
            self.quit_app()

    def on_minimize(self, event=None):
        """Handle window minimize events."""
        # On some systems, this could trigger tray minimization
        pass

    def show_about(self):
        """Show about dialog."""
        about_text = """Darvis Voice Assistant

A modern, cross-platform voice assistant
with intelligent command processing.

Features:
• Voice wake word detection
• AI-powered responses
• System tray integration
• Waybar status support
• Cross-platform compatibility

Version: 1.0.0
Built with ❤️"""
        self.display_message(f"About Darvis:\n{about_text}\n")

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

        # Logo centered at bottom with enhanced visual effects
        try:
            self.load_logo_images()
            if self.base_logo_image:
                self.logo_label = tk.Label(self.root, image=self.base_logo_image, bg="black")
                self.logo_label.pack(side=tk.BOTTOM, pady=20)
            else:
                raise Exception("Logo images failed to load")
        except Exception as e:
            print(f"Enhanced logo loading failed: {e}")
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
        update_waybar_status("thinking", f"Thinking about: {command[:30]}...")
        try:
            response, session_id = process_ai_query(command)
            if session_id:
                self.display_message(f"New AI session started (ID: {session_id})\n")
            update_waybar_status("speaking", "Speaking response...")
            self.display_message(f"AI Response: {response}\n")
            speak(response)  # Speak the actual response
            update_waybar_status("success", "Response delivered")
        except Exception as e:
            error_msg = str(e)
            if "opencode" in error_msg.lower():
                self.display_message("AI assistance not available (opencode not found)\n")
                update_waybar_status("error", "AI not available")
            else:
                self.display_message(f"AI error: {error_msg}\n")
                update_waybar_status("error", f"AI error: {error_msg[:50]}")
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
        """Add or remove sophisticated glow effect from logo."""
        try:
            if not hasattr(self, 'logo_label') or not self.logo_label:
                return

            if enable_glow:
                if ai_active and self.ai_glow_image:
                    # Red eye glow for AI processing
                    self.logo_label.config(image=self.ai_glow_image)
                    self.logo_label.image = self.ai_glow_image  # Keep reference
                    self.current_logo_state = "ai"
                elif self.wake_glow_image:
                    # Green border glow for wake word
                    self.logo_label.config(image=self.wake_glow_image)
                    self.logo_label.image = self.wake_glow_image  # Keep reference
                    self.current_logo_state = "wake"
            else:
                # Return to normal state
                if self.base_logo_image:
                    self.logo_label.config(image=self.base_logo_image)
                    self.logo_label.image = self.base_logo_image  # Keep reference
                self.current_logo_state = "normal"
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

            # Create enhanced tray menu
            menu = pystray.Menu(
                pystray.MenuItem("Show/Hide Window", self.toggle_window),
                pystray.MenuItem("Minimize to Tray", self.minimize_to_tray),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Voice Commands", pystray.Menu(
                    pystray.MenuItem("Say 'hey darvis'", lambda: None, enabled=False),
                    pystray.MenuItem("Say 'open calculator'", lambda: None, enabled=False),
                    pystray.MenuItem("Say 'what is 2+2'", lambda: None, enabled=False),
                )),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("About", self.show_about),
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