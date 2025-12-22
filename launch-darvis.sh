#!/usr/bin/env bash
# Darvis Voice Assistant Launcher Script
# This script provides a clean way to launch Darvis with proper environment setup

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Change to project directory
cd "$PROJECT_DIR"

# Set up Python virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Warning: Virtual environment not found. Using system Python."
fi

# Set environment variables for better integration
export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"

# Launch the application (using the main script for now)
python darvis.py

# Future: python -m darvis.ui (once modules are fully integrated)