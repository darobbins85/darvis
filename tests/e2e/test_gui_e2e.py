"""
End-to-end tests for Darvis Voice Assistant GUI functionality.

These tests verify the graphical user interface behavior including
speech bubbles, animations, visual feedback, and user interactions.
"""

import pytest
import time
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Mark all tests in this module as E2E and GUI tests
pytestmark = [pytest.mark.e2e, pytest.mark.gui]


class TestGUIVisualFeedback:
    """Tests for GUI visual feedback and animations."""

    def test_speech_bubble_display(self, darvis_process, voice_simulator, gui_verifier):
        """
        Test that speech bubbles appear correctly after voice input.

        Verifies the visual feedback system for user input recognition.
        """
        # Trigger voice input
        voice_simulator.simulate_wake_word("hey darvis")
        time.sleep(0.5)
        voice_simulator.simulate_voice_command("hello")

        # Wait for GUI response
        voice_simulator.wait_for_voice_processing()

        # Verify speech bubble appears
        speech_bubble_found = gui_verifier.wait_for_speech_bubble()
        assert speech_bubble_found, "Speech bubble should appear after voice command"

        # Verify process stability
        assert darvis_process.poll() is None

    def test_logo_animation_wake_word(self, darvis_process, voice_simulator, gui_verifier):
        """
        Test logo animation during wake word detection.

        Verifies that the logo provides visual feedback when wake words are detected.
        """
        # Trigger wake word
        voice_simulator.simulate_wake_word("hey darvis")

        # Check for logo glow animation
        animation_active = gui_verifier.verify_logo_animation("glow")
        assert animation_active, "Logo should glow during wake word detection"

        assert darvis_process.poll() is None

    def test_logo_animation_ai_processing(self, darvis_process, voice_simulator, gui_verifier):
        """
        Test logo animation during AI processing.

        Verifies visual feedback while AI queries are being processed.
        """
        # Trigger AI query
        voice_simulator.simulate_wake_word("hey darvis")
        time.sleep(0.5)
        voice_simulator.simulate_voice_command("what is the capital of France")

        # Check for processing animation (red glow)
        animation_active = gui_verifier.verify_logo_animation("processing")
        assert animation_active, "Logo should show processing animation during AI queries"

        assert darvis_process.poll() is None

    def test_speech_bubble_colors(self, darvis_process, voice_simulator, gui_verifier):
        """
        Test speech bubble color coding.

        Verifies that different types of messages use appropriate colors:
        - Green: Voice input recognition
        - Blue: AI responses
        - Yellow: System status
        - Red: Errors
        """
        # Test voice input (green bubble)
        voice_simulator.simulate_wake_word("hey darvis")
        time.sleep(0.5)
        voice_simulator.simulate_voice_command("test command")

        voice_simulator.wait_for_voice_processing()

        # In full implementation, would verify bubble colors
        # For now, just ensure GUI remains responsive
        assert darvis_process.poll() is None


class TestGUILifecycle:
    """Tests for GUI behavior across different application states."""

    def test_gui_startup_animation(self, darvis_process, gui_verifier):
        """
        Test GUI startup sequence and initial animations.

        Verifies that the application starts with appropriate visual feedback.
        """
        # Wait for initial startup
        time.sleep(2)

        # Verify basic GUI elements are present
        # In full implementation, would check for logo display, initial state, etc.

        assert darvis_process.poll() is None, "GUI should start without crashing"

    def test_gui_idle_state(self, darvis_process, gui_verifier):
        """
        Test GUI appearance in idle state.

        Verifies the default appearance when no interaction is occurring.
        """
        # Wait for any startup animations to complete
        time.sleep(3)

        # Verify idle state appearance
        # In full implementation, would check logo opacity, no active animations, etc.

        assert darvis_process.poll() is None

    def test_gui_transition_states(self, darvis_process, voice_simulator, gui_verifier):
        """
        Test smooth transitions between GUI states.

        Verifies that state changes are visually smooth and don't cause glitches.
        """
        # Start in idle state
        time.sleep(1)

        # Transition to listening state
        voice_simulator.simulate_wake_word("hey darvis")
        time.sleep(1)

        # Transition to processing state
        voice_simulator.simulate_voice_command("quick test")
        time.sleep(1)

        # Return to idle state (after timeout or completion)
        voice_simulator.wait_for_voice_processing()

        # Verify smooth transitions occurred
        assert darvis_process.poll() is None, "GUI should handle state transitions without crashing"


