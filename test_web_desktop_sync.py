#!/usr/bin/env python3
"""
Test script for web-desktop synchronization
"""

import socket
import time

def test_web_app_connection():
    """Test if web app is running and accessible"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', 5000))
        sock.close()

        if result == 0:
            print("✅ Web app is running on localhost:5000")
            return True
        else:
            print("❌ Web app not found on localhost:5000")
            return False
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def test_desktop_imports():
    """Test if desktop app can import web sync dependencies"""
    try:
        import socket
        import threading
        print("✅ Basic sync imports available")

        try:
            import socketio
            print("✅ SocketIO client available for web sync")
            return True
        except ImportError:
            print("⚠️ SocketIO client not installed - web sync disabled")
            print("   Install with: pip install python-socketio")
            return False
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Web-Desktop Synchronization Setup")
    print("=" * 50)

    web_available = test_web_app_connection()
    desktop_ready = test_desktop_imports()

    print("\n📊 Results:")
    if web_available and desktop_ready:
        print("✅ Full synchronization ready!")
        print("   Run desktop app - it will auto-connect to web app")
    elif web_available and not desktop_ready:
        print("⚠️ Web app ready, but desktop sync needs dependencies")
    elif not web_available and desktop_ready:
        print("⚠️ Desktop ready, but web app not running")
    else:
        print("❌ Neither web nor desktop sync ready")

    print("\n🚀 To test:")
    print("1. Start web app: ./setup_web_chat.sh && ./launch_web_chat.sh")
    print("2. Start desktop: ./launch-darvis.sh")
    print("3. Send messages in either - they should appear in both!")