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

# Function to wait for web server to start
wait_for_web() {
    echo "⏳ Waiting 5 seconds for web server to start..."
    sleep 5

    # Test if port 5001 is actually listening
    if python3 -c "
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('127.0.0.1', 5001))
sock.close()
exit(0 if result == 0 else 1)
"; then
        echo "✅ Web server is listening on port 5001"
        return 0
    else
        echo "❌ Web server is not listening on port 5001"
        return 1
    fi
}

# Start web chat interface in background
echo "🌐 Starting web chat interface..."
cd "$SCRIPT_DIR" && source venv/bin/activate && python web_chat.py &
WEB_PID=$!
echo "🌐 Web app started with PID: $WEB_PID"

# Check if web app is still running
if kill -0 $WEB_PID 2>/dev/null; then
    echo "🌐 Web app process is running (PID: $WEB_PID)"
else
    echo "❌ Web app process exited early"
    exit 1
fi

# Wait for web server to start
if wait_for_web; then
    echo ""
    echo "🖥️  Starting desktop application..."
    echo "💡 Both apps should now sync chats!"
    echo "   - Web interface: http://localhost:5001"
    echo "   - Desktop app will open in a new window"
    echo "❌ Press Ctrl+C to stop both applications"
    echo ""

    # Start desktop app in background
    bash -c "cd '$SCRIPT_DIR' && source venv/bin/activate && python -m darvis.ui" &
    DESKTOP_PID=$!

    echo "Both apps running (Web PID: $WEB_PID, Desktop PID: $DESKTOP_PID)"
    echo "Press Ctrl+C to stop both applications"
    echo "Note: Closing the desktop window will stop both apps"

    # Monitor both processes - if either exits, kill the other
    trap "echo 'Stopping both apps...'; kill $WEB_PID $DESKTOP_PID 2>/dev/null; exit 0" INT
    
    while true; do
        # Check if desktop app has exited
        if ! kill -0 $DESKTOP_PID 2>/dev/null; then
            echo "Desktop app closed. Stopping web server..."
            kill $WEB_PID 2>/dev/null
            break
        fi
        # Check if web app has exited
        if ! kill -0 $WEB_PID 2>/dev/null; then
            echo "Web server stopped."
            break
        fi
        sleep 1
    done
else
    echo "❌ Failed to start web server. Check logs above."
    kill $WEB_PID 2>/dev/null
    exit 1
fi