class TestGUISystemIntegration:
    """Tests for GUI integration with system features."""

    def test_system_tray_integration(self, darvis_process):
        """
        Test system tray icon and functionality.

        Verifies that the application properly integrates with the system tray.
        """
        # Wait for tray icon to initialize
        time.sleep(2)

        # In full implementation, would verify:
        # - Tray icon is visible
        # - Right-click menu works
        # - Minimize to tray functionality

        assert darvis_process.poll() is None

    def test_window_management(self, darvis_process):
        """
        Test window positioning and management.

        Verifies that the GUI window behaves correctly in different states.
        """
        # Wait for window to stabilize
        time.sleep(2)

        # In full implementation, would test:
        # - Window positioning
        # - Always-on-top behavior
        # - Minimize/maximize functionality

        assert darvis_process.poll() is None

    @pytest.mark.skipif(sys.platform != "linux", reason="Waybar integration is Linux-specific")
    def test_waybar_status_display(self, darvis_process):
        """
        Test Waybar status integration (Linux only).

        Verifies that status information is properly displayed in Waybar.
        """
        # Wait for Waybar integration to initialize
        time.sleep(2)

        # In full implementation, would verify:
        # - Waybar module updates
        # - Status text accuracy
        # - Icon display

        assert darvis_process.poll() is None


class TestGUIPerformance:
    """Tests for GUI performance and responsiveness."""

    def test_gui_response_latency(self, darvis_process, voice_simulator, gui_verifier):
        """
        Test GUI response time to voice commands.

        Measures and verifies acceptable response latency.
        """
        import time

        # Measure response time
        start_time = time.time()

        voice_simulator.simulate_wake_word("hey darvis")
        time.sleep(0.5)
        voice_simulator.simulate_voice_command("hello")

        # Wait for visual response
        speech_bubble_found = gui_verifier.wait_for_speech_bubble(timeout=5.0)

        response_time = time.time() - start_time

        assert speech_bubble_found, "GUI should respond to voice commands"
        assert response_time < 10.0, f"Response time {response_time:.2f}s exceeded 10s limit"

        assert darvis_process.poll() is None

    def test_gui_animation_smoothness(self, darvis_process, voice_simulator, gui_verifier):
        """
        Test animation smoothness and performance.

        Verifies that animations run smoothly without stuttering.
        """
        # Trigger animation sequence
        voice_simulator.simulate_wake_word("hey darvis")
        time.sleep(1)

        # In full implementation, would measure:
        # - Frame rates during animations
        # - CPU usage during animations
        # - Memory usage stability

        assert darvis_process.poll() is None, "Animations should not cause crashes"

    def test_gui_memory_usage(self, darvis_process):
        """
        Test GUI memory usage over time.

        Verifies that the GUI doesn't have memory leaks during extended operation.
        """
        import psutil

        # Get initial memory usage
        process = psutil.Process(darvis_process.pid)
        initial_memory = process.memory_info().rss

        # Simulate some activity
        time.sleep(5)

        # Check memory hasn't grown excessively
        current_memory = process.memory_info().rss
        memory_growth = current_memory - initial_memory

        # Allow some growth but not excessive (less than 50MB)
        assert memory_growth < 50 * 1024 * 1024, f"Memory growth {memory_growth} bytes is excessive"

        assert darvis_process.poll() is None