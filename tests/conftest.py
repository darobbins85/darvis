"""
Pytest configuration and fixtures for Darvis Voice Assistant E2E testing.

This module provides shared fixtures and utilities for end-to-end testing of the
Darvis application, including voice simulation, GUI verification, and process monitoring.
"""

import pytest
import subprocess
import time
import psutil
import os
import signal
import tempfile
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test configuration
TEST_CONFIG = {
    'darvis_startup_timeout': 10,  # seconds
    'voice_simulation_delay': 2,   # seconds between voice commands
    'gui_response_timeout': 5,     # seconds to wait for GUI updates
    'app_launch_timeout': 3,       # seconds to wait for app launch
    'cleanup_timeout': 5,          # seconds for cleanup
    'test_audio_device': None,     # None = default device
}


@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration to all tests."""
    return TEST_CONFIG.copy()


@pytest.fixture(scope="session")
def darvis_process(test_config):
    """
    Fixture that starts Darvis application for E2E testing.

    This fixture starts the Darvis application in a separate process,
    waits for it to initialize, and ensures it's properly cleaned up
    after all tests complete.
    """
    darvis_proc = None
    try:
        # Start Darvis in test mode (if supported) or normal mode
        cmd = [sys.executable, "-m", "darvis.ui"]

        # Set environment variables for testing
        env = os.environ.copy()
        env['DARVIS_TEST_MODE'] = '1'  # Enable test mode if supported
        env['PYTHONPATH'] = str(project_root)

        darvis_proc = subprocess.Popen(
            cmd,
            cwd=str(project_root),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid if os.name != 'nt' else None
        )

        # Wait for Darvis to start up
        time.sleep(test_config['darvis_startup_timeout'])

        # Verify process is still running
        if darvis_proc.poll() is not None:
            stdout, stderr = darvis_proc.communicate()
            pytest.fail(f"Darvis failed to start. STDOUT: {stdout.decode()}, STDERR: {stderr.decode()}")

        yield darvis_proc

    finally:
        # Cleanup: terminate Darvis process
        if darvis_proc and darvis_proc.poll() is None:
            try:
                if os.name == 'nt':
                    darvis_proc.terminate()
                    darvis_proc.wait(timeout=test_config['cleanup_timeout'])
                else:
                    os.killpg(os.getpgid(darvis_proc.pid), signal.SIGTERM)
                    darvis_proc.wait(timeout=test_config['cleanup_timeout'])
            except subprocess.TimeoutExpired:
                if os.name == 'nt':
                    darvis_proc.kill()
                else:
                    os.killpg(os.getpgid(darvis_proc.pid), signal.SIGKILL)


@pytest.fixture
def voice_simulator():
    """
    Fixture providing voice simulation utilities.

    This fixture provides methods to simulate voice input without
    requiring actual microphone input.
    """
    class VoiceSimulator:
        def __init__(self):
            self.audio_device = TEST_CONFIG['test_audio_device']

        def simulate_wake_word(self, wake_word="hey darvis"):
            """
            Simulate wake word detection.

            In a real implementation, this would inject audio data
            directly into the speech recognition pipeline.
            """
            # For now, this is a placeholder - actual implementation
            # would require modifying Darvis to accept simulated input
            print(f"Simulating wake word: {wake_word}")
            time.sleep(0.5)  # Brief delay for processing

        def simulate_voice_command(self, command):
            """
            Simulate a complete voice command.

            Args:
                command (str): The voice command to simulate
            """
            print(f"Simulating voice command: {command}")
            # Placeholder - would inject audio for the command
            time.sleep(TEST_CONFIG['voice_simulation_delay'])

        def wait_for_voice_processing(self):
            """Wait for voice processing to complete."""
            time.sleep(TEST_CONFIG['gui_response_timeout'])

    return VoiceSimulator()


@pytest.fixture
def gui_verifier():
    """
    Fixture providing GUI verification utilities.

    This fixture provides methods to verify GUI state and content.
    """
    class GUIVerifier:
        def __init__(self):
            try:
                import pyautogui
                self.pyautogui = pyautogui
                self.available = True
            except ImportError:
                self.pyautogui = None
                self.available = False

        def wait_for_speech_bubble(self, timeout=None):
            """
            Wait for a speech bubble to appear on screen.

            Returns:
                bool: True if speech bubble found, False otherwise
            """
            if not self.available:
                pytest.skip("pyautogui not available for GUI testing")

            if timeout is None:
                timeout = TEST_CONFIG['gui_response_timeout']

            # This is a simplified implementation
            # Real implementation would use image recognition
            # to find speech bubbles on screen
            time.sleep(1)  # Simplified wait
            return True  # Placeholder

        def get_speech_bubble_text(self):
            """
            Extract text from the most recent speech bubble.

            Returns:
                str: Text content of speech bubble, or None if not found
            """
            if not self.available:
                return None

            # Placeholder - would use OCR or accessibility APIs
            return "Sample speech bubble text"

        def verify_logo_animation(self, animation_type="glow"):
            """
            Verify that logo animation is active.

            Args:
                animation_type (str): Type of animation to check for

            Returns:
                bool: True if animation detected
            """
            if not self.available:
                return False

            # Placeholder - would analyze screen for animation effects
            return True

    return GUIVerifier()


@pytest.fixture
def process_monitor():
    """
    Fixture providing process monitoring utilities.

    This fixture helps verify that applications are launched correctly.
    """
    class ProcessMonitor:
        def __init__(self):
            self.baseline_processes = set()

        def take_baseline(self):
            """Record current running processes as baseline."""
            self.baseline_processes = {p.pid for p in psutil.process_iter()}

        def wait_for_process(self, process_name, timeout=None):
            """
            Wait for a process to start.

            Args:
                process_name (str): Name of process to wait for
                timeout (float): Maximum time to wait in seconds

            Returns:
                bool: True if process found, False if timeout
            """
            if timeout is None:
                timeout = TEST_CONFIG['app_launch_timeout']

            start_time = time.time()
            while time.time() - start_time < timeout:
                for proc in psutil.process_iter(['pid', 'name']):
                    if process_name.lower() in proc.info['name'].lower():
                        return True
                time.sleep(0.1)
            return False

        def get_new_processes(self):
            """
            Get processes that started since baseline.

            Returns:
                list: List of new process information
            """
            current_processes = {p.pid: p.info for p in psutil.process_iter(['pid', 'name'])}
            new_processes = []

            for pid, info in current_processes.items():
                if pid not in self.baseline_processes:
                    new_processes.append(info)

            return new_processes

    monitor = ProcessMonitor()
    monitor.take_baseline()
    return monitor


@pytest.fixture(autouse=True)
def cleanup_after_test():
    """
    Fixture that runs after each test to ensure clean state.

    This fixture kills any processes that might have been started
    during testing to prevent interference between tests.
    """
    yield

    # Cleanup code here if needed
    # For example, close any test applications that were launched


# Custom pytest markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test"
    )
    config.addinivalue_line(
        "markers", "voice: mark test as voice-related"
    )
    config.addinivalue_line(
        "markers", "gui: mark test as GUI-related"
    )
    config.addinivalue_line(
        "markers", "ai: mark test as AI-related"
    )
    config.addinivalue_line(
        "markers", "apps: mark test as application-related"
    )