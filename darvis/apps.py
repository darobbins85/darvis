"""
Application detection and launching functionality.
"""

import glob
import os
import subprocess


from .config import (
    DESKTOP_DIRS,
    get_desktop_dirs,
    is_macos,
    is_linux,
    MACOS_APP_MAPPINGS,
    get_open_command,
)


def find_macos_app(app_name: str) -> str:
    """
    Find macOS .app bundle paths.

    Args:
        app_name: Name of the application to find

    Returns:
        Path to .app bundle, or empty string if not found
    """
    app_name_lower = app_name.lower()

    # Check macOS-specific mappings first
    if app_name_lower in MACOS_APP_MAPPINGS:
        for app_path in MACOS_APP_MAPPINGS[app_name_lower]:
            if os.path.exists(app_path):
                return app_path

    # Search in Applications directories
    for app_dir in get_desktop_dirs():
        if os.path.exists(app_dir):
            # Try exact match
            exact_path = os.path.join(app_dir, f"{app_name}.app")
            if os.path.exists(exact_path):
                return exact_path

            # Try case-insensitive search
            try:
                for item in os.listdir(app_dir):
                    if item.lower() == f"{app_name_lower}.app":
                        full_path = os.path.join(app_dir, item)
                        if os.path.exists(full_path):
                            return full_path
            except (OSError, PermissionError):
                continue

    return ""  # Not found


def find_app_command(app_name: str) -> str:
    """
    Find the correct command to launch an application.

    Checks .desktop files, PATH, and common command variations.
    Platform-specific: uses .desktop files on Linux, .app bundles on macOS.

    Args:
        app_name: Name of the application to find

    Returns:
        Command string to execute, or empty string if not found
    """
    app_name_lower = app_name.lower()

    # macOS-specific handling
    if is_macos():
        macos_app = find_macos_app(app_name)
        if macos_app:
            return macos_app

    # Extended app mapping with common variations (Linux-focused)
    app_map = {
        "chrome": ["chromium", "google-chrome", "chrome"],
        "browser": ["firefox", "chromium", "chrome"],
        "firefox": ["firefox"],
        "chromium": ["chromium"],
        "terminal": ["xterm", "gnome-terminal", "konsole", "terminator", "alacritty"],
        "editor": [
            "gedit",
            "kate",
            "mousepad",
            "leafpad",
            "nano",
            "vim",
            "code",
            "vscode",
        ],
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
        "libreoffice": ["libreoffice", "lowriter", "libreoffice"],
        "gimp": ["gimp"],
        "inkscape": ["inkscape"],
        "blender": ["blender"],
        "krita": ["krita", "krita"],
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
        "scribus": ["scribus"],
        "audacity": ["audacity"],
        "kdenlive": ["kdenlive"],
        "shotcut": ["shotcut"],
        # Office and documents
        "onlyoffice": ["onlyoffice", "onlyoffice-desktopeditors"],
        "wps": ["wps", "wps-office"],
    }

    # Check if we have a direct mapping
    if app_name_lower in app_map:
        for cmd in app_map[app_name_lower]:
            if is_command_available(cmd):
                return cmd

    # Check .desktop files in standard locations (Linux only)
    if is_linux():
        for desktop_dir in DESKTOP_DIRS:
            if os.path.exists(desktop_dir):
                # Look for .desktop files that match the app name
                # Try multiple variations: original, spaces replaced with hyphens, underscores
                search_patterns = [
                    f"*{app_name_lower}*.desktop",
                    f"*{app_name_lower.replace(' ', '-')}.desktop",
                    f"*{app_name_lower.replace(' ', '_')}.desktop",
                ]

                for pattern in search_patterns:
                    for desktop_file in glob.glob(os.path.join(desktop_dir, pattern)):
                        try:
                            exec_cmd = parse_desktop_file(desktop_file)
                            if exec_cmd and is_command_available(exec_cmd.split()[0]):
                                return exec_cmd
                        except (OSError, IOError, ValueError):
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
                        except (OSError, IOError, ValueError):
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
        for line in content.split("\n"):
            if line.startswith("Exec="):
                exec_cmd = line.split("=", 1)[1].strip()
                # Remove field codes like %f, %F, %u, %U, etc.
                exec_cmd = exec_cmd.split()[0]  # Take just the command, not args
                return exec_cmd
    except (OSError, IOError, UnicodeDecodeError):
        pass
    return ""


def open_app(app_name: str) -> str:
    """
    Launch applications or open web services based on user commands.

    Supports both local system applications and web services. Uses intelligent
    app detection to find installed applications and their correct launch commands.
    Works on both Linux and macOS.

    Args:
        app_name: Name of application or web service to launch

    Returns:
        Success message or error description

    Supported Web Services:
        - youtube, google, gmail, github, netflix, spotify

    App Detection:
        - Linux: Checks .desktop files, searches PATH
        - macOS: Checks /Applications, /System/Applications, ~/Applications
        - Supports common application name variations on both platforms
    """
    from .config import WEB_SERVICES

    app_name_lower = app_name.lower()

    # Handle web services that should open in browser
    if app_name_lower in WEB_SERVICES:
        open_cmd = get_open_command()
        try:
            subprocess.Popen([open_cmd, WEB_SERVICES[app_name_lower]])
            return f"Opening {app_name}"
        except FileNotFoundError:
            # Fallback to trying browsers directly
            browsers = ["chromium", "firefox", "google-chrome", "safari"]
            for browser in browsers:
                try:
                    subprocess.Popen([browser, WEB_SERVICES[app_name_lower]])
                    return f"Opening {app_name} in {browser}"
                except FileNotFoundError:
                    continue
            return (
                f"Couldn't find a way to open {app_name}. "
                f"Try installing a browser or check if it's in your PATH."
            )
        except Exception as e:
            return f"Error opening {app_name}: {str(e)}"
    else:
        # Try to find the app command
        app_command = find_app_command(app_name)

        if app_command:
            try:
                # On macOS, use 'open' command for .app bundles
                if is_macos() and app_command.endswith('.app'):
                    subprocess.Popen(["open", app_command])
                else:
                    subprocess.Popen([app_command])
                return f"Opening {app_name}"
            except Exception as e:
                return f"Error launching {app_name}: {str(e)}"
        else:
            platform_hint = "brew install" if is_macos() else "pacman -S (on Arch)"
            return (
                f"'{app_name}' is not installed or not found on this system. "
                f"Try: {platform_hint} {app_name} or check if it's installed."
            )
