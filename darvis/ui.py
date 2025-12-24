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

        # Modern dark theme color palette
        self.colors = {
            'bg_primary': '#0f0f23',      # Deep dark blue-black
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
        self.root.option_add('*Font', ('JetBrains Mono', 10))  # Modern monospace font

    def _setup_text_tags(self):
        """Set up text tags for colored output in the console."""
        # This will be called after text_info is created
        pass

    # Remove header section - going for cleaner look

    def _create_input_section(self, parent):
        """Create the input section with modern styling."""
        input_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        input_frame.pack(fill=tk.X, pady=(0, 15))

        # Input label
        input_label = tk.Label(
            input_frame,
            text="💬 Command Input:",
            font=('JetBrains Mono', 11, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_primary']
        )
        input_label.pack(anchor=tk.W, padx=5, pady=(0, 5))

        # Modern styled entry
        self.manual_input_entry = tk.Entry(
            input_frame,
            font=('JetBrains Mono', 12),
            bg=self.colors['bg_accent'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['text_accent'],
            relief='flat',
            bd=0,
            highlightthickness=2,
            highlightcolor=self.colors['border'],
            highlightbackground=self.colors['border']
        )
        self.manual_input_entry.pack(fill=tk.X, padx=5, pady=(0, 5), ipady=8)
        self.manual_input_entry.bind("<Return>", lambda e: self.submit_manual_input())

    def _create_console_section(self, parent):
        """Create the console/output section."""
        console_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        console_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Console label
        console_label = tk.Label(
            console_frame,
            text="📊 Console Output:",
            font=('JetBrains Mono', 11, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_primary']
        )
        console_label.pack(anchor=tk.W, padx=5, pady=(0, 5))

        # Modern styled text widget
        self.text_info = tk.Text(
            console_frame,
            height=12,
            font=('JetBrains Mono', 10),
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
            relief='flat',
            bd=0,
            highlightthickness=2,
            highlightcolor=self.colors['border'],
            highlightbackground=self.colors['border'],
            wrap=tk.WORD,
            padx=10,
            pady=10
        )
        self.text_info.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        # Set up text tags for colored output
        self._setup_text_tags()

    def _create_status_section(self, parent):
        """Create the status and visual feedback section."""
        status_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        status_frame.pack(fill=tk.X)

        # Timer display
        self.timer_label = tk.Label(
            status_frame,
            text="",
            font=('JetBrains Mono', 18, 'bold'),
            fg=self.colors['text_accent'],
            bg=self.colors['bg_primary']
        )
        self.timer_label.pack(side=tk.TOP, pady=(0, 10))

        # Logo section
        try:
            self.load_logo_images()
            if self.base_logo_image:
                self.logo_label = tk.Label(
                    status_frame, image=self.base_logo_image, bg=self.colors['bg_primary']
                )
                self.logo_label.pack(side=tk.BOTTOM, pady=5)
            else:
                raise Exception("Logo images failed to load")
        except Exception:
            # Modern fallback text logo
            self.logo_label = tk.Label(
                status_frame,
                text="🤖\nDARVIS",
                font=('JetBrains Mono', 24, 'bold'),
                fg=self.colors['text_accent'],
                bg=self.colors['bg_primary']
            )
            self.logo_label.pack(side=tk.BOTTOM, pady=5)

    def _setup_text_tags(self):
        """Set up text tags for colored output in the console."""
        if self.text_info:
            # Define color tags for different message types
            self.text_info.tag_config("success", foreground=self.colors['success'])
            self.text_info.tag_config("warning", foreground=self.colors['warning'])
            self.text_info.tag_config("error", foreground=self.colors['error'])
            self.text_info.tag_config("accent", foreground=self.colors['text_accent'])
            self.text_info.tag_config("muted", foreground=self.colors['text_secondary'])
            self.text_info.tag_config("header", foreground=self.colors['text_primary'], font=('JetBrains Mono', 10, 'bold'))

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
        # Modern window sizing
        window_width = 700
        window_height = 500

        # Center the window on the screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Modern window appearance
        self.root.resizable(True, True)
        self.root.minsize(600, 400)

        # Make window visible and focused
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

        # Handle window close button (X) - quit application instead of minimize to tray
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

    def show_about(self):
        """Show about dialog."""
        about_text = """🤖 DARVIS VOICE ASSISTANT v2.0

A modern, cross-platform voice assistant with intelligent command processing and sleek UI design.

✨ Features:
• 🎤 Voice wake word detection ("hey darvis")
• 🧠 AI-powered responses via opencode
• 🎨 Modern dark theme with visual effects
• 📱 System tray integration
• 📊 Waybar status support
• 🚀 Smart app detection & launching
• 🌐 21+ web services supported
• 💻 30+ local applications

🎯 Commands:
• "open slack" → Opens Slack in browser
• "open bluetooth manager" → Launches system settings
• "what is the weather?" → AI response

Built with ❤️ using Python & Tkinter"""
        self.display_message(f"\n{about_text}\n", "header")

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

        # Create eye glow regions (closer together for perfect alignment)
        eye_regions = [
            (
                width // 2 - 17,
                height // 3 - 8,
                width // 2 - 2,
                height // 3 + 8,
            ),  # Left eye - even closer
            (
                width // 2 + 2,
                height // 3 - 8,
                width // 2 + 17,
                height // 3 + 8,
            ),  # Right eye - even closer
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
        """Set up the conversational AI assistant UI."""
        # Initialize speech bubble states
        self.speech_bubble_text = ""
        self.speech_bubble_state = "listening"  # listening, awake, processing, speaking
        self.help_messages = [
            "How can I help you?",
            "What can I do for you?",
            "I'm here to assist!",
            "What would you like me to do?",
            "Ready for your command!",
            "How may I assist you?",
            "What do you need?",
            "I'm listening...",
            "Tell me what you need!",
            "I'm ready to help!"
        ]

        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Large Darvis image at top
        self._create_darvis_image_section(main_frame)

        # Speech bubble in middle
        self._create_speech_bubble_section(main_frame)

        # Input field at bottom
        self._create_bottom_input_section(main_frame)

        # Set initial speech bubble
        self.update_speech_bubble("I'm listening...", "listening")

    def _create_darvis_image_section(self, parent):
        """Create the large Darvis image section at the top."""
        image_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        image_frame.pack(pady=(0, 20))

        try:
            # Load and resize logo to 2x size
            base_img = Image.open("assets/darvis-logo.png").convert("RGBA")
            width, height = base_img.size
            large_img = base_img.resize((width * 2, height * 2), Image.Resampling.LANCZOS)
            self.large_logo_image = ImageTk.PhotoImage(large_img)

            self.logo_label = tk.Label(
                image_frame, image=self.large_logo_image, bg=self.colors['bg_primary']
            )
        except Exception:
            # Large emoji fallback
            self.logo_label = tk.Label(
                image_frame,
                text="🤖",
                font=('JetBrains Mono', 72),
                fg=self.colors['text_accent'],
                bg=self.colors['bg_primary']
            )

        self.logo_label.pack()

    def _create_speech_bubble_section(self, parent):
        """Create the speech bubble section in the middle."""
        bubble_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        bubble_frame.pack(pady=(0, 20))

        # Speech bubble container
        self.speech_bubble = tk.Label(
            bubble_frame,
            text="",
            font=('JetBrains Mono', 14),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_accent'],
            relief='raised',
            bd=2,
            padx=20,
            pady=15,
            wraplength=400
        )
        self.speech_bubble.pack()

        # Add a pointer/tail to make it look like a speech bubble
        pointer_label = tk.Label(
            bubble_frame,
            text="▼",
            font=('JetBrains Mono', 16),
            fg=self.colors['bg_accent'],
            bg=self.colors['bg_primary']
        )
        pointer_label.pack(pady=(0, 10))

    def _create_bottom_input_section(self, parent):
        """Create the input section at the bottom."""
        input_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        input_frame.pack(fill=tk.X, pady=(20, 0))

        # Input label
        input_label = tk.Label(
            input_frame,
            text="💬 Type your command:",
            font=('JetBrains Mono', 11, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_primary']
        )
        input_label.pack(anchor=tk.W, padx=5, pady=(0, 5))

        # Modern styled entry
        self.manual_input_entry = tk.Entry(
            input_frame,
            font=('JetBrains Mono', 12),
            bg=self.colors['bg_accent'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['text_accent'],
            relief='flat',
            bd=0,
            highlightthickness=2,
            highlightcolor=self.colors['border'],
            highlightbackground=self.colors['border']
        )
        self.manual_input_entry.pack(fill=tk.X, padx=5, pady=(0, 5), ipady=8)
        self.manual_input_entry.bind("<Return>", lambda e: self.submit_manual_input())

    def update_speech_bubble(self, text, state="normal"):
        """Update the speech bubble with new text and styling."""
        if self.speech_bubble:
            self.speech_bubble_text = text
            self.speech_bubble_state = state

            # Color based on state
            if state == "listening":
                bg_color = self.colors['bg_secondary']
                fg_color = self.colors['text_secondary']
            elif state == "awake":
                bg_color = self.colors['success']  # Green for awake
                fg_color = self.colors['bg_primary']
            elif state == "processing":
                bg_color = self.colors['warning']  # Orange for processing
                fg_color = self.colors['bg_primary']
            elif state == "speaking":
                bg_color = self.colors['text_accent']  # Cyan for speaking
                fg_color = self.colors['bg_primary']
            else:
                bg_color = self.colors['bg_accent']
                fg_color = self.colors['text_primary']

            self.speech_bubble.config(text=text, bg=bg_color, fg=fg_color)

        # Logo centered at bottom with enhanced visual effects
        try:
            self.load_logo_images()
            if self.base_logo_image:
                self.logo_label = tk.Label(
                    self.root, image=self.base_logo_image, bg="black"
                )
                self.logo_label.pack(side=tk.BOTTOM, pady=10)

                # Add timer label above logo (but still below text area)
                self.timer_label = tk.Label(
                    self.root,
                    text="",
                    font=("Arial", FONT_SIZE_LARGE, "bold"),
                    bg="black",
                    fg="white",
                )
                self.timer_label.pack(side=tk.BOTTOM, pady=5)
            else:
                raise Exception("Logo images failed to load")
        except Exception as e:
            # Fallback if image fails to load
            self.logo_label = tk.Label(
                self.root,
                text="DARVIS",
                font=("Arial", FONT_SIZE_LARGE),
                bg="black",
                fg="white",
            )
            self.logo_label.pack(side=tk.BOTTOM, pady=20)

        # Speech bubble is already initialized to "I'm listening..."

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
                            import random
                            help_msg = random.choice(self.help_messages)
                            self.update_speech_bubble(help_msg, "awake")
                            speak("Activated!")
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
        import random
        help_msg = random.choice(self.help_messages)
        self.update_speech_bubble(help_msg, "awake")
        speak("Activated!")

        # Start countdown timer for command input
        self.start_countdown_timer(seconds=8, color="green")

        # Listen for the actual command
        command = listen()
        if command:
            self.process_command(command, "voice")
        else:
            # No command heard, stop timer and return to listening
            self.stop_timer()
            self.update_speech_bubble("I'm listening...", "listening")

    def process_ai_command(self, command: str):
        """Process a command using AI assistance."""
        self.glow_logo(True, True)  # Red glow for AI
        update_waybar_status("thinking", f"Thinking about: {command[:30]}...")

        # Start count-up timer for AI processing
        self.start_countup_timer(color="red")

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
                self.display_message(
                    "AI assistance not available (opencode not found)\n"
                )
                update_waybar_status("error", "AI not available")
            else:
                self.display_message(f"AI error: {error_msg}\n")
                update_waybar_status("error", f"AI error: {error_msg[:50]}")
        finally:
            # Stop timer and glow after processing
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
                # Handle speech bubble updates instead of text output
                text = msg["text"]

                # Determine speech bubble state and content
                if "Darvis heard:" in text:
                    # Voice input detected - stay in current state
                    pass
                elif "Activated!" in text:
                    # Wake word detected - switch to awake state with random help message
                    import random
                    help_msg = random.choice(self.help_messages)
                    self.update_speech_bubble(help_msg, "awake")
                elif "Using AI assistance" in text or "AI Query:" in text:
                    # AI processing started
                    self.update_speech_bubble("Thinking...", "processing")
                elif "AI Response:" in text:
                    # AI response ready
                    response_text = text.replace("AI Response:", "").strip()
                    self.update_speech_bubble(response_text, "speaking")
                elif "Command:" in text:
                    # Local command executed
                    cmd_text = text.replace("Command:", "").strip()
                    self.update_speech_bubble(f"Opening {cmd_text}...", "speaking")
                elif "not installed" in text:
                    # App not found
                    self.update_speech_bubble("I couldn't find that application.", "error")
                else:
                    # Other messages - use as speech bubble if it's a user-visible message
                    if not text.startswith("LOG:") and text.strip():
                        self.update_speech_bubble(text.strip(), "speaking")
            elif msg["type"] == "wake_word_detected":
                # Glow logo when wake word is detected
                self.glow_logo(True)
            elif msg["type"] == "wake_word_end":
                self.root.after(1000, lambda: self.glow_logo(False))
        except queue.Empty:
            pass
        # Schedule next check
        self.root.after(100, self.update_gui)

    def _insert_colored_text(self, text, tag=None):
        """Insert colored text into the console."""
        if self.text_info:
            # Insert text
            start_pos = self.text_info.index(tk.END + "-1c")
            self.text_info.insert(tk.END, text)
            end_pos = self.text_info.index(tk.END + "-1c")

            # Apply color tag if specified
            if tag:
                self.text_info.tag_add(tag, start_pos, end_pos)

            # Auto-scroll to bottom
            self.text_info.see(tk.END)

    def bind_events(self):
        """Bind UI events for interactive elements."""
        # Keyboard shortcuts
        self.root.bind('<Control-q>', lambda e: self.quit_app())
        self.root.bind('<Control-w>', lambda e: self.quit_app())

        # Glow effects for manual input
        # No text box animations needed anymore

    def glow_logo(self, enable_glow, ai_active=False):
        """Add or remove sophisticated glow effect from logo."""
        try:
            if not hasattr(self, "logo_label") or not self.logo_label:
                return

            if enable_glow:
                if ai_active and self.ai_glow_image:
                    # Red eye glow for AI processing
                    self.logo_label.config(image=self.ai_glow_image)
                    self.logo_label.image = self.ai_glow_image  # Keep reference
                    self.current_logo_state = "ai"
                elif self.wake_glow_image:
                    # Green eye glow for wake word
                    self.logo_label.config(image=self.wake_glow_image)
                    self.logo_label.image = self.wake_glow_image  # Keep reference
                    self.current_logo_state = "wake"
            else:
                # Return to normal state
                if self.base_logo_image:
                    self.logo_label.config(image=self.base_logo_image)
                    self.logo_label.image = self.base_logo_image  # Keep reference
                self.current_logo_state = "normal"
                # Stop any active timer when returning to normal state
                self.stop_timer()
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
        # Stop countdown timer since command was received
        self.stop_timer()

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
                    self.display_message(
                        f"Local command failed, using AI assistance...\nAI Query: {command}\n"
                    )
                    self.process_ai_command(command)
                else:
                    self.display_message(f"Command: {command}\n{response}\n")
                    speak(response)
            else:
                # Default to AI for unrecognized inputs
                self.display_message(f"Using AI assistance...\nAI Query: {command}\n")
                self.process_ai_command(command)

    def display_message(self, message: str, tag: str = None):
        """Display a message by adding it to the message queue."""
        # Put the message in the queue for the GUI thread to handle
        self.msg_queue.put({"type": "insert", "text": message, "tag": tag})

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
