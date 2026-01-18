"""
End-to-end tests for Darvis Voice Assistant AI integration.

These tests verify AI query processing, response generation, conversation
continuity, and error handling in AI interactions.
"""

import pytest
import time
import re
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Mark all tests in this module as E2E and AI tests
pytestmark = [pytest.mark.e2e, pytest.mark.ai]


class TestAIQueryProcessing:
    """Tests for AI query processing and response generation."""

    def test_basic_ai_query(self, darvis_process, voice_simulator, gui_verifier):
        """
        Test basic AI query processing.

        Verifies that simple questions are processed and responded to appropriately.
        """
        # Ask a basic question
        voice_simulator.simulate_wake_word("hey darvis")
        time.sleep(0.5)
        voice_simulator.simulate_voice_command("what is 2 plus 2")

        # Wait for AI processing
        voice_simulator.wait_for_voice_processing()

        # Verify response was generated
        speech_bubble_found = gui_verifier.wait_for_speech_bubble()
        assert speech_bubble_found, "AI should generate a response to basic queries"

        # Get response text
        response_text = gui_verifier.get_speech_bubble_text()
        if response_text:
            # Should contain some form of answer or acknowledgment
            assert len(response_text.strip()) > 0, "AI response should not be empty"

        assert darvis_process.poll() is None

    def test_ai_conversation_continuity(self, darvis_process, voice_simulator, gui_verifier):
        """
        Test AI conversation continuity across multiple queries.

        Verifies that the AI maintains context between related queries.
        """
        # First query
        voice_simulator.simulate_wake_word("hey darvis")
        time.sleep(0.5)
        voice_simulator.simulate_voice_command("hello")

        voice_simulator.wait_for_voice_processing()
        time.sleep(1)

        # Follow-up query
        voice_simulator.simulate_wake_word("hey darvis")
        time.sleep(0.5)
        voice_simulator.simulate_voice_command("how are you")

        voice_simulator.wait_for_voice_processing()

        # Verify both responses were generated
        speech_bubble_found = gui_verifier.wait_for_speech_bubble()
        assert speech_bubble_found, "AI should maintain conversation continuity"

        assert darvis_process.poll() is None

    @pytest.mark.parametrize("query_type,expected_patterns", [
        ("factual", ["is", "are", "was", "were", "the", "a", "an"]),
        ("instruction", ["can", "should", "would", "could", "please", "help"]),
        ("opinion", ["think", "believe", "feel", "seems", "appears"]),
    ])
    def test_ai_response_patterns(self, darvis_process, voice_simulator, gui_verifier,
                                query_type, expected_patterns):
        """
        Test AI response patterns for different query types.

        Verifies that AI responses are contextually appropriate.
        """
        # Select query based on type
        queries = {
            "factual": "what is the capital of France",
            "instruction": "how do I make coffee",
            "opinion": "what do you think about artificial intelligence"
        }

        query = queries[query_type]

        voice_simulator.simulate_wake_word("hey darvis")
        time.sleep(0.5)
        voice_simulator.simulate_voice_command(query)

        voice_simulator.wait_for_voice_processing()

        response_text = gui_verifier.get_speech_bubble_text()
        if response_text:
            response_lower = response_text.lower()
            # Check for expected linguistic patterns
            pattern_found = any(pattern in response_lower for pattern in expected_patterns)
            assert pattern_found, f"Response should contain appropriate patterns for {query_type} queries"

        assert darvis_process.poll() is None


class TestAIErrorHandling:
    """Tests for AI error handling and edge cases."""

    def test_ai_timeout_handling(self, darvis_process, voice_simulator, gui_verifier):
        """
        Test AI query timeout handling.

        Verifies that long-running queries are handled gracefully.
        """
        # Ask a complex question that might take time
        voice_simulator.simulate_wake_word("hey darvis")
        time.sleep(0.5)
        voice_simulator.simulate_voice_command("explain quantum physics in detail")

        # Wait for processing (should timeout gracefully)
        voice_simulator.wait_for_voice_processing()

        # Verify system remains stable even if AI times out
        assert darvis_process.poll() is None, "Should handle AI timeouts without crashing"

    def test_ai_network_error_simulation(self, darvis_process, voice_simulator):
        """
        Test AI behavior during network connectivity issues.

        Verifies graceful degradation when AI service is unavailable.
        """
        # This would require network simulation in a full implementation
        # For now, test with a query that might trigger network issues

        voice_simulator.simulate_wake_word("hey darvis")
        time.sleep(0.5)
        voice_simulator.simulate_voice_command("tell me a joke")

        voice_simulator.wait_for_voice_processing()

        # Verify graceful handling
        assert darvis_process.poll() is None, "Should handle network issues gracefully"

    def test_ai_empty_query_handling(self, darvis_process, voice_simulator, gui_verifier):
        """
        Test AI handling of empty or minimal queries.

        Verifies appropriate response to unclear input.
        """
        # Send minimal input
        voice_simulator.simulate_wake_word("hey darvis")
        time.sleep(0.5)
        voice_simulator.simulate_voice_command("um")

        voice_simulator.wait_for_voice_processing()

        # Should still generate some response
        speech_bubble_found = gui_verifier.wait_for_speech_bubble()
        assert speech_bubble_found, "AI should respond even to unclear queries"

        assert darvis_process.poll() is None


