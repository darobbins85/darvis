#!/bin/bash
# Unified Test Script for Darvis Web-Desktop Sync
# This script starts both the web chat interface and desktop app for testing synchronization

echo "🔄 Starting Darvis Web-Desktop Sync Test..."
echo "This will launch both web interface and desktop app"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

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

# Start web chat interface
echo "🌐 Starting web chat interface..."
./venv/bin/python web_chat.py &
WEB_PID=$!
echo "🌐 Web app started with PID: $WEB_PID"

# Wait for web server to be ready
echo "⏳ Waiting for web server..."
for i in {1..30}; do
    if ./venv/bin/python -c "
import socket, sys
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('127.0.0.1', 5001))
    sock.close()
    sys.exit(0 if result == 0 else 1)
except:
    sys.exit(1)
" 2>/dev/null; then
        echo "✅ Web server ready on port 5001"
        break
    fi
    sleep 1
done

echo ""
echo "🖥️  Starting desktop application..."
echo "💡 Both apps should now sync chats!"
echo "   - Web interface: http://localhost:5001"
echo "❌ Press Ctrl+C to stop both applications"
echo ""

# Run desktop app in foreground
# When user closes the window, Python exits and we continue to cleanup
echo "Both apps running"
echo "Note: Closing the desktop window will stop both apps"
echo ""

./venv/bin/python -m darvis.ui

# If we get here, desktop app has exited (user closed window)
echo ""
echo "🖥️  Desktop app closed. Stopping web server..."
cleanup
