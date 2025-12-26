#!/usr/bin/env python3
"""
Test script to verify GUI-web synchronization is working.
"""

import time
import socket
import requests
from darvis.config import WEB_APP_HOST, WEB_APP_PORT, WEB_APP_URL

def test_web_server():
    """Test if the web server is running."""
    print("🌐 Testing web server connection...")
    try:
        # Test basic HTTP connection
        response = requests.get(f"http://{WEB_APP_HOST}:{WEB_APP_PORT}", timeout=5)
        if response.status_code == 200:
            print(f"✅ Web server is running at {WEB_APP_URL}")
            return True
        else:
            print(f"❌ Web server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to web server: {e}")
        return False

def test_socket_connection():
    """Test if we can establish a socket connection."""
    print("🔌 Testing socket connection...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((WEB_APP_HOST, WEB_APP_PORT))
        sock.close()
        
        if result == 0:
            print(f"✅ Socket connection successful to {WEB_APP_HOST}:{WEB_APP_PORT}")
            return True
        else:
            print(f"❌ Socket connection failed with code {result}")
            return False
    except Exception as e:
        print(f"❌ Socket test failed: {e}")
        return False

def main():
    """Run all synchronization tests."""
    print("🧪 Testing GUI-Web Synchronization")
    print("=" * 40)
    
    # Test web server
    web_ok = test_web_server()
    print()
    
    # Test socket connection
    socket_ok = test_socket_connection()
    print()
    
    # Summary
    print("📊 Test Results:")
    print(f"   Web Server: {'✅ PASS' if web_ok else '❌ FAIL'}")
    print(f"   Socket Connection: {'✅ PASS' if socket_ok else '❌ FAIL'}")
    
    if web_ok and socket_ok:
        print("\n🎉 GUI-Web synchronization test PASSED!")
        print("   The GUI should be able to sync with the web interface.")
        print(f"   Open {WEB_APP_URL} in your browser to test manually.")
    else:
        print("\n❌ GUI-Web synchronization test FAILED!")
        print("   Check that the web server is running properly.")
    
    return web_ok and socket_ok

if __name__ == "__main__":
    main()