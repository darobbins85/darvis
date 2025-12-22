#!/usr/bin/env python3
"""
Configure waybar for Darvis integration.
Adds the custom darvis module to waybar configuration.
"""

import json
import os
from pathlib import Path
from darvis.config import WAYBAR_MODULE_CONFIG


def find_waybar_config():
    """Find waybar configuration file."""
    # Common locations for waybar config
    config_paths = [
        Path.home() / ".config" / "waybar" / "config.jsonc",
        Path.home() / ".config" / "waybar" / "config.json",
        # Check if it's in the omarchy theme
        Path.home()
        / ".local"
        / "share"
        / "omarchy"
        / "themes"
        / "ramen"
        / "waybar.jsonc",
    ]

    for path in config_paths:
        if path.exists():
            return path

    return None


def backup_config(config_path):
    """Create backup of current config."""
    backup_path = config_path.with_suffix(config_path.suffix + ".backup.darvis")
    if config_path.exists():
        import shutil

        shutil.copy2(config_path, backup_path)
        print(f"Backup created: {backup_path}")


def update_waybar_config():
    """Update waybar configuration to include Darvis module."""

    config_path = find_waybar_config()
    if not config_path:
        print(
            "Waybar configuration not found. Please ensure waybar is installed and configured."
        )
        print("Common locations:")
        print("  ~/.config/waybar/config.jsonc")
        print("  ~/.config/waybar/config.json")
        return False

    print(f"Found waybar config: {config_path}")

    try:
        # Read current config
        with open(config_path, "r") as f:
            if config_path.suffix == ".jsonc":
                # Remove comments for JSON parsing (simple approach)
                content = f.read()
                # Remove // comments
                lines = []
                for line in content.split("\n"):
                    line = line.split("//")[0].strip()
                    if line:
                        lines.append(line)
                content = "\n".join(lines)
                config = json.loads(content)
            else:
                config = json.load(f)

        # Backup original config
        backup_config(config_path)

        # Check if custom/darvis module already exists
        modules_right = config.get("modules-right", [])
        if "custom/darvis" not in modules_right:
            modules_right.insert(0, "custom/darvis")  # Add at beginning
            config["modules-right"] = modules_right
            print("Added custom/darvis to modules-right")
        else:
            print("custom/darvis already in modules-right")

        # Add module configuration
        for module_name, module_config in WAYBAR_MODULE_CONFIG.items():
            config[module_name] = module_config
            print(f"Added configuration for {module_name}")

        # Write updated config
        with open(config_path, "w") as f:
            if config_path.suffix == ".jsonc":
                # Write with some formatting for readability
                json.dump(config, f, indent=2)
            else:
                json.dump(config, f, indent=2)

        print(f"Waybar configuration updated successfully!")
        print("Please restart waybar to apply changes:")
        print("  omarchy-restart-waybar")
        print("  or: killall waybar && uwsm-app -- waybar")

        return True

    except Exception as e:
        print(f"Error updating waybar config: {e}")
        return False


if __name__ == "__main__":
    print("Darvis Waybar Configuration Tool")
    print("=" * 40)

    success = update_waybar_config()
    if success:
        print("\n✅ Waybar configured for Darvis!")
        print("Restart waybar to see the Darvis status indicator.")
    else:
        print("\n❌ Failed to configure waybar.")
        print(
            "You may need to manually add the custom/darvis module to your waybar config."
        )
