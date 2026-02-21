"""
AI integration and intelligent response functionality.
"""

import os
import subprocess
from typing import Tuple

# Global conversation state
conversation_history = []
current_session_id = None
current_ai_process = None  # Track the current AI subprocess for cancellation


def _get_opencode_cmd() -> str:
    """Get the opencode command, checking PATH and common locations."""
    # First try PATH
    result = subprocess.run(["which", "opencode"], capture_output=True, text=True)
    if result.returncode == 0:
        return "opencode"

    # Try home directory location
    home_opencode = os.path.expanduser("~/.opencode/bin/opencode")
    if os.path.isfile(home_opencode) and os.access(home_opencode, os.X_OK):
        return home_opencode

    # Fall back to PATH
    return "opencode"


# Get the opencode command once at module load
OPENCODE_CMD = _get_opencode_cmd()


def get_latest_session_id() -> str:
    """Extract the latest session ID from opencode session list."""
    try:
        result = subprocess.run(
            [OPENCODE_CMD, "session", "list"], capture_output=True, text=True, timeout=10
        )

        if result.returncode == 0 and result.stdout:
            # Parse the session list output
            lines = result.stdout.strip().split("\n")
            # Skip header (line 0) and separator (line 1), get first data line
            if len(lines) >= 3:  # Need header, separator, and at least one data line
                # Get the first data line (most recent session)
                first_data_line = lines[2].strip()
                if first_data_line and not first_data_line.startswith("─"):
                    session_id = first_data_line.split()[0]
                    print(f"DEBUG: Extracted session ID: {session_id}")
                    return session_id

        return ""
    except Exception as e:
        print(f"DEBUG: Error getting session ID: {e}")
        return ""


def process_ai_query(query: str) -> Tuple[str, str]:
    """
    Process a query using AI assistance.

    Args:
        query: The user's query to process

    Returns:
        Tuple of (response_text, session_id)
    """
    global current_session_id, current_ai_process

    try:
        if current_session_id is None:
            # First query: start new session with darvis agent
            command = [OPENCODE_CMD, "run", "--agent", "darvis", query]
            print(f"DEBUG: Executing command: {' '.join(command)}")
            current_ai_process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            try:
                stdout, stderr = current_ai_process.communicate(timeout=300)
                result = subprocess.CompletedProcess(
                    command, current_ai_process.returncode, stdout, stderr
                )
            finally:
                current_ai_process = None
            response = (result.stdout or "").strip() or "No response"

            # Get the session ID (this would need proper implementation)
            current_session_id = get_latest_session_id()
            print(f"DEBUG: New session ID: {current_session_id}")

            return response, current_session_id or ""
        else:
            # Subsequent queries: continue the last session with @darvis prefix
            # This ensures the session continues with the darvis agent
            darvis_query = f"@darvis {query}"
            command = [OPENCODE_CMD, "run", "--session", current_session_id, darvis_query]
            print(f"DEBUG: Executing command: {' '.join(command)}")
            current_ai_process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            try:
                stdout, stderr = current_ai_process.communicate(timeout=300)
                result = subprocess.CompletedProcess(
                    command, current_ai_process.returncode, stdout, stderr
                )
                if stderr:
                    print(f"DEBUG: stderr: {stderr}")
            finally:
                current_ai_process = None
            response = (result.stdout or "").strip() or "No response"
            print(f"DEBUG: Response: {response[:100]}...")
            return response, current_session_id

    except subprocess.TimeoutExpired:
        return "AI query timed out", ""
    except FileNotFoundError:
        return "AI assistance not available (opencode not found)", ""
    except Exception as e:
        return f"AI error: {str(e)}", ""


def cancel_ai_request() -> bool:
    """Cancel the current AI request if one is running.

    Returns:
        True if a request was cancelled, False if no request was running
    """
    global current_ai_process
    if current_ai_process and current_ai_process.poll() is None:
        try:
            current_ai_process.terminate()
            # Wait a bit for graceful termination
            try:
                current_ai_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't terminate gracefully
                current_ai_process.kill()
                current_ai_process.wait()
            current_ai_process = None
            return True
        except Exception:
            current_ai_process = None
            return False
    return False


def reset_ai_session() -> None:
    """Reset the AI conversation session."""
    global current_session_id, conversation_history
    current_session_id = None
    conversation_history = []
    if current_ai_process:
        cancel_ai_request()


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
        "what",
        "how",
        "why",
        "explain",
        "tell me",
        "calculate",
        "solve",
        "convert",
        "translate",
        "write",
        "create",
        "generate",
        "code",
    ]

    return any(indicator in query_lower for indicator in ai_indicators)
