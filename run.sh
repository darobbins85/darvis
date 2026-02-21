#!/bin/bash
# Unified Test Script for Darvis Web-Desktop Sync
# This script starts both the web chat interface and desktop app for testing synchronization

echo "🔄 Starting Darvis Web-Desktop Sync Test..."
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Add opencode to PATH (needed for AI functionality)
export PATH="$HOME/.opencode/bin:$PATH"
echo "📍 PATH set to: $PATH"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment 'venv' not found. Please set up the environment first."
    exit 1
fi

# Function to cleanup and exit
cleanup() {
    echo ""
    echo "🧹 Cleaning up..."
    
    # Kill web server if running
    if [ -n "$WEB_PID" ]; then
        kill $WEB_PID 2>/dev/null || true
        wait $WEB_PID 2>/dev/null || true
    fi
    
    # Kill any remaining Python processes
    pkill -f "python.*web_chat.py" 2>/dev/null || true
    pkill -f "python.*darvis.ui" 2>/dev/null || true
    
    echo "✅ Done"
    exit 0
}

# Handle Ctrl+C
trap cleanup INT

# Start web chat interface in background
echo "🌐 Starting web chat interface..."
./venv/bin/python web_chat.py &
WEB_PID=$!
echo "🌐 Web app started (PID: $WEB_PID)"

# Give web server a moment to start
echo "⏳ Initializing..."
sleep 2

# Start desktop app immediately (GUI will appear right away)
echo "🖥️  Starting desktop application..."
echo ""

./venv/bin/python -m darvis.ui

# If we get here, desktop app has closed
echo ""
echo "🖥️  Desktop app closed. Stopping web server..."
cleanup
