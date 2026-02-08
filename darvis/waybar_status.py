"""
Waybar IPC communication for Darvis status updates.
Provides real-time status updates to waybar custom modules via FIFO pipe.
"""

import atexit
import json
import os
import platform
import subprocess
from pathlib import Path
from typing import Optional


class WaybarStatusManager:
    """Manages communication with waybar custom modules via FIFO pipe."""

    def __init__(self):
        self.is_linux = platform.system().lower() == "linux"
        self.has_waybar = False
        self.fifo_path: Optional[Path] = None
        self._initialized = False

    def setup(self) -> bool:
        """Setup FIFO pipe communication if on Linux with waybar.

        Returns:
            bool: True if setup successful, False otherwise
        """
        if not self.is_linux:
            return False

        try:
            # Check if waybar is running
            if not self._check_waybar_running():
                return False

            # Create user-specific FIFO path
            cache_dir = Path.home() / ".cache" / "darvis"
            cache_dir.mkdir(parents=True, exist_ok=True)
            self.fifo_path = cache_dir / "status.fifo"

            # Create FIFO pipe if it doesn't exist
            if not self.fifo_path.exists():
                os.mkfifo(self.fifo_path)

            self.has_waybar = True
            self._initialized = True

            # Register cleanup on exit
            atexit.register(self.cleanup)

            # Send initial status
            self.update_status("idle", "Darvis: Ready")
            return True

        except Exception as e:
            print(f"Waybar setup failed: {e}")
            return False

    def update_status(self, status: str, tooltip: str = ""):
        """Send status update to waybar via FIFO pipe.

        Args:
            status: Status type (idle, listening, processing, success, error)
            tooltip: Optional tooltip text
        """
        if not self.has_waybar or not self.fifo_path:
            return

        status_map = {
            "idle": {"text": "🤖", "class": "idle"},
            "listening": {"text": "🎤", "class": "listening"},
            "processing": {"text": "⚙️", "class": "processing"},
            "thinking": {"text": "🧠", "class": "thinking"},
            "speaking": {"text": "🔊", "class": "speaking"},
            "success": {"text": "✅", "class": "success"},
            "error": {"text": "❌", "class": "error"},
            "warning": {"text": "⚠️", "class": "warning"},
        }

        if status in status_map:
            data = status_map[status].copy()
            if tooltip:
                data["tooltip"] = f"Darvis: {tooltip}"
            else:
                data["tooltip"] = f"Darvis: {status.title()}"

            self._write_to_fifo(data)

    def _write_to_fifo(self, data: dict):
        """Write JSON data to FIFO pipe."""
        if not self.fifo_path:
            return

        try:
            # Open FIFO in non-blocking mode to avoid hanging if no reader
            import fcntl
            fd = os.open(self.fifo_path, os.O_WRONLY | os.O_NONBLOCK)
            with os.fdopen(fd, "w") as fifo:
                json.dump(data, fifo)
                fifo.write("\n")
                fifo.flush()
        except (OSError, IOError) as e:
            # No reader connected or other error - silently ignore
            pass
        except Exception as e:
            print(f"FIFO write failed: {e}")

    def _check_waybar_running(self) -> bool:
        """Check if waybar process is running."""
        try:
            # Try multiple ways to detect waybar with timeout
            # First try exact match
            result = subprocess.run(
                ["pgrep", "-x", "waybar"], capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                return True
            
            # Also try with 'ps' command as fallback
            result = subprocess.run(
                ["ps", "aux"], capture_output=True, text=True, timeout=2
            )
            if "waybar" in result.stdout and "/waybar" in result.stdout:
                return True
                
            return False
        except subprocess.TimeoutExpired:
            return False
        except Exception:
            return False

    def cleanup(self):
        """Clean up FIFO pipe."""
        if self.fifo_path and self.fifo_path.exists():
            try:
                # Send a final status to clear the waybar module before removing the FIFO
                with open(self.fifo_path, "w") as fifo:
                    import json
                    json.dump({"text": "", "class": "exited", "tooltip": "Darvis: Exited"}, fifo)
                    fifo.write("\n")
                    fifo.flush()
                # Small delay to ensure the message is processed
                import time
                time.sleep(0.1)
                # Now remove the FIFO file
                self.fifo_path.unlink()
            except Exception as e:
                print(f"FIFO cleanup failed: {e}")


# Global instance for easy access
_waybar_manager = None


def get_waybar_manager() -> WaybarStatusManager:
    """Get the global waybar status manager instance."""
    global _waybar_manager
    if _waybar_manager is None:
        _waybar_manager = WaybarStatusManager()
    return _waybar_manager


def init_waybar() -> bool:
    """Initialize waybar integration. Returns True if successful."""
    manager = get_waybar_manager()
    return manager.setup()


def update_waybar_status(status: str, tooltip: str = ""):
    """Update waybar status (convenience function)."""
    manager = get_waybar_manager()
    manager.update_status(status, tooltip)
