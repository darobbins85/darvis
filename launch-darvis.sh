#!/usr/bin/env bash
# Darvis Voice Assistant Launcher Script

# Get the absolute path of the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

# Change to home directory
cd "$HOME"

# Set PYTHONPATH
export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"

# Add opencode to PATH
if [ -d "$HOME/.opencode/bin" ]; then
    export PATH="$HOME/.opencode/bin:$PATH"
fi

# Ensure proper display
export DISPLAY="${DISPLAY:-:0}"

# Use explicit python from venv
PYTHON_EXE="$PROJECT_DIR/venv/bin/python"

# Log file
LOG_FILE="$HOME/.local/share/darvis/darvis.log"

# Launch the application
if [ -f "$PYTHON_EXE" ]; then
    # Use unbuffered output and append to log
    exec "$PYTHON_EXE" -u -m darvis.ui >> "$LOG_FILE" 2>&1
else
    echo "ERROR: Python not found" >> "$LOG_FILE"
    exit 1
fi
