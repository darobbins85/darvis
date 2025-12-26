#!/usr/bin/env python3
"""
Test script to mimic desktop GUI initialization and debug web sync
"""

import sys
import os

# Add the project directory to Python path like the launch script does
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = SCRIPT_DIR
sys.path.insert(0, PROJECT_DIR)

print("=== Desktop GUI Initialization Test ===")
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")
print(f"Script directory: {SCRIPT_DIR}")
print(f"Project directory: {PROJECT_DIR}")

# Test basic imports
print("\n--- Testing Basic Imports ---")
try:
    import darvis
    print("✅ darvis package imported")
except Exception as e:
    print(f"❌ darvis import failed: {e}")
    sys.exit(1)

try:
    from darvis import config
    print("✅ darvis.config imported")
    print(f"  WEB_APP_HOST: {config.WEB_APP_HOST}")
    print(f"  WEB_APP_PORT: {config.WEB_APP_PORT}")
    print(f"  WEB_APP_URL: {config.WEB_APP_URL}")
except Exception as e:
    print(f"❌ darvis.config import failed: {e}")

# Test socketio import
print("\n--- Testing SocketIO Import ---")
try:
    import socketio
    print("✅ socketio imported successfully")
    print(f"  SocketIO location: {socketio.__file__}")
    print(f"  SocketIO version: {getattr(socketio, '__version__', 'unknown')}")
except ImportError as e:
    print(f"❌ socketio import failed: {e}")

# Test GUI-related imports (but don't create GUI)
print("\n--- Testing GUI-Related Imports ---")
try:
    import tkinter as tk
    print("✅ tkinter imported")
except Exception as e:
    print(f"❌ tkinter import failed: {e}")

try:
    from PIL import Image, ImageTk, ImageFilter
    print("✅ PIL imported")
except Exception as e:
    print(f"❌ PIL import failed: {e}")

# Test web app detection
print("\n--- Testing Web App Detection ---")
try:
    import socket
    from darvis.config import WEB_APP_HOST, WEB_APP_PORT

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((WEB_APP_HOST, WEB_APP_PORT))
    sock.close()

    if result == 0:
        print(f"✅ Web app detected at {WEB_APP_HOST}:{WEB_APP_PORT}")
    else:
        print(f"❌ Web app not detected at {WEB_APP_HOST}:{WEB_APP_PORT}")
except Exception as e:
    print(f"❌ Web app detection failed: {e}")

print("\n=== Test Complete ===")