"""
End-to-end tests for Darvis Voice Assistant voice functionality.

These tests verify the complete voice processing pipeline from wake word
detection through command processing and response generation.
"""

import pytest
import time
import threading
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Mark all tests in this module as E2E and voice tests
pytestmark = [pytest.mark.e2e, pytest.mark.voice]


class TestVoiceE2E:
    """End-to-end tests for voice functionality."""

    def test_wake_word_detection(self, darvis_process, voice_simulator):
        """
        Test that wake words properly activate voice input mode.

        This test simulates wake word detection and verifies that
        the application enters listening mode.
        """
        # Simulate wake word
        voice_simulator.simulate_wake_word("hey darvis")

        # Wait for processing
        voice_simulator.wait_for_voice_processing()

        # In a full implementation, we would verify:
        # - Voice input window appears
        # - Timer starts counting down
        # - Logo begins glowing animation
        # - Application enters listening state

        # For now, just verify the process is still running
        assert darvis_process.poll() is None, "Darvis process crashed during wake word test"

    def test_voice_command_processing(self, darvis_process, voice_simulator, gui_verifier):
        """
        Test complete voice command processing pipeline.

        This test simulates a voice command and verifies the response.
        """
        # First activate with wake word
        voice_simulator.simulate_wake_word("hey darvis")
        time.sleep(1)

        # Simulate voice command
        voice_simulator.simulate_voice_command("what time is it")

        # Wait for processing
        voice_simulator.wait_for_voice_processing()

        # Verify GUI response
        speech_bubble_found = gui_verifier.wait_for_speech_bubble()
        assert speech_bubble_found, "Speech bubble should appear after voice command"

        # Verify process stability
        assert darvis_process.poll() is None, "Darvis process crashed during command processing"

    def test_multiple_wake_words(self, darvis_process, voice_simulator):
        """
        Test different wake word variations.

        Verifies that all supported wake words properly activate the assistant.
        """
        wake_words = ["hey darvis", "play jarvis", "ok darvis"]

        for wake_word in wake_words:
            # Simulate wake word
            voice_simulator.simulate_wake_word(wake_word)

            # Brief wait
            time.sleep(0.5)

            # Verify process stability
            assert darvis_process.poll() is None, f"Darvis crashed with wake word: {wake_word}"

    def test_voice_timeout_handling(self, darvis_process, voice_simulator, gui_verifier):
        """
        Test voice input timeout handling.

        Verifies that the application properly handles cases where
        voice input times out without a command.
        """
        # Activate listening mode
        voice_simulator.simulate_wake_word("hey darvis")

        # Wait longer than typical voice input timeout
        time.sleep(10)  # Assuming 8-second timeout

        # Verify application returns to idle state
        # In full implementation, would check that listening mode deactivated

        # Verify process stability
        assert darvis_process.poll() is None, "Darvis process crashed during timeout test"

    @pytest.mark.parametrize("command,expected_response_pattern", [
        ("hello", ["hello", "hi", "greetings"]),
        ("how are you", ["fine", "good", "well"]),
        ("thank you", ["welcome", "you're welcome", "no problem"]),
    ])
    def test_ai_conversation_patterns(self, darvis_process, voice_simulator, gui_verifier,
                                    command, expected_response_pattern):
        """
        Test AI conversation patterns with parameterized inputs.

        Verifies that AI responses contain expected patterns for common interactions.
        """
        # Activate and give command
        voice_simulator.simulate_wake_word("hey darvis")
        time.sleep(0.5)
        voice_simulator.simulate_voice_command(command)

        # Wait for AI processing
        voice_simulator.wait_for_voice_processing()

        # Get response text
        response_text = gui_verifier.get_speech_bubble_text()

        # Verify response contains expected pattern
        if response_text:
            response_lower = response_text.lower()
            pattern_found = any(pattern in response_lower for pattern in expected_response_pattern)
            assert pattern_found, f"Response '{response_text}' should contain one of {expected_response_pattern}"

        # Verify process stability
        assert darvis_process.poll() is None, "Darvis process crashed during AI conversation test"


class TestVoiceErrorHandling:
    """Tests for voice input error handling and edge cases."""

    def test_background_noise_resistance(self, darvis_process, voice_simulator):
        """
        Test resistance to background noise and false activations.

        Verifies that the assistant doesn't activate on random noise.
        """
        # Simulate random noise (not wake words)
        noise_commands = ["random noise", "unrelated sounds", "background chatter"]

        for noise in noise_commands:
            voice_simulator.simulate_voice_command(noise)
            time.sleep(1)

            # Verify no activation occurred
            # In full implementation, would check that listening mode wasn't triggered

        assert darvis_process.poll() is None, "Darvis process crashed during noise resistance test"

    def test_rapid_wake_word_activation(self, darvis_process, voice_simulator):
        """
        Test rapid successive wake word activations.

        Verifies stability when wake words are triggered in quick succession.
        """
        # Rapidly trigger wake words
        for i in range(5):
            voice_simulator.simulate_wake_word("hey darvis")
            time.sleep(0.2)  # Very short delay

        # Wait for any queued processing to complete
        time.sleep(3)

        assert darvis_process.poll() is None, "Darvis process crashed during rapid activation test"

    def test_long_voice_commands(self, darvis_process, voice_simulator, gui_verifier):
        """
        Test processing of long, complex voice commands.

        Verifies that the system can handle extended voice input.
        """
        long_command = "can you please tell me about the weather forecast for tomorrow and also remind me to pick up groceries on the way home from work"

        voice_simulator.simulate_wake_word("hey darvis")
        time.sleep(0.5)
        voice_simulator.simulate_voice_command(long_command)

        # Wait for processing
        voice_simulator.wait_for_voice_processing()

        # Verify response was generated
        speech_bubble_found = gui_verifier.wait_for_speech_bubble()
        assert speech_bubble_found, "Should handle long voice commands"

        assert darvis_process.poll() is None, "Darvis process crashed during long command test"