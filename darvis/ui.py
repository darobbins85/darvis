"""
User interface and GUI components for Darvis Voice Assistant.
"""

import os
import queue
import tkinter as tk
import threading
import socket
from PIL import Image, ImageTk

try:
    import pystray  # noqa: F401

    HAS_PYSTRAY = True
except ImportError:
    HAS_PYSTRAY = False

from .ai import process_ai_query


class DarvisGUI:
    """Main GUI class for the Darvis Voice Assistant."""

    def __init__(self):
        print("🏗️ DarvisGUI constructor starting...")
        self.root = tk.Tk()
        self.root.title("Darvis Voice Assistant")
        self.root.configure(bg="black")
        self.root.geometry("800x600")  # Set window size
        self.root.resizable(True, True)  # Allow resizing
        print("✅ Tkinter window created")

        # Initialize variables
        self.msg_queue = queue.Queue()
        self.manual_input_entry = None
        self.text_info = None
        self.logo_label = None
        self.tray_icon = None

        # Logo display
        self.logo_label = None
        self.logo_frame = None  # Frame around logo for glow effect

        # Visual effects variables (like master branch)
        self.base_logo_image = None
        self.wake_glow_image = None
        self.ai_glow_image = None
        self.current_logo_state = "normal"

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
        self.listening_mode = tk.BooleanVar(value=False)  # Default to OFF
        self.conversation_history = []
        self.current_session_id = None
        self.is_speaking = False

        # Web sync variables
        self.web_sync_enabled = False
        self.web_socket = None
        self.web_connected = False

        print("✅ Web sync variables initialized")

        # Initialize web app synchronization
        print("🌐 About to initialize web sync...")
        try:
            self.init_web_sync()
            print("✅ init_web_sync completed successfully")
        except Exception as e:
            print(f"❌ init_web_sync failed with exception: {e}")
            import traceback

            traceback.print_exc()

        print("🔧 About to call setup methods...")
        try:
            self.setup_ui()
            print("✅ setup_ui completed")
        except Exception as e:
            print(f"❌ setup_ui failed: {e}")
            import traceback
            traceback.print_exc()

        try:
            self.bind_events()
            self.setup_system_tray()
            self.start_voice_processing()
            self.start_message_processing()
            print("✅ All setup methods completed")

            # Logo is already set up with enhanced styling
        except Exception as e:
            print(f"❌ Setup methods failed: {e}")
            import traceback
            traceback.print_exc()

        try:
            self.bind_events()
            self.setup_system_tray()
            self.start_voice_processing()
            self.start_message_processing()

            print("✅ All setup methods completed")
        except Exception as e:
            print(f"❌ Setup methods failed: {e}")
            import traceback

            traceback.print_exc()

    def setup_ui(self):
        """Set up the basic GUI components."""
        print("🔧 Setting up GUI components...")

        try:
            # Create logo frame at the top
            logo_frame = tk.Frame(self.root, bg="black")
            logo_frame.pack(fill=tk.X, padx=10, pady=10)
            print("✅ Logo frame created")

            # Try to load and create logo with image immediately
            try:
                # Load base image
                base_img = Image.open("assets/darvis-logo.png").convert("RGBA")

                # Create base PhotoImage for tkinter immediately
                self.base_logo_image = ImageTk.PhotoImage(base_img)

                # Create wake word glow effect (green eyes)
                wake_glow = self.create_eye_glow(base_img, (0, 255, 0, 255))
                self.wake_glow_image = ImageTk.PhotoImage(wake_glow)

                # Create AI glow effect (red eyes)
                ai_glow = self.create_eye_glow(base_img, (255, 20, 20, 255))
                self.ai_glow_image = ImageTk.PhotoImage(ai_glow)

                # Create logo label with base image immediately
                self.logo_label = tk.Label(logo_frame, image=self.base_logo_image, bg="black")
                self.logo_label.pack(side=tk.TOP, padx=10, pady=10)
                print("✅ Logo with actual image created successfully")

            except Exception as e:
                print(f"⚠️ Image loading failed: {e}, using text fallback")
                # Fallback text logo
                self.logo_label = tk.Label(
                    logo_frame,
                    text="DARVIS",
                    bg="black",
                    fg="#00D4FF",
                    font=('Arial', 28, 'bold')
                )
                self.logo_label.pack(side=tk.TOP, padx=10, pady=10)
                print("✅ Fallback text logo created")

            # Create main text area for chat
            self.text_info = tk.Text(
                self.root,
                bg="black",
                fg="white",
                font=("JetBrains Mono", 12),
                wrap=tk.WORD,
                state=tk.DISABLED,
            )
            self.text_info.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
            print("✅ Text area created")

            # Configure text tags for colored messages
            self.text_info.tag_config("you", foreground="green")
            self.text_info.tag_config("ai", foreground="red")
            self.text_info.tag_config("web_user", foreground="yellow")

            # Create controls frame
            controls_frame = tk.Frame(self.root, bg="black")
            controls_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

            # Copy chat button
            copy_button = tk.Button(
                controls_frame,
                text="📋 Copy Chat",
                bg="#333",
                fg="white",
                font=("JetBrains Mono", 10),
                command=self.copy_chat
            )
            copy_button.pack(side=tk.RIGHT)
            print("✅ Copy button created")

            # Create input frame
            input_frame = tk.Frame(self.root, bg="black")
            input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
            print("✅ Input frame created")

            # Manual input entry
            self.manual_input_entry = tk.Entry(
                input_frame,
                bg="#333",
                fg="white",
                font=("JetBrains Mono", 12),
                insertbackground="white",
            )
            self.manual_input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            print("✅ Input entry created")

            # Submit button
            submit_button = tk.Button(
                input_frame,
                text="Send",
                command=self.submit_manual_input,
                bg="#007AFF",
                fg="white",
                font=("JetBrains Mono", 10),
            )
            submit_button.pack(side=tk.RIGHT, padx=(5, 0))
            print("✅ Submit button created")

            print("✅ GUI setup completed - all widgets created")
        except Exception as e:
            print(f"❌ Error in setup_ui: {e}")
            import traceback

            traceback.print_exc()

    def bind_events(self):
        """Bind GUI events."""
        if self.manual_input_entry:
            # Bind Enter key to submit function
            self.manual_input_entry.bind('<Return>', lambda event: self.submit_manual_input())

    def setup_system_tray(self):
        """Set up system tray icon."""
        pass

    def start_voice_processing(self):
        """Start voice processing."""
        pass

    def start_message_processing(self):
        """Start message processing."""
        pass

    def display_message(self, message):
        """Display a message in the GUI."""
        if self.text_info:
            self.text_info.config(state=tk.NORMAL)

            # Apply color tags for entire You: and AI: messages
            if message.startswith("You:"):
                self.text_info.insert(tk.END, message, "you")
            elif message.startswith("AI:"):
                self.text_info.insert(tk.END, message, "ai")
            else:
                self.text_info.insert(tk.END, message)

            self.text_info.config(state=tk.DISABLED)

            # Ensure auto-scroll happens after widget updates
            if self.text_info:
                self.root.after(10, lambda: self.text_info.see(tk.END))
            self.text_info.see(tk.END)

    def copy_chat(self):
        """Copy the entire chat content to clipboard."""
        if self.text_info:
            chat_content = self.text_info.get("1.0", tk.END).strip()
            self.root.clipboard_clear()
            self.root.clipboard_append(chat_content)
            print("📋 Chat content copied to clipboard")

    def send_to_web(self, message):
        """Send a message to the web interface if connected."""
        if self.web_connected and self.web_socket:
            try:
                self.web_socket.emit("chat_message", {"message": message})
            except Exception as e:
                print(f"🌐 Failed to send to web: {e}")







    def glow_logo(self, enable_glow, ai_active=False):
        """Add or remove glow effect from logo by switching images (like master branch)."""
        print(f"🔥 glow_logo called: enable_glow={enable_glow}, ai_active={ai_active}")

        if not self.logo_label:
            print("❌ No logo label, returning")
            return

        try:
            if enable_glow:
                if ai_active and self.ai_glow_image:
                    print("🔴 Setting AI (red) glow - switching to glow image")
                    # Red eye glow for AI processing
                    self.logo_label.config(image=self.ai_glow_image)
                    self.logo_label.image = self.ai_glow_image  # Keep reference
                    self.current_logo_state = "ai"
                elif self.wake_glow_image:
                    print("🟢 Setting wake (green) glow - switching to glow image")
                    # Green eye glow for wake word
                    self.logo_label.config(image=self.wake_glow_image)
                    self.logo_label.image = self.wake_glow_image  # Keep reference
                    self.current_logo_state = "wake"
                else:
                    print("❌ No glow images available")
            else:
                print("⚪ Restoring normal logo - switching to base image")
                # Restore normal logo
                if self.base_logo_image:
                    self.logo_label.config(image=self.base_logo_image)
                    self.logo_label.image = self.base_logo_image  # Keep reference
                    self.current_logo_state = "normal"
                else:
                    print("❌ No base logo image available")
        except Exception as e:
            print(f"⚠️ Could not update logo glow: {e}")
            import traceback
            traceback.print_exc()



    def create_eye_glow(self, image, eye_color):
        """Create a dramatic red glow effect in the eyes of the face - Terminator style."""
        width, height = image.size
        eye_glow = image.copy()

        # Create eye glow regions (adjusted for our image)
        eye_regions = [
            (
                width // 3 - 15,
                height // 3 - 10,
                width // 3 + 15,
                height // 3 + 10,
            ),  # Left eye
            (
                2*width // 3 - 15,
                height // 3 - 10,
                2*width // 3 + 15,
                height // 3 + 10,
            ),  # Right eye
        ]

        # Create a more dramatic glow effect with brighter center
        glow_radius = 10  # Even larger glow radius for better visibility
        max_alpha = 255  # Maximum brightness

        # Apply intense glow to eye regions with larger radius
        for x in range(width):
            for y in range(height):
                for eye_region in eye_regions:
                    ex1, ey1, ex2, ey2 = eye_region
                    eye_center_x = (ex1 + ex2) // 2
                    eye_center_y = (ey1 + ey2) // 2

                    # Calculate distance from eye center
                    distance = (
                        (x - eye_center_x) ** 2 + (y - eye_center_y) ** 2
                    ) ** 0.5

                    if distance <= glow_radius:
                        # Create intense radial glow effect
                        if distance <= 4:  # Inner glow - very bright
                            blend_factor = min(1.0, 1.0 - (distance / 4.0) ** 0.5)
                        else:  # Outer glow - exponential falloff
                            blend_factor = max(0.1, 0.6 * (1 - (distance - 4) / (glow_radius - 4)) ** 0.7)

                        # Get original pixel
                        r, g, b, a = eye_glow.getpixel((x, y))

                        # Blend with glow color
                        new_r = int(eye_color[0] * blend_factor + r * (1 - blend_factor))
                        new_g = int(eye_color[1] * blend_factor + g * (1 - blend_factor))
                        new_b = int(eye_color[2] * blend_factor + b * (1 - blend_factor))
                        new_a = min(255, int(eye_color[3] * blend_factor + a * (1 - blend_factor)))

                        eye_glow.putpixel((x, y), (new_r, new_g, new_b, new_a))

        return eye_glow



    def submit_manual_input(self):
        """Process manual text input from the GUI."""
        if self.manual_input_entry:
            input_text = self.manual_input_entry.get().strip()
            if input_text:
                # Display the message locally
                self.display_message(f"You: {input_text}\n")

                # Clear the input
                self.manual_input_entry.delete(0, tk.END)

                # Send to web sync
                self.send_to_web(input_text)

                # Handle AI processing based on sync status
                if getattr(self, 'web_sync_enabled', False):
                    print("🌐 Web sync enabled - message sent to web app for processing")
                    # Don't start glow or local processing - web app handles it
                else:
                    print("🚀 Starting local AI processing with glow")
                    self.glow_logo(True, True)  # Red glow for AI processing
                    threading.Thread(
                        target=self._process_ai_query_threaded,
                        args=(input_text,),
                        daemon=True
                    ).start()

    def _process_ai_query_threaded(self, query):
        """Process AI query in background thread."""
        try:
            response, session_id = process_ai_query(query)

            # Update UI on main thread
            self.root.after(0, lambda: self._display_ai_response(response))

        except Exception as e:
            print(f"❌ AI processing failed: {e}")
            self.root.after(0, lambda: self._display_ai_response(f"Error processing query: {e}"))

    def _display_ai_response(self, response):
        """Display AI response and stop glow effect."""
        print(f"🤖 AI response received: {response[:50]}...")
        # Replace the "Processing..." message with the actual response
        # This is a simple approach - in a real app you'd track the processing message
        if not getattr(self, 'web_sync_enabled', False):
            self.display_message(f"AI: {response}\n")
            self.display_message("─" * 50 + "\n")

        # Stop the glow after a longer delay to ensure it's visible
        print("⏰ Scheduling glow stop in 3 seconds")
        self.root.after(3000, lambda: self.glow_logo(False, False))

    def run(self):
        """Run the GUI main loop."""
        self.root.mainloop()

    def init_web_sync(self):
        """Initialize web app synchronization if available."""
        print("🌐 init_web_sync called - starting web sync initialization")
        print(f"🌐 Initial web_sync_enabled: {getattr(self, 'web_sync_enabled', 'not set')}")
        from .config import WEB_APP_HOST, WEB_APP_PORT

        print(f"🌐 Web app config loaded: {WEB_APP_HOST}:{WEB_APP_PORT}")

        # Retry web detection a few times in case web server is still starting
        for attempt in range(1, 4):
            print(f"🌐 Web detection attempt {attempt}/3...")
            try:
                # Check if web app is running
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((WEB_APP_HOST, WEB_APP_PORT))
                sock.close()
                print(f"🌐 Connection test result: {result}")

                if result == 0:
                    print(
                        f"✅ Web app detected at {WEB_APP_HOST}:{WEB_APP_PORT}, enabling sync..."
                    )
                    self.web_sync_enabled = True
                    self.connect_to_web_app()
                    return  # Success, exit function

                print(f"🌐 Web app not detected on attempt {attempt}, waiting...")
                if attempt < 3:
                    import time

                    time.sleep(2)  # Wait 2 seconds before retry

            except Exception as e:
                print(f"🌐 Web sync check failed on attempt {attempt}: {e}")
                if attempt < 3:
                    import time

                    time.sleep(1)

        print("🌐 Web app not detected after 3 attempts, running in standalone mode")
        print(f"🌐 Final web_sync_enabled: {getattr(self, 'web_sync_enabled', False)}")

    def connect_to_web_app(self):
        """Connect to the web app for synchronized chat."""
        print(
            f"🌐 connect_to_web_app called, web_sync_enabled: {self.web_sync_enabled}"
        )
        if not self.web_sync_enabled:
            print("🌐 Web sync not enabled, returning")
            return

        print("🌐 Attempting to import socketio...")
        try:
            # Import socketio client
            import socketio

            print("✅ SocketIO imported successfully")
            print(f"✅ SocketIO version: {getattr(socketio, '__version__', 'unknown')}")

            self.web_socket = socketio.Client()

            def on_connect():
                print("🌐 Connected to web app for chat sync")
                self.web_connected = True

            def on_disconnect():
                print("🌐 Disconnected from web app")
                self.web_connected = False

            def on_user_message(data):
                # Received user message from web interface
                if self.web_connected:
                    # Add to desktop chat with yellow color
                    self.text_info.config(state=tk.NORMAL)
                    self.text_info.insert(tk.END, f"You: {data['message']}\n", "web_user")
                    self.text_info.config(state=tk.DISABLED)
                    self.text_info.see(tk.END)

            def on_ai_message(data):
                # Received AI response from web interface
                if self.web_connected:
                    # Add to desktop chat
                    self.display_message(f"AI: {data['message']}\n")
                    # Dynamic separator based on text widget width
                    width = int(self.text_info.cget('width') or 80) if self.text_info else 80
                    self.display_message("─" * width + "\n")

            # Connect to web app
            from .config import WEB_APP_URL
            self.web_socket.connect(WEB_APP_URL, wait_timeout=5)
            print("🌐 Web sync initialized")

        except Exception as e:
            print(f"❌ Web sync connection failed: {e}")
            self.web_sync_enabled = False

    def quit_app(self):
        """Quit the application."""
        # Disconnect from web app
        if self.web_socket:
            try:
                self.web_socket.disconnect()
            except Exception:
                pass

        if self.tray_icon:
            self.tray_icon.stop()
        self.root.quit()


# Global GUI instance for backward compatibility
_gui_instance = None

# Global PhotoImage reference to prevent garbage collection
_global_logo_photo = None


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
