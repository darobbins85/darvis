# Multi-User Sessions Implementation Plan

**Date:** 2026-03-18  
**Feature:** Multi-User Authentication & Session Management  
**Goal:** Enable multiple users to sign up, log in, and maintain separate chat session histories

---

## Overview

Add user authentication and session management to Darvis so multiple family members can use the voice assistant on the same network, each with their own chat history and sessions.

**Tech Stack:** SQLite (built-in), Flask-Login (existing), Werkzeug (existing)

---

## Data Model

### Database Schema (SQLite)

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    session_number INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);
```

### Database File
- Location: ~/.darvis/sessions.db (user's home directory)

---

## Task 1: Database Setup

**Files:**
- Create: darvis/database.py

- [ ] Step 1: Create database module with tables and CRUD functions
- [ ] Step 2: Test database creation
- [ ] Step 3: Commit

---

## Task 2: User Authentication with Database

**Files:**
- Modify: web_chat.py

- [ ] Step 1: Replace simple User class with database-backed auth
- [ ] Step 2: Update login to verify users from DB
- [ ] Step 3: Add signup route with validation
- [ ] Step 4: Commit

---

## Task 3: Session Management API

**Files:**
- Modify: web_chat.py

- [ ] Step 1: Add GET/POST /api/sessions endpoint
- [ ] Step 2: Add PUT/DELETE /api/sessions/<id> endpoint
- [ ] Step 3: Add GET/POST /api/sessions/<id>/messages endpoint
- [ ] Step 4: Commit

---

## Task 4: Create Signup Template

**Files:**
- Create: web_templates/signup.html
- Modify: web_templates/login.html

- [ ] Step 1: Create signup page with username/password form
- [ ] Step 2: Add signup link to login page
- [ ] Step 3: Commit

---

## Task 5: Update Chat UI with Session Selector

**Files:**
- Modify: web_templates/index.html

- [ ] Step 1: Add session sidebar HTML structure
- [ ] Step 2: Add session management JavaScript (load, switch, create)
- [ ] Step 3: Add CSS for sidebar layout
- [ ] Step 4: Add /api/user endpoint
- [ ] Step 5: Commit

---

## Task 6: Wire Up Messages with Sessions

**Files:**
- Modify: web_chat.py, web_templates/index.html

- [ ] Step 1: Update chat_message handler to save to DB
- [ ] Step 2: Update sendMessage JS to include session_id
- [ ] Step 3: Commit

---

## Task 7: Rename and Delete Sessions

**Files:**
- Modify: web_templates/index.html

- [ ] Step 1: Add rename session functionality
- [ ] Step 2: Add delete session functionality
- [ ] Step 3: Commit

---

## Summary

| Task | Description |
|------|-------------|
| 1 | SQLite database with users, sessions, messages tables |
| 2 | Database-backed user authentication |
| 3 | Session and message API endpoints |
| 4 | Signup page and login updates |
| 5 | Session selector sidebar UI |
| 6 | Persist messages to database per session |
| 7 | Rename and delete session features |
