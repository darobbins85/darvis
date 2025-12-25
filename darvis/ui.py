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
    WAKE_WORDS,
    FONT_SIZE_NORMAL,
    FONT_SIZE_LARGE,
    GLOW_DURATION_MS,
    MSG_TYPES,
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
        self.listening_mode = tk.BooleanVar(value=False)  # Default to OFF
        self.conversation_history = []
        self.current_session_id = None
        self.is_speaking = False

        # Visual effects variables
        self.base_logo_image = None
        self.wake_glow_image = None
        self.ai_glow_image = None
        self.current_logo_state = "normal"

        # Timer variables
        self.timer_label = None
        self.timer_active = False
        self.timer_seconds = 0
        self.timer_callback = None

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
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

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

    def toggle_listening_mode(self):
        """Toggle listening mode on/off and update display."""
        if self.listening_mode.get():
            self.display_message("Darvis is Listening...\n")
        else:
            self.display_message("Darvis is not listening\n")

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

    def start_countdown_timer(self, seconds=8, color="green"):
        """Start a countdown timer with specified color."""
        self.stop_timer()  # Stop any existing timer
        self.timer_seconds = seconds
        self.timer_active = True
        if self.timer_label:
            self.timer_label.config(fg=color)
            self._update_timer_display()
            self.timer_callback = self.root.after(1000, self._countdown_tick)

    def start_countup_timer(self, color="red"):
        """Start a count-up timer with specified color."""
        self.stop_timer()  # Stop any existing timer
        self.timer_seconds = 0
        self.timer_active = True
        if self.timer_label:
            self.timer_label.config(fg=color)
        self._update_timer_display()
        self.timer_callback = self.root.after(1000, self._countup_tick)

    def stop_timer(self):
        """Stop the active timer."""
        if self.timer_callback:
            self.root.after_cancel(self.timer_callback)
            self.timer_callback = None
        self.timer_active = False
        if self.timer_label:
            self.timer_label.config(text="")

    def _countdown_tick(self):
        """Handle countdown timer tick."""
        if self.timer_active and self.timer_seconds > 0:
            self.timer_seconds -= 1
            self._update_timer_display()
            if self.timer_seconds > 0:
                self.timer_callback = self.root.after(1000, self._countdown_tick)
            else:
                self.stop_timer()

    def _countup_tick(self):
        """Handle count-up timer tick."""
        if self.timer_active:
            self.timer_seconds += 1
            self._update_timer_display()
            self.timer_callback = self.root.after(1000, self._countup_tick)

    def _update_timer_display(self):
        """Update the timer label display."""
        if self.timer_label and self.timer_active:
            self.timer_label.config(text=str(self.timer_seconds))

    def load_logo_images(self):
        """Load and create enhanced logo images with glow effects."""
        try:
            # Load base image
            base_img = Image.open("assets/darvis-logo.png").convert("RGBA")

            # Create base PhotoImage for tkinter
            self.base_logo_image = ImageTk.PhotoImage(base_img)

            # Create wake word glow effect (green eyes) - same as AI but green
            wake_glow = self.create_eye_glow(
                base_img, (0, 255, 0, 255)
            )  # Green eyes for wake word
            self.wake_glow_image = ImageTk.PhotoImage(wake_glow)

            # Create AI glow effect (red eyes) - more intense for Terminator effect
            ai_glow = self.create_eye_glow(
                base_img, (255, 20, 20, 255)
            )  # Slightly orange-tinted red
            self.ai_glow_image = ImageTk.PhotoImage(ai_glow)

        except Exception as e:
            # Fallback to basic image
            try:
                self.base_logo_image = ImageTk.PhotoImage(
                    Image.open("assets/darvis-logo.png").convert("RGBA")
                )
            except Exception:
                self.base_logo_image = None

    def create_border_glow(self, image, glow_color, blur_radius=3, intensity=0.6):
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

        # Add glow around the edges - more intense and visible
        for x in range(glow_size):
            for y in range(glow_size):
                # Create glow on all edges for better visibility
                if x <= 2 or y <= 2 or x >= glow_size - 3 or y >= glow_size - 3:
                    # Calculate distance from edge for fade effect
                    edge_distance = min(x, y, glow_size - 1 - x, glow_size - 1 - y)
                    glow_alpha = min(255, int(255 * intensity * (edge_distance / 3.0)))
                    if glow_alpha > 0:
                        # Apply glow to all four corners of the canvas
                        border_glow.putpixel((x, y), glow_color[:3] + (glow_alpha,))
                        border_glow.putpixel(
                            (width + glow_size + x, y), glow_color[:3] + (glow_alpha,)
                        )
                        border_glow.putpixel(
                            (x, height + glow_size + y), glow_color[:3] + (glow_alpha,)
                        )
                        border_glow.putpixel(
                            (width + glow_size + x, height + glow_size + y),
                            glow_color[:3] + (glow_alpha,),
                        )

        # Apply gaussian blur to the glow
        border_glow = border_glow.filter(
            ImageFilter.GaussianBlur(radius=blur_radius / 2)
        )

        # Composite the original image over the glow
        result = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
        result.paste(border_glow, (0, 0), border_glow)
        result.paste(image, (glow_size, glow_size), image)

        return result

    def create_eye_glow(self, image, eye_color):
        """Create a dramatic red glow effect in the eyes of the face - Terminator style."""
        width, height = image.size
        eye_glow = image.copy()

        # Create eye glow regions (widely spaced for 2x image)
        eye_regions = [
            (
                width // 2 - 26,
                height // 3 - 8,
                width // 2 - 10,
                height // 3 + 8,
            ),  # Left eye - further apart
            (
                width // 2 + 10,
                height // 3 - 8,
                width // 2 + 26,
                height // 3 + 8,
            ),  # Right eye - further apart
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
                        # Create intense radial glow effect with brighter center
                        if distance <= 2:  # Very center - maximum brightness
                            alpha = max_alpha
                        elif distance <= 4:  # Near center - very bright
                            alpha = int(max_alpha * 0.9)
                        else:  # Outer glow - exponential falloff
                            alpha = int(
                                max_alpha
                                * (1 - (distance - 4) / (glow_radius - 4)) ** 0.7
                            )

                        if alpha > 0:
                            r, g, b, a = eye_glow.getpixel((x, y))
                            # More aggressive color blending for dramatic effect
                            blend_factor = alpha / 255.0
                            new_r = int(
                                eye_color[0] * blend_factor + r * (1 - blend_factor)
                            )
                            new_g = int(
                                eye_color[1] * blend_factor + g * (1 - blend_factor)
                            )
                            new_b = int(
                                eye_color[2] * blend_factor + b * (1 - blend_factor)
                            )
                            eye_glow.putpixel(
                                (x, y), (new_r, new_g, new_b, max(a, alpha))
                            )

        return eye_glow

    def setup_ui(self):
        """Set up the main UI components with modern styling."""
        # Modern dark theme colors
        self.colors = {
            'bg_primary': '#0f0f23',      # Deep dark blue
            'bg_secondary': '#1a1a2e',    # Dark blue-gray
            'bg_accent': '#16213e',       # Medium dark blue
            'text_primary': '#e0e0e0',    # Light gray
            'text_secondary': '#b0b0b0',  # Medium gray
            'text_accent': '#00d4ff',     # Cyan accent
            'border': '#2a2a4e',          # Subtle border
            'success': '#00ff88',         # Green success
            'warning': '#ffaa00',         # Orange warning
            'error': '#ff4444',           # Red error
            'glow_green': '#00ff88',      # Wake word glow
            'glow_red': '#ff6b6b',        # AI processing glow
        }

        self.root.configure(bg=self.colors['bg_primary'])

        # No header - title removed as requested

        # Information panel with modern styling (moved to top)
        info_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        info_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(15, 5))

        self.text_info = tk.Text(
            info_frame,
            height=12,
            font=('JetBrains Mono', 14),
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
            relief='flat',
            bd=2,
            padx=10,
            pady=10
        )
        self.text_info.pack(fill=tk.BOTH, expand=True)

        # Prevent navigation and editing in the text area
        self.text_info.bind('<Key>', lambda e: 'break')  # Block all keyboard input
        self.text_info.bind('<Button-1>', lambda e: 'break')  # Block mouse clicks
        self.text_info.bind('<Button-3>', lambda e: 'break')  # Block right clicks
        self.text_info.bind('<FocusIn>', lambda e: 'break')  # Prevent focus

        # Set up text tags for console coloring
        self._setup_text_tags()

    def _setup_text_tags(self):
        """Set up text tags for colored output in the console."""
        if self.text_info:
            # Define color tags for different message types
            self.text_info.tag_config("success", foreground=self.colors.get('success', 'green'))
            self.text_info.tag_config("warning", foreground=self.colors.get('warning', 'orange'))
            self.text_info.tag_config("error", foreground=self.colors.get('error', 'red'))
            self.text_info.tag_config("accent", foreground=self.colors.get('text_accent', 'cyan'))
            self.text_info.tag_config("muted", foreground=self.colors.get('text_secondary', 'gray'))
            # User bubble background color (matches input field)
            self.text_info.tag_config("user_bubble", background=self.colors.get('bg_accent', '#16213e'))

        # Manual input section with modern styling (moved below text field)
        input_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        input_frame.pack(fill=tk.X, padx=15, pady=5)

        self.manual_input_entry = tk.Entry(
            input_frame,
            font=('JetBrains Mono', 16),
            bg=self.colors['bg_accent'],  # Different color from text field
            fg=self.colors['text_primary'],
            insertbackground=self.colors['text_accent'],
            relief='flat',
            bd=2
        )
        self.manual_input_entry.pack(fill=tk.X, pady=(0, 5), ipady=6)
        self.manual_input_entry.bind("<Return>", lambda e: self.submit_manual_input())

        # Control buttons frame (below input field)
        control_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        control_frame.pack(fill=tk.X, padx=15, pady=(0, 5))

        # Listening mode toggle button
        self.listening_toggle = tk.Checkbutton(
            control_frame,
            text="🎤 Listening Mode",
            variable=self.listening_mode,
            command=self.toggle_listening_mode,
            font=('JetBrains Mono', 10),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_primary'],
            selectcolor=self.colors['bg_accent'],
            activeforeground=self.colors['text_accent'],
            activebackground=self.colors['bg_primary']
        )
        self.listening_toggle.pack(side=tk.LEFT)

        # Large logo at bottom with modern styling
        try:
            # Load and resize logo to 2x size
            base_img = Image.open("assets/darvis-logo.png").convert("RGBA")
            width, height = base_img.size
            large_img = base_img.resize((width * 2, height * 2), Image.Resampling.LANCZOS)

            # Create base image
            self.base_logo_image = ImageTk.PhotoImage(large_img)

            # Create glow effects for the resized image
            wake_glow_full = self.create_eye_glow(large_img, (0, 255, 0, 255))  # Green eyes
            self.wake_glow_image = ImageTk.PhotoImage(wake_glow_full)

            ai_glow_full = self.create_eye_glow(large_img, (255, 20, 20, 255))  # Red eyes
            self.ai_glow_image = ImageTk.PhotoImage(ai_glow_full)

            # Semi-bright glow for pulsing (lower intensity but still visible)
            wake_glow_dim = self.create_eye_glow(large_img, (0, 150, 0, 150))  # Semi-bright green
            self.wake_glow_dim_image = ImageTk.PhotoImage(wake_glow_dim)

            ai_glow_dim = self.create_eye_glow(large_img, (150, 20, 20, 150))  # Semi-bright red
            self.ai_glow_dim_image = ImageTk.PhotoImage(ai_glow_dim)

            # Success - create the UI elements
            # Create a bottom section frame for logo, timer, and cancel button
            bottom_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
            bottom_frame.pack(side=tk.BOTTOM, pady=10)

            # Logo in the bottom frame
            self.logo_label = tk.Label(
                bottom_frame, image=self.base_logo_image, bg=self.colors['bg_primary']
            )
            self.logo_label.pack(pady=(0, 10))

            # Timer below logo
            self.timer_label = tk.Label(
                bottom_frame,
                text="",
                font=('JetBrains Mono', 18, 'bold'),
                bg=self.colors['bg_primary'],
                fg=self.colors['text_accent'],
            )
            self.timer_label.pack(pady=(0, 10))

            # Cancel button below timer
            self.cancel_button = tk.Button(
                bottom_frame,
                text="Cancel AI Request",
                font=('JetBrains Mono', 10),
                bg=self.colors['error'],
                fg='black',  # Dark text for better contrast on red button
                relief='raised',
                bd=2,
                padx=10,
                pady=5,
                state='disabled',  # Initially disabled
                command=self.cancel_ai_request
            )
            self.cancel_button.pack()

        except Exception as e:
            print(f"Image loading failed: {e}")
            # Modern emoji fallback with proper layout
            bottom_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
            bottom_frame.pack(side=tk.BOTTOM, pady=10)

            # Create ASCII art logo as fallback
            darvis_logo = """\
╔══════════════════════════════════╗
║              DARVIS              ║
║          Voice Assistant         ║
║                                  ║
║           [●]  [●]              ║
║            \\____/               ║
║                                  ║
║  🤖 Advanced AI • Voice Control  ║
╚══════════════════════════════════╝"""

            self.logo_label = tk.Label(
                bottom_frame,
                text=darvis_logo,
                font=('JetBrains Mono', 8),
                bg=self.colors['bg_primary'],
                fg=self.colors['text_accent'],
                justify=tk.CENTER,
            )
            self.logo_label.pack(pady=(0, 10))

            # Timer below logo
            self.timer_label = tk.Label(
                bottom_frame,
                text="",
                font=('JetBrains Mono', 18, 'bold'),
                bg=self.colors['bg_primary'],
                fg=self.colors['text_accent'],
            )
            self.timer_label.pack(pady=(0, 10))

            # Cancel button below timer
            self.cancel_button = tk.Button(
                bottom_frame,
                text="Cancel AI Request",
                font=('JetBrains Mono', 10),
                bg=self.colors['error'],
                fg='white',
                relief='raised',
                bd=2,
                padx=10,
                pady=5,
                state='disabled',
                command=self.cancel_ai_request
            )
            self.cancel_button.pack()

            # Add timer label above logo
            self.timer_label = tk.Label(
                self.root,
                text="",
                font=('JetBrains Mono', 18, 'bold'),
                bg=self.colors['bg_primary'],
                fg=self.colors['text_accent'],
            )
            self.timer_label.pack(side=tk.BOTTOM, pady=10)

            # Cancel AI button
            self.cancel_button = tk.Button(
                self.root,
                text="Cancel AI Request",
                font=('JetBrains Mono', 10),
                bg=self.colors['error'],
                fg='white',
                relief='raised',
                bd=2,
                padx=10,
                pady=5,
                state='disabled',  # Initially disabled
                command=self.cancel_ai_request
            )
            self.cancel_button.pack(side=tk.BOTTOM, pady=5)
        except Exception as e:
            # Modern emoji fallback
            self.logo_label = tk.Label(
                self.root,
                text="🤖",
                font=('JetBrains Mono', 48),
                bg=self.colors['bg_primary'],
                fg=self.colors['text_accent'],
            )
            self.logo_label.pack(side=tk.BOTTOM, pady=15)

            self.timer_label = tk.Label(
                self.root,
                text="",
                font=('JetBrains Mono', 18, 'bold'),
                bg=self.colors['bg_primary'],
                fg=self.colors['text_accent'],
            )
            self.timer_label.pack(side=tk.BOTTOM, pady=10)

        # Initialize info text (no default message - controlled by listening toggle)

    def start_voice_processing(self):
        """Start the voice recognition processing thread."""
        import threading

        voice_thread = threading.Thread(target=self.listen_loop, daemon=True)
        voice_thread.start()

    def listen_loop(self):
        """Main voice processing loop - continuously listen for speech when enabled."""
        while True:
            try:
                # Only listen if listening mode is enabled
                if not self.listening_mode.get():
                    import time
                    time.sleep(0.1)  # Small delay to prevent busy waiting
                    continue

                text = listen()
                if text:
                    text_lower = text.lower()
                    activated = any(wake in text_lower for wake in self.wake_words)
                    if activated:
                        # Trigger wake word glow
                        self.msg_queue.put({"type": "wake_word_detected"})

                        # Extract command from wake word phrase (e.g., "hey darvis open youtube" -> "open youtube")
                        command = None
                        for wake in self.wake_words:
                            if wake in text_lower:
                                # Remove wake word and extract command
                                command_part = text_lower.replace(wake, "", 1).strip()
                                if command_part:
                                    command = command_part
                                break

                        if command:
                            # Wake word + command in one utterance
                            self.display_message("Darvis heard you - What's up?\n")
                            speak("Darvis heard you - What's up?")
                            self.start_countdown_timer(seconds=8, color="green")
                            self.process_command(command, "voice")
                            self.msg_queue.put({"type": "wake_word_end"})
                        else:
                            # Just wake word - listen for separate command
                            listening_for_command = True
                            self.manual_activate()
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
        self.display_message("Darvis heard you - What's up?\n")
        # Speak in background thread to avoid blocking
        import threading
        speak_thread = threading.Thread(target=lambda: speak("Darvis heard you - What's up?"), daemon=True)
        speak_thread.start()

        # Start countdown timer for command input
        self.start_countdown_timer(seconds=8, color="green")

        # Listen for the actual command
        command = listen()
        if command:
            self.process_command(command, "voice")
        else:
            # No command heard, stop timer
            self.stop_timer()

    def process_ai_command(self, command: str):
        """Process a command using AI assistance asynchronously."""
        # Start visual indicators immediately
        self.glow_logo(True, True)  # Red glow for AI
        update_waybar_status("thinking", f"Thinking about: {command[:30]}...")

        # Enable cancel button
        if hasattr(self, 'cancel_button'):
            self.cancel_button.config(state='normal')

        # Start count-up timer for AI processing
        self.start_countup_timer(color="red")

        def ai_processing_thread():
            try:
                response, session_id = process_ai_query(command)
                update_waybar_status("speaking", "Speaking response...")

                # Schedule UI updates back to main thread
                self.root.after(0, lambda: self.display_message(f"AI Response: {response}\n"))

                # Speak in background thread
                import threading
                speak_thread = threading.Thread(target=lambda: speak(response), daemon=True)
                speak_thread.start()
                update_waybar_status("success", "Response delivered")
            except Exception as e:
                error_msg = str(e)
                if "opencode" in error_msg.lower():
                    self.root.after(0, lambda: self.display_message("AI assistance not available (opencode not found)\n"))
                    update_waybar_status("error", "AI not available")
                else:
                    self.root.after(0, lambda: self.display_message(f"AI error: {error_msg}\n"))
                    update_waybar_status("error", f"AI error: {error_msg[:50]}")
            finally:
                # Stop indicators back on main thread
                self.root.after(0, lambda: self._cleanup_ai_indicators())

        # Start AI processing in background thread
        import threading
        ai_thread = threading.Thread(target=ai_processing_thread, daemon=True)
        ai_thread.start()

    def _cleanup_ai_indicators(self):
        """Clean up AI processing indicators."""
        if hasattr(self, 'cancel_button'):
            self.cancel_button.config(state='disabled')
        self.stop_timer()
        self.root.after(1000, lambda: self.glow_logo(False, False))  # Stop red glow

    def start_message_processing(self):
        """Start processing messages from the queue."""
        import threading

        gui_thread = threading.Thread(target=self.update_gui, daemon=True)
        gui_thread.start()

    def update_gui(self):
        """Process messages from the queue and update consolidated info panel."""
        try:
            msg = self.msg_queue.get_nowait()
            if msg["type"] == "insert":
                # Add spacing for new interactions
                if "Darvis heard you - What's up?" in msg["text"]:
                    self._insert_colored_text("\n" + "─" * 60 + "\n\n", "muted")

                # Route all messages to create proper chat bubbles
                if msg["text"].startswith("Darvis heard:"):
                    # Voice input - right-aligned green bubble
                    clean_text = msg["text"].replace("Darvis heard: ", "", 1)
                    self._insert_chat_bubble(clean_text, "success", "right")
                elif (
                    "AI assistance not available" in msg["text"]
                    or "AI error:" in msg["text"]
                ):
                    # Error messages - center-aligned red bubble
                    self._insert_chat_bubble(msg["text"], "error", "center")
                elif msg["text"].startswith("AI Response:"):
                    # AI responses - left-aligned blue bubble
                    clean_text = msg["text"].replace("AI Response: ", "", 1)
                    self._insert_chat_bubble(clean_text, "accent", "left")
                elif len(msg["text"].strip()) > 0 and not any(prefix in msg["text"] for prefix in ["Darvis heard:", "AI Response:", "Darvis is", "AI assistance not available", "AI error:"]):
                    # User input (messages without special prefixes) - right-aligned bubble with input field color
                    clean_text = msg["text"].strip()
                    self._insert_chat_bubble(clean_text, "user_bubble", "right")
                elif "Darvis heard you - What's up?" in msg["text"]:
                    # Activation message - center-aligned
                    self._insert_chat_bubble(msg["text"], "warning", "center")
                elif "Darvis is Listening" in msg["text"] or "Darvis is not listening" in msg["text"]:
                    # Listening status - center-aligned
                    self._insert_chat_bubble(msg["text"], "muted", "center")
                else:
                    # Other messages - left-aligned default
                    self._insert_colored_text(f"{msg['text']}\n")
            elif msg["type"] == "wake_word_detected":
                # Glow logo when wake word is detected
                self.glow_logo(True)
            elif msg["type"] == "wake_word_end":
                self.root.after(1000, lambda: self.glow_logo(False, False))
        except queue.Empty:
            pass
        except Exception as e:
            # Log any errors but don't crash the message processing loop
            print(f"Error processing message: {e}")
            import traceback
            traceback.print_exc()
        # Schedule next check
        self.root.after(100, self.update_gui)

    def _insert_chat_bubble(self, text, tag=None, align="left"):
        """Insert a proper chat bubble with rounded borders and background colors."""
        if self.text_info:
            # Enable text widget for insertion
            self.text_info.config(state='normal')

            # Initialize bubble background tags if not already done
            if not hasattr(self, '_bubble_tags_created'):
                # User bubbles (right side) - lighter background
                self.text_info.tag_config("user_bubble_bg", background="#007AFF", foreground="white")
                # AI bubbles (left side) - darker background
                self.text_info.tag_config("ai_bubble_bg", background="#E5E5EA", foreground="#1C1C1E")
                # System bubbles (center) - neutral background
                self.text_info.tag_config("system_bubble_bg", background="#F2F2F7", foreground="#3C3C43")
                self._bubble_tags_created = True

            lines = text.split('\n')
            max_len = max(len(line) for line in lines) if lines else 0

            # Create bubble styling based on alignment
            if align == "right":
                # Right-aligned user bubble (like iOS Messages - blue)
                padding = max(0, 30 - max_len)

                # Top of bubble
                top_line = f"{' ' * (padding - 1)}╭{'─' * (max_len + 2)}╮\n"
                self.text_info.insert(tk.END, top_line)

                # Content lines
                for line in lines:
                    if line.strip():
                        content_line = f"{' ' * (padding - 1)}│ {line} │\n"
                        start_pos = self.text_info.index(tk.END + "-1c")
                        self.text_info.insert(tk.END, content_line)
                        end_pos = self.text_info.index(tk.END + "-1c")

                        # Apply user bubble styling
                        self.text_info.tag_add("user_bubble_bg", start_pos, end_pos)
                        if tag:
                            self.text_info.tag_add(tag, start_pos, end_pos)

                # Bottom of bubble
                bottom_line = f"{' ' * (padding - 1)}╰{'─' * (max_len + 2)}╯\n"
                self.text_info.insert(tk.END, bottom_line)

            elif align == "center":
                # Center-aligned system bubble
                center_padding = max(0, 20 - max_len // 2)

                # Top of bubble
                top_line = f"{' ' * center_padding}╭{'─' * (max_len + 2)}╮\n"
                self.text_info.insert(tk.END, top_line)

                # Content lines
                for line in lines:
                    if line.strip():
                        content_line = f"{' ' * center_padding}│ {line} │\n"
                        start_pos = self.text_info.index(tk.END + "-1c")
                        self.text_info.insert(tk.END, content_line)
                        end_pos = self.text_info.index(tk.END + "-1c")

                        # Apply system bubble styling
                        self.text_info.tag_add("system_bubble_bg", start_pos, end_pos)
                        if tag:
                            self.text_info.tag_add(tag, start_pos, end_pos)

                # Bottom of bubble
                bottom_line = f"{' ' * center_padding}╰{'─' * (max_len + 2)}╯\n"
                self.text_info.insert(tk.END, bottom_line)

            else:  # left
                # Left-aligned AI bubble (like ChatGPT - light gray)
                # Top of bubble
                top_line = f"╭{'─' * (max_len + 2)}╮\n"
                self.text_info.insert(tk.END, top_line)

                # Content lines
                for line in lines:
                    if line.strip():
                        content_line = f"│ {line} │\n"
                        start_pos = self.text_info.index(tk.END + "-1c")
                        self.text_info.insert(tk.END, content_line)
                        end_pos = self.text_info.index(tk.END + "-1c")

                        # Apply AI bubble styling
                        self.text_info.tag_add("ai_bubble_bg", start_pos, end_pos)
                        if tag:
                            self.text_info.tag_add(tag, start_pos, end_pos)

                # Bottom of bubble
                bottom_line = f"╰{'─' * (max_len + 2)}╯\n"
                self.text_info.insert(tk.END, bottom_line)

            # Add spacing between bubbles
            self.text_info.insert(tk.END, "\n")

            # Disable text widget again
            self.text_info.config(state='disabled')

            # Scroll to bottom
            self.text_info.see(tk.END)

    def _insert_colored_text(self, text, tag=None):
        """Insert colored text into the console with chronological flow."""
        if self.text_info:
            # Enable text widget for insertion
            self.text_info.config(state='normal')

            # Insert at end for chronological order (oldest to newest)
            start_pos = self.text_info.index(tk.END + "-1c")
            self.text_info.insert(tk.END, text)
            end_pos = self.text_info.index(tk.END + "-1c")

            # Apply color tag if specified
            if tag:
                self.text_info.tag_add(tag, start_pos, end_pos)

            # Apply user bubble background if this is a user message with bubble
            if "user_bubble" in (tag or ""):
                self.text_info.tag_add("user_bubble", start_pos, end_pos)

            # Disable text widget again to make it read-only
            self.text_info.config(state='disabled')

            # Scroll to bottom to show latest messages
            self.text_info.see(tk.END)

    def bind_events(self):
        """Bind UI events for interactive elements."""
        # Keyboard shortcuts for quitting
        self.root.bind('<Control-q>', lambda e: self.quit_app())
        self.root.bind('<Control-w>', lambda e: self.quit_app())

        # Glow effects for manual input
        # No text box animations needed anymore

    def glow_logo(self, enable_glow, ai_active=False):
        """Add or remove sophisticated glow effect from logo with pulsing animation."""
        try:
            if not hasattr(self, "logo_label") or not self.logo_label:
                return

            if enable_glow:
                # Initialize pulsing state if not exists
                if not hasattr(self, 'pulse_state'):
                    self.pulse_state = True
                    self.pulse_callback = None

                if ai_active and self.ai_glow_image:
                    # Red eye glow for AI processing with pulsing
                    self.current_logo_state = "ai"
                    self._start_pulsing(ai_active=True)
                elif self.wake_glow_image:
                    # Green eye glow for wake word with pulsing
                    self.current_logo_state = "wake"
                    self._start_pulsing(ai_active=False)
            else:
                # Stop pulsing and return to normal state
                self._stop_pulsing()
                if self.base_logo_image:
                    self.logo_label.config(image=self.base_logo_image)
                    self.logo_label.image = self.base_logo_image  # Keep reference
                self.current_logo_state = "normal"
        except Exception as e:
            print(f"Error in glow_logo: {e}")

    def _start_pulsing(self, ai_active=False):
        """Start the pulsing glow animation."""
        self._stop_pulsing()  # Stop any existing pulsing

        def pulse_step():
            if self.current_logo_state in ["wake", "ai"]:
                # Alternate between bright and dim glow (no disappearing)
                if self.pulse_state:
                    # Bright glow
                    if ai_active and self.ai_glow_image:
                        self.logo_label.config(image=self.ai_glow_image)
                        self.logo_label.image = self.ai_glow_image
                    elif self.wake_glow_image:
                        self.logo_label.config(image=self.wake_glow_image)
                        self.logo_label.image = self.wake_glow_image
                else:
                    # Dim glow (still glowing, just less bright)
                    if ai_active and hasattr(self, 'ai_glow_dim_image'):
                        self.logo_label.config(image=self.ai_glow_dim_image)
                        self.logo_label.image = self.ai_glow_dim_image
                    elif hasattr(self, 'wake_glow_dim_image'):
                        self.logo_label.config(image=self.wake_glow_dim_image)
                        self.logo_label.image = self.wake_glow_dim_image

                # Toggle pulse state and schedule next pulse
                self.pulse_state = not self.pulse_state
                self.pulse_callback = self.root.after(500, pulse_step)  # 0.5 second interval

        # Start pulsing
        pulse_step()

    def _stop_pulsing(self):
        """Stop the pulsing animation."""
        if hasattr(self, 'pulse_callback') and self.pulse_callback:
            self.root.after_cancel(self.pulse_callback)
            self.pulse_callback = None

    def cancel_ai_request(self):
        """Cancel the current AI request."""
        from .ai import cancel_ai_request
        if cancel_ai_request():
            self.display_message("AI request cancelled by user.\n")
            # Reset UI state
            self.stop_timer()
            self.glow_logo(False)
            if hasattr(self, 'cancel_button'):
                self.cancel_button.config(state='disabled')
        else:
            self.display_message("No active AI request to cancel.\n")

    def submit_manual_input(self):
        """Process manual text input from the GUI input field."""
        input_text = self.manual_input_entry.get().strip()
        if input_text:
            # Show immediate feedback that input was received
            self.display_message(f"{input_text}\n")

            # Clear the input field immediately
            self.manual_input_entry.delete(0, tk.END)

            # Change text color to green briefly to show submission
            self.manual_input_entry.config(fg="green")
            self.root.after(500, lambda: self.manual_input_entry.config(fg="white"))

            # Intelligent command processing
            self.process_command(input_text, "manual")

    def process_command(self, command: str, source: str):
        """Process a command with intelligent AI fallback."""
        # Stop countdown timer since command was received
        self.stop_timer()

        command_lower = command.lower()

        # Check if it's a local command first
        if command_lower.startswith("open "):
            # Handle open commands locally
            app = command_lower.split("open")[-1].strip()
            response = open_app(app)
            self.display_message(f"Response: {response}\n")
            # Speak in background thread to avoid blocking GUI
            import threading
            speak_thread = threading.Thread(target=lambda: speak(response), daemon=True)
            speak_thread.start()
        else:
            # Check if it looks like a command we can handle locally
            local_commands = ["calculator", "terminal", "editor", "browser"]
            if any(cmd in command_lower for cmd in local_commands):
                # Try to handle as local command
                app = command_lower  # Pass the full input to open_app
                response = open_app(app)
                if "not installed" in response or "not found" in response:
                    # Fall back to AI
                    self.process_ai_command(command)
                else:
                    self.display_message(f"Response: {response}\n")
                    # Speak in background thread to avoid blocking GUI
                    import threading
                    speak_thread = threading.Thread(target=lambda: speak(response), daemon=True)
                    speak_thread.start()
            else:
                # Default to AI for unrecognized inputs
                self.process_ai_command(command)

    def display_message(self, message: str):
        """Display a message by adding it to the message queue."""
        # Put the message in the queue for the GUI thread to handle
        self.msg_queue.put({"type": "insert", "text": message})

    def run(self):
        """Start the GUI event loop."""
        self.root.mainloop()

    def setup_system_tray(self):
        """Set up the system tray icon."""
        if not HAS_PYSTRAY:
            print("System tray not available - pystray not installed")
            return

        # Check if we have a display and system tray
        if not os.environ.get("DISPLAY"):
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
                pystray.MenuItem(
                    "Voice Commands",
                    pystray.Menu(
                        pystray.MenuItem(
                            "Say 'hey darvis'", lambda: None, enabled=False
                        ),
                        pystray.MenuItem(
                            "Say 'open calculator'", lambda: None, enabled=False
                        ),
                        pystray.MenuItem(
                            "Say 'what is 2+2'", lambda: None, enabled=False
                        ),
                    ),
                ),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("About", self.show_about),
                pystray.MenuItem("Quit", self.quit_app),
            )

            # Create the tray icon
            self.tray_icon = pystray.Icon(
                "darvis", icon_image, "Darvis Voice Assistant", menu
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
        if self.root.state() == "withdrawn":
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
