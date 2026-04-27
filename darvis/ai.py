"""
AI integration and intelligent response functionality.
"""

import subprocess
from typing import Tuple

# Global conversation state
conversation_history = []
current_ai_process = None

CLAUDE_MODEL = "claude-sonnet-4-6"
AI_BACKEND = "claude"   # "claude" | "ollama"
OLLAMA_MODEL = None     # active Ollama model name when backend is "ollama"


def get_available_ollama_models() -> list:
    """Return model names from `ollama ls`, empty list on failure."""
    try:
        result = subprocess.run(
            ["ollama", "ls"], capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return []
        lines = result.stdout.strip().split("\n")
        models = []
        for line in lines[1:]:   # skip header row
            parts = line.split()
            if parts:
                models.append(parts[0])
        return models
    except Exception:
        return []


def set_ai_backend(backend: str, model: str = None) -> None:
    """Switch the active AI backend.  backend: 'claude' | 'ollama'"""
    global AI_BACKEND, OLLAMA_MODEL
    AI_BACKEND = backend
    OLLAMA_MODEL = model


def process_ai_query(query: str) -> Tuple[str, str]:
    """
    Process a query using AI assistance.

    Uses the Claude CLI directly when AI_BACKEND == 'claude', or
    `ollama launch claude` with the selected Ollama model otherwise.

    Args:
        query: The user's query to process

    Returns:
        Tuple of (response_text, session_marker)
    """
    global current_ai_process

    is_first = len(conversation_history) == 0
    conversation_history.append(query)

    try:
        if AI_BACKEND == "ollama" and OLLAMA_MODEL:
            base = ["ollama", "launch", "claude", "--model", OLLAMA_MODEL, "--yes", "--"]
            command = base + (["-p", query] if is_first else ["-c", "-p", query])
        else:
            command = (
                ["claude", "--model", CLAUDE_MODEL, "-p", query]
                if is_first
                else ["claude", "--model", CLAUDE_MODEL, "-c", "-p", query]
            )

        print(f"DEBUG: Executing command: {' '.join(command)}")
        current_ai_process = subprocess.Popen(
            command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True
        )
        print("DEBUG: process started, waiting for output...")
        try:
            stdout, stderr = current_ai_process.communicate(timeout=60)
            print(f"DEBUG: process completed with returncode={current_ai_process.returncode}")
            print(f"DEBUG: stdout len={len(stdout) if stdout else 0}, stderr len={len(stderr) if stderr else 0}")
            print(f"DEBUG: stdout={repr(stdout[:500]) if stdout else 'empty'}")
            print(f"DEBUG: stderr={repr(stderr[:500]) if stderr else 'empty'}")
            result = subprocess.CompletedProcess(
                command, current_ai_process.returncode, stdout, stderr
            )
        except subprocess.TimeoutExpired:
            print("DEBUG: process timed out, killing...")
            current_ai_process.kill()
            stdout, stderr = current_ai_process.communicate()
            print(f"DEBUG: killed process, got stdout={stdout[:200] if stdout else 'none'}")
            return "AI query timed out", ""
        finally:
            current_ai_process = None

        if result.returncode != 0 and stderr:
            print(f"DEBUG: stderr: {stderr}")

        response = (result.stdout or "").strip() or "No response"
        return response, AI_BACKEND

    except subprocess.TimeoutExpired:
        return "AI query timed out", ""
    except FileNotFoundError:
        backend_name = "ollama" if AI_BACKEND == "ollama" else "claude"
        return f"AI assistance not available ({backend_name} not found)", ""
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
    global conversation_history
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
