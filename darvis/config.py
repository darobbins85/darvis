"""
Configuration and constants for Darvis Voice Assistant.
"""

import os

# Suppress ALSA warnings for cleaner output
os.environ["ALSA_LOG_LEVEL"] = "0"

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

# Application detection settings
DESKTOP_DIRS = [
    "/usr/share/applications/",
    "/usr/local/share/applications/",
    os.path.expanduser("~/.local/share/applications/"),
    "/var/lib/snapd/desktop/applications/",
]

# Message queue types
MSG_TYPES = {
    "INSERT": "insert",
    "STATUS": "status",
    "WAKE_WORD_DETECTED": "wake_word_detected",
    "WAKE_WORD_END": "wake_word_end",
}

# Waybar integration configuration
WAYBAR_MODULE_CONFIG = {
    "custom/darvis": {
        "exec": "python3 /home/david/Code/github/darobbins85/darvis/scripts/darvis-waybar-status",
        "return-type": "json",
        "restart-interval": 0,
        "tooltip-format": "{tooltip}",
    }
}

# Web app integration settings
WEB_APP_HOST = "localhost"
WEB_APP_PORT = 5001
WEB_APP_URL = f"http://{WEB_APP_HOST}:{WEB_APP_PORT}"
