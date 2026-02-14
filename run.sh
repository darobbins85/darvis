#!/bin/bash
# Unified Test Script for Darvis Web-Desktop Sync
# This script starts both the web chat interface and desktop app for testing synchronization

set -m  # Enable job control

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

# Function to wait for web server to start
wait_for_web() {
    echo "⏳ Waiting for web server to start..."
    local attempts=0
    local max_attempts=30
    
    while [ $attempts -lt $max_attempts ]; do
        if python3 -c "
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(1)
result = sock.connect_ex(('127.0.0.1', 5001))
sock.close()
exit(0 if result == 0 else 1)
" 2>/dev/null; then
            echo "✅ Web server is listening on port 5001"
            return 0
        fi
        attempts=$((attempts + 1))
        sleep 1
    done
    
    echo "❌ Web server failed to start on port 5001"
    return 1
}

# Cleanup function to kill all child processes
cleanup() {
    echo ""
    echo "🧹 Cleaning up processes..."
    
    # Kill by PID if we have them
    if [ -n "$WEB_PID" ]; then
        kill $WEB_PID 2>/dev/null
        # Wait for process to actually terminate
        timeout 5 sh -c "while kill -0 $WEB_PID 2>/dev/null; do sleep 0.5; done" 2>/dev/null || true
    fi
    
    if [ -n "$DESKTOP_PID" ]; then
        kill $DESKTOP_PID 2>/dev/null
        timeout 5 sh -c "while kill -0 $DESKTOP_PID 2>/dev/null; do sleep 0.5; done" 2>/dev/null || true
    fi
    
    # Kill any remaining Python processes related to Darvis
    pkill -f "python.*darvis.ui" 2>/dev/null || true
    pkill -f "python.*web_chat.py" 2>/dev/null || true
    
    echo "✅ Cleanup complete"
    exit 0
}

# Set up signal handlers
trap cleanup INT TERM EXIT

# Activate virtual environment
source venv/bin/activate

# Start web chat interface in background
echo "🌐 Starting web chat interface..."
python web_chat.py &
WEB_PID=$!
echo "🌐 Web app started with PID: $WEB_PID"

# Check if web app is still running
if ! kill -0 $WEB_PID 2>/dev/null; then
    echo "❌ Web app process exited early"
    exit 1
fi

# Wait for web server to start
if ! wait_for_web; then
    echo "❌ Failed to start web server"
    cleanup
    exit 1
fi

echo ""
echo "🖥️  Starting desktop application..."
echo "💡 Both apps should now sync chats!"
echo "   - Web interface: http://localhost:5001"
echo "   - Desktop app will open in a new window"
echo "❌ Press Ctrl+C to stop both applications"
echo ""

# Start desktop app in background using exec to replace the shell
# This ensures the PID is actually the Python process
(
    cd "$SCRIPT_DIR"
    exec python -m darvis.ui
) &
DESKTOP_PID=$!

echo "Both apps running (Web PID: $WEB_PID, Desktop PID: $DESKTOP_PID)"
echo "Press Ctrl+C to stop both applications"
echo "Note: Closing the desktop window will stop both apps"

# Main monitoring loop
while true; do
    # Check if desktop app has exited
    if ! kill -0 $DESKTOP_PID 2>/dev/null; then
        echo ""
        echo "🖥️  Desktop app closed. Stopping web server..."
        cleanup
        break
    fi
    
    # Check if web app has exited
    if ! kill -0 $WEB_PID 2>/dev/null; then
        echo ""
        echo "🌐 Web server stopped."
        # Kill desktop app too
        kill $DESKTOP_PID 2>/dev/null || true
        break
    fi
    
    sleep 0.5
done

echo ""
echo "👋 Darvis stopped"
