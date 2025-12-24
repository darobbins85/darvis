"""
Application detection and launching functionality.
"""

import glob
import os
import subprocess
from typing import List, Optional
from .config import DESKTOP_DIRS


def find_app_command(app_name: str) -> str:
    """
    Find the correct command to launch an application.

    Checks .desktop files, PATH, and common command variations.

    Args:
        app_name: Name of the application to find

    Returns:
        Command string to execute, or empty string if not found
    """
    app_name_lower = app_name.lower()

    # Extended app mapping with common variations
    app_map = {
        "chrome": ["chromium", "google-chrome", "chrome"],
        "browser": ["firefox", "chromium", "chrome"],
        "firefox": ["firefox"],
        "chromium": ["chromium"],
        "terminal": ["xterm", "gnome-terminal", "konsole", "terminator", "alacritty"],
        "editor": ["gedit", "kate", "mousepad", "leafpad", "nano", "vim", "code", "vscode"],
        "gedit": ["gedit"],
        "calculator": ["galculator", "gnome-calculator", "kcalc", "speedcrunch"],
        "galculator": ["galculator"],
        "bluetooth manager": ["blueman-manager"],
        "bluetooth": ["blueman-manager"],
        "bluetooth adapters": ["blueman-adapters"],
        "system settings": ["gnome-settings-daemon", "systemsettings"],
        "settings": ["gnome-control-center", "systemsettings"],
        "network manager": ["nm-connection-editor", "networkmanager"],
        "printer settings": ["system-config-printer"],
        "volume control": ["pavucontrol", "alsamixer"],
        "sound settings": ["pavucontrol"],
        "display settings": ["arandr", "gnome-display-panel"],
        "steam": ["steam", "steam-runtime", "/usr/bin/steam"],
        "lutris": ["lutris"],
        "heroic": ["heroic", "heroic-launcher"],
        "proton": ["proton", "proton-ge"],
        "wine": ["wine"],
        "playonlinux": ["playonlinux"],
        "bottles": ["bottles"],
        "signal": ["signal-desktop", "signal"],
        "discord": ["discord", "discord-canary"],
        "slack": ["slack"],
        "spotify": ["spotify"],
        "vlc": ["vlc"],
        "code": ["code", "vscode"],
        "sublime": ["subl", "sublime-text"],
        "atom": ["atom"],
        "thunderbird": ["thunderbird"],
        "libreoffice": ["libreoffice", "lowriter"],
        "gimp": ["gimp"],
        "inkscape": ["inkscape"],
        "blender": ["blender"],
        "krita": ["krita"],
        # Productivity apps
        "obsidian": ["obsidian"],
        "notion": ["notion", "notion-app"],
        "evernote": ["evernote"],
        "onenote": ["onenote"],
        "zoom": ["zoom", "zoom-client"],
        "teams": ["teams", "teams-for-linux"],
        "skype": ["skype", "skypeforlinux"],
        "whatsapp": ["whatsapp", "whatsapp-desktop"],
        "telegram": ["telegram", "telegram-desktop"],
        # Development tools
        "postman": ["postman"],
        "insomnia": ["insomnia"],
        "dbeaver": ["dbeaver"],
        "mysql-workbench": ["mysql-workbench"],
        # Graphics and media
        "krita": ["krita"],
        "scribus": ["scribus"],
        "audacity": ["audacity"],
        "kdenlive": ["kdenlive"],
        "shotcut": ["shotcut"],
        # Office and documents
        "onlyoffice": ["onlyoffice", "onlyoffice-desktopeditors"],
        "wps": ["wps", "wps-office"],
        "libreoffice": ["libreoffice"],
    }

    # Check if we have a direct mapping
    if app_name_lower in app_map:
        for cmd in app_map[app_name_lower]:
            if is_command_available(cmd):
                return cmd

    # Check .desktop files in standard locations
    for desktop_dir in DESKTOP_DIRS:
        if os.path.exists(desktop_dir):
            # Look for .desktop files that match the app name
            # Try multiple variations: original, spaces replaced with hyphens, underscores
            search_patterns = [
                f"*{app_name_lower}*.desktop",
                f"*{app_name_lower.replace(' ', '-') }*.desktop",
                f"*{app_name_lower.replace(' ', '_') }*.desktop",
            ]

            for pattern in search_patterns:
                for desktop_file in glob.glob(os.path.join(desktop_dir, pattern)):
                    try:
                        exec_cmd = parse_desktop_file(desktop_file)
                        if exec_cmd and is_command_available(exec_cmd.split()[0]):
                            return exec_cmd
                    except:
                        continue

            # Also check for exact matches with various naming patterns
            exact_patterns = [
                f"{app_name_lower}.desktop",
                f"{app_name_lower.replace(' ', '-')}.desktop",
                f"{app_name_lower.replace(' ', '_')}.desktop",
            ]

            for exact_pattern in exact_patterns:
                exact_desktop = os.path.join(desktop_dir, exact_pattern)
                if os.path.exists(exact_desktop):
                    try:
                        exec_cmd = parse_desktop_file(exact_desktop)
                        if exec_cmd and is_command_available(exec_cmd.split()[0]):
                            return exec_cmd
                    except:
                        continue

    # Check if the app name itself is a valid command
    if is_command_available(app_name_lower):
        return app_name_lower

    # Try some common variations
    variations = [
        app_name_lower,
        f"{app_name_lower}-desktop",
        f"{app_name_lower}.bin",
        f"{app_name_lower}.sh",
        f"{app_name_lower}-linux",
        f"{app_name_lower}-client",
        f"{app_name_lower}-app",
        f"{app_name_lower}.AppImage",
        f"{app_name_lower}-flatpak",
    ]

    for variation in variations:
        if is_command_available(variation):
            return variation

    return ""  # Not found


