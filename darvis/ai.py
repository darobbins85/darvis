"""
AI integration and intelligent response functionality.
"""

import subprocess
from typing import Tuple

# Global conversation state
conversation_history = []
current_session_id = None


def get_latest_session_id() -> str:
    """Extract the latest session ID from opencode output."""
    try:
        # This would need to be implemented based on opencode's output format
        # For now, return a placeholder
        return ""
    except Exception:
        return ""


def process_ai_query(query: str) -> Tuple[str, str]:
    """
    Process a query using AI assistance.

    Args:
        query: The user's query to process

    Returns:
        Tuple of (response_text, session_id)
    """
    global current_session_id

    try:
        if current_session_id is None:
            # First query: start new session
            result = subprocess.run(
                ["opencode", "run", query],
                capture_output=True,
                text=True,
                timeout=60
            )
            response = (result.stdout or "").strip() or "No response"

            # Get the session ID (this would need proper implementation)
            current_session_id = get_latest_session_id()

            return response, current_session_id or ""
        else:
            # Subsequent queries: use existing session
            result = subprocess.run(
                ["opencode", "run", "--session", current_session_id, query],
                capture_output=True,
                text=True,
                timeout=60
            )
            response = (result.stdout or "").strip() or "No response"
            return response, current_session_id

    except subprocess.TimeoutExpired:
        return "AI query timed out", ""
    except FileNotFoundError:
        return "AI assistance not available (opencode not found)", ""
    except Exception as e:
        return f"AI error: {str(e)}", ""


def reset_ai_session() -> None:
    """Reset the AI conversation session."""
    global current_session_id, conversation_history
    current_session_id = None
    conversation_history = []


def is_ai_command(query: str) -> bool:
    """
    Determine if a query should be handled by AI.

    This is a simple heuristic - in a real implementation,
    this might use NLP to classify the query intent.

    Args:
        query: The user's query

    Returns:
        True if the query should use AI, False for local processing
    """
    query_lower = query.lower()

    # Handle obvious AI queries
    ai_indicators = [
        "what", "how", "why", "explain", "tell me",
        "calculate", "solve", "convert", "translate",
        "write", "create", "generate", "code"
    ]

    return any(indicator in query_lower for indicator in ai_indicators)