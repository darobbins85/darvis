"""
Unit tests for the AI integration module.
"""

import pytest
import subprocess
from unittest.mock import patch, MagicMock, Mock
from darvis.ai import (
    process_ai_query,
    get_latest_session_id,
    cancel_ai_request,
    reset_ai_session,
    is_ai_command,
    current_ai_process,
    current_session_id
)


class TestAI:
    """Test cases for AI functionality."""

    @patch('subprocess.run')
    def test_get_latest_session_id_success(self, mock_subprocess):
        """Test successful retrieval of latest session ID."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "SESSION_ID    STATUS    CREATED\n─────────────────────────────────\nabc123def   Active    2023-01-01"
        mock_subprocess.return_value = mock_result

        result = get_latest_session_id()

        assert result == "abc123def"
        mock_subprocess.assert_called_once_with(
            ["opencode", "session", "list"], capture_output=True, text=True, timeout=10
        )

    @patch('subprocess.run')
    def test_get_latest_session_id_empty_output(self, mock_subprocess):
        """Test handling of empty session list output."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_subprocess.return_value = mock_result

        result = get_latest_session_id()

        assert result == ""

    @patch('subprocess.run')
    def test_get_latest_session_id_exception(self, mock_subprocess):
        """Test handling of subprocess exception."""
        mock_subprocess.side_effect = Exception("Subprocess error")

        result = get_latest_session_id()

        assert result == ""

    @patch('subprocess.Popen')
    @patch('darvis.ai.get_latest_session_id')
    def test_process_ai_query_first_query(self, mock_get_session, mock_popen):
        """Test AI query processing for first query (new session)."""
        mock_process = MagicMock()
        mock_process.communicate.return_value = ("Test response", "")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        mock_get_session.return_value = "session123"

        # Reset global state for test
        import darvis.ai
        darvis.ai.current_session_id = None
        darvis.ai.current_ai_process = None

        response, session_id = process_ai_query("test query")

        assert response == "Test response"
        assert session_id == "session123"
        mock_popen.assert_called_once()
        # Verify the command includes the darvis agent
        args = mock_popen.call_args[0][0]
        assert "--agent" in args
        assert "darvis" in args

    @patch('subprocess.Popen')
    def test_process_ai_query_continuation(self, mock_popen):
        """Test AI query processing for continuation query."""
        mock_process = MagicMock()
        mock_process.communicate.return_value = ("Continuation response", "")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        # Set up global state for continuation
        import darvis.ai
        darvis.ai.current_session_id = "existing_session"
        darvis.ai.current_ai_process = None

        response, session_id = process_ai_query("continuation query")

        assert response == "Continuation response"
        assert session_id == "existing_session"
        mock_popen.assert_called_once()
        # Verify the command uses --continue for continuation
        args = mock_popen.call_args[0][0]
        assert "--continue" in args

    @patch('subprocess.Popen')
    def test_process_ai_query_timeout(self, mock_popen):
        """Test AI query processing with timeout."""
        mock_process = MagicMock()
        mock_process.communicate.side_effect = subprocess.TimeoutExpired(cmd=["test"], timeout=1)
        mock_popen.return_value = mock_process

        # Reset global state for test
        import darvis.ai
        darvis.ai.current_session_id = None
        darvis.ai.current_ai_process = None

        response, session_id = process_ai_query("test query")

        assert response == "AI query timed out"
        assert session_id == ""

    @patch('subprocess.Popen')
    def test_process_ai_query_file_not_found(self, mock_popen):
        """Test AI query processing when opencode is not found."""
        mock_popen.side_effect = FileNotFoundError()

        # Reset global state for test
        import darvis.ai
        darvis.ai.current_session_id = None
        darvis.ai.current_ai_process = None

        response, session_id = process_ai_query("test query")

        assert response == "AI assistance not available (opencode not found)"
        assert session_id == ""

    @patch('subprocess.Popen')
    def test_process_ai_query_general_exception(self, mock_popen):
        """Test AI query processing with general exception."""
        mock_popen.side_effect = Exception("General error")

        # Reset global state for test
        import darvis.ai
        darvis.ai.current_session_id = None
        darvis.ai.current_ai_process = None

        response, session_id = process_ai_query("test query")

        assert "AI error:" in response
        assert session_id == ""

    @patch('darvis.ai.current_ai_process', None)
    def test_cancel_ai_request_no_process(self):
        """Test canceling AI request when no process is running."""
        result = cancel_ai_request()

        assert result is False

    @patch('darvis.ai.current_ai_process')
    def test_cancel_ai_request_with_process(self, mock_process):
        """Test canceling AI request when process is running."""
        mock_process.poll.return_value = None  # Process is still running
        mock_process.terminate = MagicMock()
        mock_process.wait = MagicMock()

        result = cancel_ai_request()

        assert result is True
        mock_process.terminate.assert_called_once()

    @patch('darvis.ai.current_ai_process')
    def test_cancel_ai_request_kill_if_needed(self, mock_process):
        """Test killing AI process if it doesn't terminate gracefully."""
        mock_process.poll.return_value = None  # Process is still running
        mock_process.terminate = MagicMock()
        mock_process.kill = MagicMock()
        mock_process.wait = MagicMock()
        # First call raises TimeoutExpired, second succeeds
        mock_process.wait.side_effect = [subprocess.TimeoutExpired(cmd=["test"], timeout=2), None]

        result = cancel_ai_request()

        assert result is True  # Process was killed successfully
        mock_process.terminate.assert_called_once()
        mock_process.kill.assert_called_once()

    def test_reset_ai_session(self):
        """Test resetting AI session."""
        import darvis.ai
        
        # Set up some state
        darvis.ai.current_session_id = "test_session"
        darvis.ai.conversation_history = ["test"]
        
        reset_ai_session()
        
        assert darvis.ai.current_session_id is None
        assert darvis.ai.conversation_history == []

    @patch('darvis.ai.cancel_ai_request')
    def test_reset_ai_session_with_active_request(self, mock_cancel):
        """Test resetting AI session when there's an active request."""
        import darvis.ai
        darvis.ai.current_ai_process = MagicMock()
        
        mock_cancel.return_value = True
        
        reset_ai_session()
        
        mock_cancel.assert_called_once()

    def test_is_ai_command_positive_cases(self):
        """Test AI command detection for positive cases."""
        positive_queries = [
            "what is the weather?",
            "how do I cook pasta?",
            "why is the sky blue?",
            "explain quantum physics",
            "tell me a joke",
            "calculate 2+2",
            "solve this equation",
            "convert miles to kilometers",
            "translate hello to Spanish",
            "write a poem",
            "create a recipe",
            "generate ideas",
            "code a function"
        ]

        for query in positive_queries:
            assert is_ai_command(query) is True, f"Failed for query: {query}"

    def test_is_ai_command_negative_cases(self):
        """Test AI command detection for negative cases."""
        negative_queries = [
            "open calculator",
            "turn on lights",
            "play music",
            "send email",
            "hello",
            "ok",
            "stop"
        ]

        for query in negative_queries:
            assert is_ai_command(query) is False, f"Failed for query: {query}"

    def test_is_ai_command_mixed_case(self):
        """Test AI command detection with mixed case."""
        assert is_ai_command("WHAT is this?") is True
        assert is_ai_command("EXPLAIN this concept") is True
        assert is_ai_command("Tell me something") is True