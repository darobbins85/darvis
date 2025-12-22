#!/usr/bin/env bash
# Darvis Voice Assistant Launcher Script
# This script provides a clean way to launch Darvis with proper environment setup

# Get the absolute path of the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

# Ensure we're in the correct directory
cd "$PROJECT_DIR"

# Set PYTHONPATH explicitly
export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"

# Add opencode to PATH if available
if [ -d "$HOME/.opencode/bin" ]; then
    export PATH="$HOME/.opencode/bin:$PATH"
fi

# Launch the application using the modular UI with system tray
if [ -f "venv/bin/activate" ]; then
    # Use exec to replace the shell process entirely
    exec bash -c "cd '$PROJECT_DIR' && source venv/bin/activate && exec python -m darvis.ui"
elif [ -f ".venv/bin/activate" ]; then
    exec bash -c "cd '$PROJECT_DIR' && source .venv/bin/activate && exec python -m darvis.ui"
else
    echo "Warning: Virtual environment not found. Using system Python."
    exec python -m darvis.ui
fi