"""
Unit tests for the application detection module.
"""

import pytest
from unittest.mock import patch, mock_open, MagicMock
from darvis.apps import (
    find_app_command, is_command_available, parse_desktop_file, open_app
)


class TestApps:
    """Test cases for application detection and launching."""

    @patch('darvis.apps.is_command_available')
    def test_find_app_command_direct_mapping(self, mock_is_available):
        """Test finding app via direct command mapping."""
        mock_is_available.return_value = True

        result = find_app_command("firefox")

        assert result == "firefox"
        mock_is_available.assert_called_with("firefox")

    @patch('darvis.apps.is_command_available')
    def test_find_app_command_variant_mapping(self, mock_is_available):
        """Test finding app via variant command mapping."""
        mock_is_available.side_effect = lambda cmd: cmd == "chromium"

        result = find_app_command("chrome")

        assert result == "chromium"

    @patch('darvis.apps.is_command_available')
    @patch('builtins.open', new_callable=mock_open)
    @patch('glob.glob')
    def test_find_app_command_desktop_file(self, mock_glob, mock_file, mock_is_available):
        """Test finding app via desktop file parsing."""
        mock_glob.return_value = ["/usr/share/applications/test.desktop"]
        mock_file.return_value.read.return_value = "[Desktop Entry]\nExec=firefox %u\n"
        mock_is_available.return_value = True

        result = find_app_command("firefox")

        assert result == "firefox"

    @patch('subprocess.run')
    def test_is_command_available_true(self, mock_run):
        """Test command availability check - available."""
        mock_run.return_value = MagicMock()

        result = is_command_available("ls")

        assert result is True
        mock_run.assert_called_once_with(["ls"], capture_output=True, check=False)

    @patch('subprocess.run')
    def test_is_command_available_false(self, mock_run):
        """Test command availability check - not available."""
        mock_run.side_effect = FileNotFoundError()

        result = is_command_available("nonexistent")

        assert result is False

    def test_parse_desktop_file_success(self):
        """Test successful desktop file parsing."""
        desktop_content = """[Desktop Entry]
Name=Firefox
Exec=firefox %u
Type=Application
"""

        with patch('builtins.open', mock_open(read_data=desktop_content)):
            result = parse_desktop_file("/fake/path/firefox.desktop")

        assert result == "firefox"

    def test_parse_desktop_file_no_exec(self):
        """Test desktop file parsing with no Exec line."""
        desktop_content = """[Desktop Entry]
Name=Test App
Type=Application
"""

        with patch('builtins.open', mock_open(read_data=desktop_content)):
            result = parse_desktop_file("/fake/path/test.desktop")

        assert result == ""

    @patch('subprocess.Popen')
    def test_open_app_web_service(self, mock_popen):
        """Test opening web service."""
        result = open_app("youtube")

        assert result == "Opening youtube"
        mock_popen.assert_called_once_with(["xdg-open", "https://youtube.com"])

    @patch('subprocess.Popen')
    def test_open_app_basecamp_web_service(self, mock_popen):
        """Test opening Basecamp web service."""
        result = open_app("basecamp")

        assert result == "Opening basecamp"
        mock_popen.assert_called_once_with(["xdg-open", "https://basecamp.com"])

    @patch('subprocess.Popen')
    def test_open_app_various_web_services(self, mock_popen):
        """Test various web services are properly handled."""
        test_cases = [
            ("slack", "https://slack.com"),
            ("discord", "https://discord.com"),
            ("zoom", "https://zoom.us"),
            ("notion", "https://notion.so"),
            ("jira", "https://jira.atlassian.com"),
        ]

        for service, expected_url in test_cases:
            mock_popen.reset_mock()
            result = open_app(service)
            assert result == f"Opening {service}"
            mock_popen.assert_called_once_with(["xdg-open", expected_url])

    @patch('darvis.apps.find_app_command')
    @patch('subprocess.Popen')
    def test_open_app_bluetooth_manager(self, mock_popen, mock_find):
        """Test opening bluetooth manager with space in name."""
        mock_find.return_value = "blueman-manager"

        result = open_app("bluetooth manager")

        assert result == "Opening bluetooth manager"
        mock_find.assert_called_once_with("bluetooth manager")
        mock_popen.assert_called_once_with(["blueman-manager"])

    @patch('darvis.apps.find_app_command')
    def test_open_app_not_found_error_message(self, mock_find):
        """Test improved error message for not found apps."""
        mock_find.return_value = ""

        result = open_app("nonexistentapp")

        assert "not installed or not found" in result
        assert "pacman -S" in result

    @patch('darvis.apps.find_app_command')
    @patch('subprocess.Popen')
    def test_open_app_local_app_success(self, mock_popen, mock_find):
        """Test opening local application successfully."""
        mock_find.return_value = "firefox"

        result = open_app("firefox")

        assert result == "Opening firefox"
        mock_popen.assert_called_once_with(["firefox"])

    @patch('darvis.apps.find_app_command')
    def test_open_app_not_found(self, mock_find):
        """Test opening app that is not found."""
        mock_find.return_value = ""

        result = open_app("nonexistent")

        assert result == "'nonexistent' is not installed or not found on this system. Try: pacman -S nonexistent (on Arch) or check if it's installed in a custom location"

    @patch('darvis.apps.find_app_command')
    @patch('subprocess.Popen')
    def test_open_app_launch_error(self, mock_popen, mock_find):
        """Test handling of app launch errors."""
        mock_find.return_value = "badapp"
        mock_popen.side_effect = Exception("Launch failed")

        result = open_app("badapp")

        assert "Error launching badapp" in result

    def test_gaming_apps_detection(self):
        """Test that gaming applications can be detected."""
        from darvis.apps import find_app_command

        # Test that gaming app detection doesn't crash
        # (Even if not installed, should return empty string, not error)
        gaming_apps = ['steam', 'lutris', 'heroic', 'wine', 'bottles']
        for app in gaming_apps:
            result = find_app_command(app)
            # Should return either a command string or empty string, not crash
            assert isinstance(result, str), f"find_app_command({app}) should return string"