# Web-Desktop Synchronization

This feature allows the desktop GUI and web interface to share chat messages in real-time.

## Setup

1. **Install dependencies** (optional - sync works without it):
   ```bash
   pip install python-socketio
   ```

2. **Run both interfaces**:
   ```bash
   # Terminal 1: Start web interface
   ./setup_web_chat.sh && ./launch_web_chat.sh

   # Terminal 2: Start desktop interface (will auto-detect web app)
   ./launch-darvis.sh
   ```

## How It Works

- Desktop app automatically detects if web app is running on localhost:5000
- If detected, establishes SocketIO connection for real-time sync
- Messages sent in either interface appear in both
- AI responses are shared between interfaces
- Works bidirectionally

## Features

- **Automatic Detection**: Desktop app finds running web instances
- **Real-time Sync**: Messages appear instantly in both interfaces
- **Graceful Fallback**: Works standalone if web app not available
- **Connection Status**: Console logs show sync status

## Benefits

- **Multi-device Access**: Control Darvis from desktop and web simultaneously
- **Shared Conversations**: Same chat history across interfaces
- **Seamless Experience**: No need to choose between desktop/web