import sqlite3
import os
from pathlib import Path
from contextlib import contextmanager

DB_PATH = Path.home() / ".darvis" / "sessions.db"


def get_db_path():
    os.makedirs(Path.home() / ".darvis", exist_ok=True)
    return DB_PATH


@contextmanager
def get_db():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                session_number INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
            );
        """)


def create_user(username, password_hash):
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )
        return cursor.lastrowid


def get_user_by_username(username):
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()


def get_user_by_id(user_id):
    with get_db() as conn:
        return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def create_session(user_id, name, session_number):
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO sessions (user_id, name, session_number) VALUES (?, ?, ?)",
            (user_id, name, session_number),
        )
        return cursor.lastrowid


def get_user_sessions(user_id):
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM sessions WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        ).fetchall()


def get_session_by_id(session_id):
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()


def update_session_name(session_id, name):
    with get_db() as conn:
        conn.execute(
            "UPDATE sessions SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (name, session_id),
        )


def delete_session(session_id):
    with get_db() as conn:
        conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))


def get_next_session_number(user_id):
    with get_db() as conn:
        result = conn.execute(
            "SELECT MAX(session_number) as max_num FROM sessions WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        return (result["max_num"] or 0) + 1


def add_message(session_id, role, content):
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content),
        )
        conn.execute(
            "UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (session_id,),
        )
        return cursor.lastrowid


def get_session_messages(session_id):
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM messages WHERE session_id = ? ORDER BY created_at ASC",
            (session_id,),
        ).fetchall()


def get_or_create_default_session(user_id):
    sessions = get_user_sessions(user_id)
    if sessions:
        return sessions[0]

    session_num = get_next_session_number(user_id)
    session_id = create_session(user_id, f"Session {session_num}", session_num)
    return get_session_by_id(session_id)
