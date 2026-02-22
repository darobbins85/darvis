# AGENTS.md - Development Guide for Darvis Voice Assistant

## Build/Lint/Test Commands

**Run Application:**
- `source venv/bin/activate && python3 -m darvis.ui` - Execute the main application with dependencies
- `./run.sh` - Clean launcher script with proper environment setup (web + desktop)
- Desktop menu: Search for "Darvis Voice Assistant" after running `./install-desktop.sh`

**Desktop Integration:**
- `./install-desktop.sh` - Install as system application with icon in menu
- Creates desktop entry in `~/.local/share/applications/`
- Adds icon to `~/.local/share/icons/`
- Updates desktop database for menu integration

**Assets:**
- `assets/darvis-black.png` - Original high-resolution logo
- `assets/darvis-logo-hires.png` - High-resolution transparent version
- `assets/darvis-logo.png` - UI-sized logo (150x150) with transparent background
- `darvis.desktop` - Desktop integration file
- `run.sh` - Primary launcher (web + desktop)
- `launch-darvis.sh` - Desktop-only launcher (alternative)
- `install-desktop.sh` - Desktop integration installer

**Linting (recommended setup):**
- `flake8 darvis/` - Check code style and errors across all modules
- `pylint darvis/` - Comprehensive code analysis
- `black darvis/ --check` - Check formatting compliance

**Formatting:**
- `black darvis/` - Auto-format all modules
- `isort darvis/` - Sort import statements across modules

**Testing (automated test suite):**
- `source venv/bin/activate && python -m pytest tests/` - Run complete test suite (29 tests, 40% coverage)
- `source venv/bin/activate && python -m pytest tests/ --cov=darvis --cov-report=html` - Run with coverage report
- `source venv/bin/activate && python -m pytest tests/test_gui.py` - Run GUI-specific tests
- `source venv/bin/activate && python -m pytest tests/e2e/` - Run E2E test suite (requires full app startup)
- `source venv/bin/activate && python -m pytest tests/e2e/ -m voice` - Run voice-related E2E tests
- `source venv/bin/activate && python -m pytest tests/e2e/ -m gui` - Run GUI-related E2E tests
- `source venv/bin/activate && python -m pytest tests/e2e/ -m ai` - Run AI-related E2E tests
- `source venv/bin/activate && python -m pytest tests/e2e/ -m apps` - Run application launching E2E tests
- Manual testing: Run `python3 -m darvis.ui` and test voice commands
- Microphone test: `python3 -c "import darvis.speech; darvis.speech.list_microphones()"`

## Working Directory Configuration

**Default Working Directory:**
- `DEFAULT_WORKING_DIR` in `darvis/config.py` - Set to user's home folder (`Path.home()`)
- Use `get_default_working_directory()` function to get the configured working directory
- All file operations should reference this instead of hardcoded paths
- This allows Darvis to access files across the entire home directory

## Code Style Guidelines

**Imports:**
- Standard library imports first, then third-party packages
- One import per line, use `import X` or `from X import Y`
- Group related imports with blank lines between groups

**Naming Conventions:**
- Functions: `snake_case` (e.g., `speak()`, `listen()`)
- Variables: `snake_case` (e.g., `wake_words`, `ai_mode`)
- Constants: `UPPER_CASE` (not currently used)
- Classes: `PascalCase` (not currently used)

**Formatting:**
- 4-space indentation
- Line length: ~100 characters
- Blank lines between function definitions
- Use double quotes for strings

**Error Handling:**
- Use try/except blocks for external operations (microphone, subprocess, etc.)
- Print error messages to console for debugging
- Handle specific exceptions (OSError, TimeoutExpired, etc.)

**Best Practices:**
- Add docstrings to functions (future enhancement)
- Use descriptive variable names
- Separate concerns into functions
- Handle global state carefully in threaded applications</content>
<parameter name="filePath">/home/david/Code/github/darobbins85/darvis/AGENTS.md