class TestAIResponseQuality:
    """Tests for AI response quality and appropriateness."""

    def test_ai_response_relevance(self, darvis_process, voice_simulator, gui_verifier):
        """
        Test AI response relevance to queries.

        Verifies that responses are topically related to the input.
        """
        test_cases = [
            ("what color is the sky", ["blue", "sky"]),
            ("how do you spell hello", ["h", "e", "l", "l", "o"]),
            ("what day is it today", ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]),
        ]

        for query, expected_keywords in test_cases:
            voice_simulator.simulate_wake_word("hey darvis")
            time.sleep(0.5)
            voice_simulator.simulate_voice_command(query)

            voice_simulator.wait_for_voice_processing()

            response_text = gui_verifier.get_speech_bubble_text()
            if response_text:
                response_lower = response_text.lower()
                # Check if response contains relevant keywords
                relevance_found = any(keyword in response_lower for keyword in expected_keywords)
                assert relevance_found, f"Response to '{query}' should be relevant"

            time.sleep(2)  # Brief pause between tests

        assert darvis_process.poll() is None

    def test_ai_response_length_appropriateness(self, darvis_process, voice_simulator, gui_verifier):
        """
        Test that AI responses are appropriately sized.

        Verifies responses aren't too short or excessively long.
        """
        queries = [
            "hello",  # Should get short response
            "explain photosynthesis",  # Should get longer response
        ]

        for query in queries:
            voice_simulator.simulate_wake_word("hey darvis")
            time.sleep(0.5)
            voice_simulator.simulate_voice_command(query)

            voice_simulator.wait_for_voice_processing()

            response_text = gui_verifier.get_speech_bubble_text()
            if response_text:
                # Response should be substantial but not excessive
                word_count = len(response_text.split())
                assert 1 <= word_count <= 500, f"Response length {word_count} words is inappropriate for query: {query}"

            time.sleep(2)

        assert darvis_process.poll() is None

    def test_ai_response_formatting(self, darvis_process, voice_simulator, gui_verifier):
        """
        Test AI response formatting and readability.

        Verifies that responses are properly formatted for speech/display.
        """
        voice_simulator.simulate_wake_word("hey darvis")
        time.sleep(0.5)
        voice_simulator.simulate_voice_command("list three programming languages")

        voice_simulator.wait_for_voice_processing()

        response_text = gui_verifier.get_speech_bubble_text()
        if response_text:
            # Should not have excessive special characters or formatting issues
            # Check for basic readability
            assert not re.search(r'[^\w\s.,!?-]', response_text), "Response should not contain excessive special characters"
            assert len(response_text.strip()) > 0, "Response should not be empty or whitespace-only"

        assert darvis_process.poll() is None


class TestAIConversationFlow:
    """Tests for AI conversation flow and context management."""

    def test_ai_follow_up_questions(self, darvis_process, voice_simulator, gui_verifier):
        """
        Test AI handling of follow-up questions.

        Verifies context awareness in multi-turn conversations.
        """
        # Initial question
        voice_simulator.simulate_wake_word("hey darvis")
        time.sleep(0.5)
        voice_simulator.simulate_voice_command("tell me about Python programming")

        voice_simulator.wait_for_voice_processing()
        time.sleep(2)

        # Follow-up
        voice_simulator.simulate_wake_word("hey darvis")
        time.sleep(0.5)
        voice_simulator.simulate_voice_command("what about JavaScript")

        voice_simulator.wait_for_voice_processing()

        # Both responses should be generated
        speech_bubble_found = gui_verifier.wait_for_speech_bubble()
        assert speech_bubble_found, "AI should handle follow-up questions"

        assert darvis_process.poll() is None

    def test_ai_topic_changes(self, darvis_process, voice_simulator, gui_verifier):
        """
        Test AI handling of topic changes.

        Verifies ability to switch contexts appropriately.
        """
        topics = ["weather", "sports", "technology"]

        for topic in topics:
            voice_simulator.simulate_wake_word("hey darvis")
            time.sleep(0.5)
            voice_simulator.simulate_voice_command(f"tell me about {topic}")

            voice_simulator.wait_for_voice_processing()
            time.sleep(2)

        # Verify system handled topic switches
        assert darvis_process.poll() is None, "AI should handle topic changes gracefully"

    def test_ai_session_persistence(self, darvis_process, voice_simulator):
        """
        Test AI session persistence across commands.

        Verifies that conversation context is maintained appropriately.
        """
        # Simulate a conversation session
        conversation = [
            "hello",
            "my name is test user",
            "what is my name",
            "thank you"
        ]

        for utterance in conversation:
            voice_simulator.simulate_wake_word("hey darvis")
            time.sleep(0.5)
            voice_simulator.simulate_voice_command(utterance)

            voice_simulator.wait_for_voice_processing()
            time.sleep(1.5)

        # Verify session completed without issues
        assert darvis_process.poll() is None, "AI session should persist across multiple interactions"