def is_command_available(cmd: str) -> bool:
    """Check if a command is available in PATH."""
    try:
        subprocess.run([cmd], capture_output=True, check=False)
        return True
    except FileNotFoundError:
        return False


def parse_desktop_file(desktop_file: str) -> str:
    """Parse a .desktop file to extract the Exec command."""
    try:
        with open(desktop_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Look for the Exec line
        for line in content.split("\n"):
            if line.startswith("Exec="):
                exec_cmd = line.split("=", 1)[1].strip()
                # Remove field codes like %f, %F, %u, %U, etc.
                exec_cmd = exec_cmd.split()[0]  # Take just the command, not args
                return exec_cmd
    except:
        pass
    return ""


def open_app(app_name: str) -> str:
    """
    Launch applications or open web services based on user commands.

    Supports both local system applications and web services. Uses intelligent
    app detection to find installed applications and their correct launch commands.

    Args:
        app_name: Name of application or web service to launch

    Returns:
        Success message or error description

    Supported Web Services:
        - youtube, google, gmail, github, netflix, spotify

    App Detection:
        - Checks .desktop files in standard locations
        - Searches PATH for executable commands
        - Supports common application name variations
    """
    from .config import WEB_SERVICES

    app_name_lower = app_name.lower()

    # Handle web services that should open in browser
    if app_name_lower in WEB_SERVICES:
        # Use xdg-open for cross-desktop compatibility
        try:
            subprocess.Popen(["xdg-open", WEB_SERVICES[app_name_lower]])
            return f"Opening {app_name}"
        except FileNotFoundError:
            # Fallback to trying browsers directly
            browsers = ["chromium", "firefox"]
            for browser in browsers:
                try:
                    subprocess.Popen([browser, WEB_SERVICES[app_name_lower]])
                    return f"Opening {app_name} in {browser}"
                except FileNotFoundError:
                    continue
            return f"Couldn't find a way to open {app_name}. Try installing it with your package manager or check if it's installed in a custom location."
        except Exception as e:
            return f"Error opening {app_name}: {str(e)}"
    else:
        # Try to find the app command
        app_command = find_app_command(app_name)

        if app_command:
            try:
                subprocess.Popen([app_command])
                return f"Opening {app_name}"
            except Exception as e:
                return f"Error launching {app_name}: {str(e)}"
        else:
            return f"'{app_name}' is not installed or not found on this system. Try: pacman -S {app_name} (on Arch) or check if it's installed in a custom location"
