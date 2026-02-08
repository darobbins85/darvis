#!/usr/bin/env bash
# Darvis Voice Assistant Launcher Script
# This script provides a clean way to launch Darvis with proper environment setup

# Get the absolute path of the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

# Change to home directory so AI has access to home folder
cd "$HOME"

# Set PYTHONPATH explicitly
export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"

# Add opencode to PATH if available
if [ -d "$HOME/.opencode/bin" ]; then
    export PATH="$HOME/.opencode/bin:$PATH"
fi

# Ensure proper display environment for GUI
export DISPLAY="${DISPLAY:-:0}"

# Use explicit python from venv
PYTHON_EXE="$PROJECT_DIR/venv/bin/python"

# Launch the application
if [ -f "$PYTHON_EXE" ]; then
    exec "$PYTHON_EXE" -m darvis.ui
else
    echo "ERROR: Python not found at $PYTHON_EXE"
    exit 1
fi
