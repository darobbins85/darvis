"""
Configuration and constants for Darvis Voice Assistant.
"""

import os
import platform
from pathlib import Path

# Suppress ALSA warnings for cleaner output (Linux only)
if platform.system().lower() == "linux":
    os.environ["ALSA_LOG_LEVEL"] = "0"


def is_linux() -> bool:
    """Check if running on Linux."""
    return platform.system().lower() == "linux"


def is_macos() -> bool:
    """Check if running on macOS."""
    return platform.system().lower() == "darwin"


def get_project_root() -> Path:
    """Get the absolute path to the project root directory.
    
    This allows Darvis to work regardless of where it's installed.
    """
    # Get the directory containing this config file
    return Path(__file__).parent.parent.resolve()


def get_waybar_script_path() -> str:
    """Get the path to the waybar status script.
    
    Returns the path as a string for use in waybar configuration.
    """
    return str(get_project_root() / "scripts" / "darvis-waybar-status")

# Wake words for voice activation
WAKE_WORDS = [
    "hey darvis",
    "hey jarvis",
    "play darvis",
    "play jarvis",
    "hi darvis",
    "hi jarvis",
]

# Web services mapping
WEB_SERVICES = {
    "youtube": "https://youtube.com",
    "google": "https://google.com",
    "gmail": "https://gmail.com",
    "github": "https://github.com",
    "netflix": "https://netflix.com",
    "spotify": "https://spotify.com",
    "basecamp": "https://basecamp.com",
    "slack": "https://slack.com",
    "discord": "https://discord.com",
    "zoom": "https://zoom.us",
    "teams": "https://teams.microsoft.com",
    "notion": "https://notion.so",
    "figma": "https://figma.com",
    "canva": "https://canva.com",
    "drive": "https://drive.google.com",
    "docs": "https://docs.google.com",
    "calendar": "https://calendar.google.com",
    "trello": "https://trello.com",
    "asana": "https://asana.com",
    "jira": "https://jira.atlassian.com",
    "confluence": "https://confluence.atlassian.com",
}

# GUI configuration
FONT_SIZE_NORMAL = 16
FONT_SIZE_LARGE = 24
GLOW_DURATION_MS = 1500

# Speech recognition settings
ENERGY_THRESHOLD = 400
LISTEN_TIMEOUT = 5
PHRASE_TIME_LIMIT = 5

# Application detection settings - platform-specific
def get_desktop_dirs() -> list:
    """Get application directories based on platform."""
    if is_macos():
        return [
            "/Applications/",
            "/System/Applications/",
            os.path.expanduser("~/Applications/"),
        ]
    else:  # Linux and others
        return [
            "/usr/share/applications/",
            "/usr/local/share/applications/",
            os.path.expanduser("~/.local/share/applications/"),
            "/var/lib/snapd/desktop/applications/",
        ]


# Keep backward compatibility
DESKTOP_DIRS = get_desktop_dirs()

# Message queue types
MSG_TYPES = {
    "INSERT": "insert",
    "STATUS": "status",
    "WAKE_WORD_DETECTED": "wake_word_detected",
    "WAKE_WORD_END": "wake_word_end",
}

# Waybar integration configuration
# The exec path will be set dynamically at runtime
WAYBAR_MODULE_CONFIG = {
    "custom/darvis": {
        "exec": f"python3 {get_waybar_script_path()}",
        "return-type": "json",
        "restart-interval": 0,
        "tooltip-format": "{tooltip}",
    }
}

# Web app integration settings
WEB_APP_HOST = "localhost"
WEB_APP_PORT = 5001
WEB_APP_URL = f"http://{WEB_APP_HOST}:{WEB_APP_PORT}"


def get_open_command() -> str:
    """Get the appropriate command to open files/URLs based on platform.
    
    Returns:
        Command string: 'xdg-open' for Linux, 'open' for macOS
    """
    if is_macos():
        return "open"
    return "xdg-open"


# macOS-specific application mappings
MACOS_APP_MAPPINGS = {
    "safari": ["/Applications/Safari.app"],
    "chrome": ["/Applications/Google Chrome.app", "/Applications/Chromium.app"],
    "firefox": ["/Applications/Firefox.app"],
    "browser": ["/Applications/Safari.app", "/Applications/Google Chrome.app", "/Applications/Firefox.app"],
    "terminal": ["/System/Applications/Terminal.app", "/Applications/iTerm.app"],
    "editor": ["/Applications/TextEdit.app", "/Applications/CotEditor.app"],
    "textedit": ["/Applications/TextEdit.app"],
    "calculator": ["/System/Applications/Calculator.app"],
    "facetime": ["/System/Applications/FaceTime.app"],
    "messages": ["/System/Applications/Messages.app"],
    "mail": ["/System/Applications/Mail.app"],
    "notes": ["/System/Applications/Notes.app"],
    "calendar": ["/System/Applications/Calendar.app"],
    "photos": ["/System/Applications/Photos.app"],
    "music": ["/System/Applications/Music.app"],
    "appstore": ["/System/Applications/App Store.app"],
    "settings": ["/System/Applications/System Settings.app", "/System/Applications/System Preferences.app"],
    "system preferences": ["/System/Applications/System Settings.app", "/System/Applications/System Preferences.app"],
    "preview": ["/System/Applications/Preview.app"],
    "activity monitor": ["/System/Applications/Utilities/Activity Monitor.app"],
    "console": ["/System/Applications/Utilities/Console.app"],
    "disk utility": ["/System/Applications/Utilities/Disk Utility.app"],
    "keychain access": ["/System/Applications/Utilities/Keychain Access.app"],
    # Development apps
    "code": ["/Applications/Visual Studio Code.app"],
    "vscode": ["/Applications/Visual Studio Code.app"],
    "sublime": ["/Applications/Sublime Text.app"],
    "xcode": ["/Applications/Xcode.app"],
    "docker": ["/Applications/Docker.app"],
    "iterm": ["/Applications/iTerm.app"],
    # Productivity apps
    "spotify": ["/Applications/Spotify.app"],
    "slack": ["/Applications/Slack.app"],
    "discord": ["/Applications/Discord.app"],
    "zoom": ["/Applications/zoom.us.app"],
    "teams": ["/Applications/Microsoft Teams.app"],
    "obsidian": ["/Applications/Obsidian.app"],
    "notion": ["/Applications/Notion.app"],
    "figma": ["/Applications/Figma.app"],
    "postman": ["/Applications/Postman.app"],
    "insomnia": ["/Applications/Insomnia.app"],
}
