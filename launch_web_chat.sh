#!/bin/bash
# Web Chat Interface Launcher for Darvis
# This script activates the virtual environment and starts the web-based chat interface

echo "🤖 Starting Darvis Web Chat Interface..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
if [ -d "web_env" ]; then
    echo "📦 Activating virtual environment..."
    source web_env/bin/activate
else
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Start the web chat interface
echo "🌐 Starting Flask server on http://localhost:5000"
echo "📱 Open your browser to http://localhost:5000"
echo "🎤 Use the listening toggle for voice commands"
echo "❌ Press Ctrl+C to stop"
echo ""

python web_chat.py