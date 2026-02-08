"""
Unit tests for the waybar status module.
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open, ANY
import sys
import os
from pathlib import Path

# Add the darvis module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestWaybarStatus(unittest.TestCase):
    """Test cases for the WaybarStatusManager class and related functions."""

    @patch('platform.system')
    def test_waybar_manager_init_non_linux(self, mock_platform):
        """Test WaybarStatusManager initialization on non-Linux systems."""
        mock_platform.return_value = "Windows"  # or "Darwin" for macOS

        from darvis.waybar_status import WaybarStatusManager

        manager = WaybarStatusManager()

        self.assertFalse(manager.is_linux)
        self.assertFalse(manager.has_waybar)
        self.assertIsNone(manager.fifo_path)
        self.assertFalse(manager._initialized)

    @patch('platform.system')
    @patch('pathlib.Path.exists')
    @patch('os.mkfifo')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    @patch('darvis.waybar_status.WaybarStatusManager._check_waybar_running')
    def test_waybar_manager_setup_success(self, mock_check_waybar, mock_json_dump, mock_open_file,
                                          mock_mkfifo, mock_exists, mock_platform):
        """Test successful WaybarStatusManager setup on Linux."""
        mock_platform.return_value = "Linux"
        mock_check_waybar.return_value = True
        mock_exists.return_value = False  # FIFO doesn't exist yet

        from darvis.waybar_status import WaybarStatusManager

        manager = WaybarStatusManager()

        result = manager.setup()

        self.assertTrue(result)
        self.assertTrue(manager.is_linux)
        self.assertTrue(manager.has_waybar)
        self.assertIsNotNone(manager.fifo_path)
        self.assertTrue(manager._initialized)

    @patch('platform.system')
    @patch('darvis.waybar_status.WaybarStatusManager._check_waybar_running')
    def test_waybar_manager_setup_no_waybar(self, mock_check_waybar, mock_platform):
        """Test WaybarStatusManager setup when waybar is not running."""
        mock_platform.return_value = "Linux"
        mock_check_waybar.return_value = False

        from darvis.waybar_status import WaybarStatusManager

        manager = WaybarStatusManager()

        result = manager.setup()

        self.assertFalse(result)
        self.assertTrue(manager.is_linux)
        self.assertFalse(manager.has_waybar)

    @patch('platform.system')
    @patch('darvis.waybar_status.WaybarStatusManager._check_waybar_running')
    def test_waybar_manager_setup_exception(self, mock_check_waybar, mock_platform):
        """Test WaybarStatusManager setup with exception."""
        mock_platform.return_value = "Linux"
        mock_check_waybar.side_effect = Exception("Test exception")

        from darvis.waybar_status import WaybarStatusManager

        manager = WaybarStatusManager()

        result = manager.setup()

        self.assertFalse(result)

    @patch('platform.system')
    @patch('pathlib.Path.exists')
    @patch('os.mkfifo')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    @patch('darvis.waybar_status.WaybarStatusManager._check_waybar_running')
    def test_update_status_idle(self, mock_check_waybar, mock_json_dump, mock_open_file,
                                mock_mkfifo, mock_exists, mock_platform):
        """Test updating status to idle."""
        mock_platform.return_value = "Linux"
        mock_check_waybar.return_value = True
        mock_exists.return_value = False

        from darvis.waybar_status import WaybarStatusManager

        manager = WaybarStatusManager()
        manager.setup()

        # Reset the mock to clear any calls made during setup
        mock_json_dump.reset_mock()

        manager.update_status("idle", "Test tooltip")

        # Verify JSON was dumped with correct data
        mock_json_dump.assert_called_once_with({"text": "🤖", "class": "idle", "tooltip": "Darvis: Test tooltip"}, ANY)

    @patch('platform.system')
    @patch('pathlib.Path.exists')
    @patch('os.mkfifo')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    @patch('darvis.waybar_status.WaybarStatusManager._check_waybar_running')
    def test_update_status_listening(self, mock_check_waybar, mock_json_dump, mock_open_file,
                                     mock_mkfifo, mock_exists, mock_platform):
        """Test updating status to listening."""
        mock_platform.return_value = "Linux"
        mock_check_waybar.return_value = True
        mock_exists.return_value = False

        from darvis.waybar_status import WaybarStatusManager

        manager = WaybarStatusManager()
        manager.setup()
        # Reset the mock to clear any calls made during setup
        mock_json_dump.reset_mock()

        manager.update_status("listening")

        # Verify JSON was dumped with correct data
        mock_json_dump.assert_called_once_with({"text": "🎤", "class": "listening", "tooltip": "Darvis: Listening"}, ANY)

    @patch('platform.system')
    @patch('pathlib.Path.exists')
    @patch('os.mkfifo')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    @patch('darvis.waybar_status.WaybarStatusManager._check_waybar_running')
    def test_update_status_processing(self, mock_check_waybar, mock_json_dump, mock_open_file,
                                      mock_mkfifo, mock_exists, mock_platform):
        """Test updating status to processing."""
        mock_platform.return_value = "Linux"
        mock_check_waybar.return_value = True
        mock_exists.return_value = False

        from darvis.waybar_status import WaybarStatusManager

        manager = WaybarStatusManager()
        manager.setup()
        # Reset the mock to clear any calls made during setup
        mock_json_dump.reset_mock()

        manager.update_status("processing")

        # Verify JSON was dumped with correct data
        mock_json_dump.assert_called_once_with({"text": "⚙️", "class": "processing", "tooltip": "Darvis: Processing"}, ANY)

    @patch('platform.system')
    @patch('pathlib.Path.exists')
    @patch('os.mkfifo')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    @patch('darvis.waybar_status.WaybarStatusManager._check_waybar_running')
    def test_update_status_thinking(self, mock_check_waybar, mock_json_dump, mock_open_file,
                                    mock_mkfifo, mock_exists, mock_platform):
        """Test updating status to thinking."""
        mock_platform.return_value = "Linux"
        mock_check_waybar.return_value = True
        mock_exists.return_value = False

        from darvis.waybar_status import WaybarStatusManager

        manager = WaybarStatusManager()
        manager.setup()
        # Reset the mock to clear any calls made during setup
        mock_json_dump.reset_mock()

        manager.update_status("thinking")

        # Verify JSON was dumped with correct data
        mock_json_dump.assert_called_once_with({"text": "🧠", "class": "thinking", "tooltip": "Darvis: Thinking"}, ANY)

    @patch('platform.system')
    @patch('pathlib.Path.exists')
    @patch('os.mkfifo')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    @patch('darvis.waybar_status.WaybarStatusManager._check_waybar_running')
    def test_update_status_speaking(self, mock_check_waybar, mock_json_dump, mock_open_file,
                                    mock_mkfifo, mock_exists, mock_platform):
        """Test updating status to speaking."""
        mock_platform.return_value = "Linux"
        mock_check_waybar.return_value = True
        mock_exists.return_value = False

        from darvis.waybar_status import WaybarStatusManager

        manager = WaybarStatusManager()
        manager.setup()
        # Reset the mock to clear any calls made during setup
        mock_json_dump.reset_mock()

        manager.update_status("speaking")

        # Verify JSON was dumped with correct data
        mock_json_dump.assert_called_once_with({"text": "🔊", "class": "speaking", "tooltip": "Darvis: Speaking"}, ANY)

    @patch('platform.system')
    @patch('pathlib.Path.exists')
    @patch('os.mkfifo')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    @patch('darvis.waybar_status.WaybarStatusManager._check_waybar_running')
    def test_update_status_success(self, mock_check_waybar, mock_json_dump, mock_open_file,
                                   mock_mkfifo, mock_exists, mock_platform):
        """Test updating status to success."""
        mock_platform.return_value = "Linux"
        mock_check_waybar.return_value = True
        mock_exists.return_value = False

        from darvis.waybar_status import WaybarStatusManager

        manager = WaybarStatusManager()
        manager.setup()
        # Reset the mock to clear any calls made during setup
        mock_json_dump.reset_mock()

        manager.update_status("success")

        # Verify JSON was dumped with correct data
        mock_json_dump.assert_called_once_with({"text": "✅", "class": "success", "tooltip": "Darvis: Success"}, ANY)

    @patch('platform.system')
    @patch('pathlib.Path.exists')
    @patch('os.mkfifo')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    @patch('darvis.waybar_status.WaybarStatusManager._check_waybar_running')
    def test_update_status_error(self, mock_check_waybar, mock_json_dump, mock_open_file,
                                 mock_mkfifo, mock_exists, mock_platform):
        """Test updating status to error."""
        mock_platform.return_value = "Linux"
        mock_check_waybar.return_value = True
        mock_exists.return_value = False

        from darvis.waybar_status import WaybarStatusManager

        manager = WaybarStatusManager()
        manager.setup()
        # Reset the mock to clear any calls made during setup
        mock_json_dump.reset_mock()

        manager.update_status("error")

        # Verify JSON was dumped with correct data
        mock_json_dump.assert_called_once_with({"text": "❌", "class": "error", "tooltip": "Darvis: Error"}, ANY)

    @patch('platform.system')
    @patch('pathlib.Path.exists')
    @patch('os.mkfifo')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    @patch('darvis.waybar_status.WaybarStatusManager._check_waybar_running')
    def test_update_status_warning(self, mock_check_waybar, mock_json_dump, mock_open_file,
                                   mock_mkfifo, mock_exists, mock_platform):
        """Test updating status to warning."""
        mock_platform.return_value = "Linux"
        mock_check_waybar.return_value = True
        mock_exists.return_value = False

        from darvis.waybar_status import WaybarStatusManager

        manager = WaybarStatusManager()
        manager.setup()
        # Reset the mock to clear any calls made during setup
        mock_json_dump.reset_mock()

        manager.update_status("warning")

        # Verify JSON was dumped with correct data
        mock_json_dump.assert_called_once_with({"text": "⚠️", "class": "warning", "tooltip": "Darvis: Warning"}, ANY)

    @patch('platform.system')
    def test_update_status_no_waybar(self, mock_platform):
        """Test updating status when waybar is not available."""
        mock_platform.return_value = "Windows"

        from darvis.waybar_status import WaybarStatusManager

        manager = WaybarStatusManager()

        # This should not cause an error
        manager.update_status("idle", "Test tooltip")

        # Nothing should happen since waybar is not available

    @patch('platform.system')
    @patch('pathlib.Path.exists')
    @patch('os.mkfifo')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    @patch('darvis.waybar_status.WaybarStatusManager._check_waybar_running')
    def test_update_status_invalid_status(self, mock_check_waybar, mock_json_dump, mock_open_file,
                                          mock_mkfifo, mock_exists, mock_platform):
        """Test updating status with invalid status type."""
        mock_platform.return_value = "Linux"
        mock_check_waybar.return_value = True
        mock_exists.return_value = False

        from darvis.waybar_status import WaybarStatusManager

        manager = WaybarStatusManager()
        manager.setup()
        # Reset the mock to clear any calls made during setup
        mock_json_dump.reset_mock()

        # This should not cause an error
        manager.update_status("invalid_status")

        # JSON dump should not be called for invalid status
        mock_json_dump.assert_not_called()

    @patch('platform.system')
    @patch('pathlib.Path.exists')
    @patch('os.mkfifo')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_write_to_fifo_success(self, mock_json_dump, mock_open_file,
                                   mock_mkfifo, mock_exists, mock_platform):
        """Test writing to FIFO successfully."""
        mock_platform.return_value = "Linux"
        mock_exists.return_value = True  # FIFO exists

        from darvis.waybar_status import WaybarStatusManager

        manager = WaybarStatusManager()
        manager.fifo_path = Path("/tmp/test.fifo")
        manager.has_waybar = True

        test_data = {"text": "🤖", "class": "idle"}

        manager._write_to_fifo(test_data)

        # Verify JSON was dumped and file was written
        mock_json_dump.assert_called_once_with(test_data, ANY)
        mock_open_file.assert_called_once_with(manager.fifo_path, "w")

    @patch('platform.system')
    @patch('pathlib.Path.exists')
    @patch('os.mkfifo')
    @patch('builtins.open', new_callable=mock_open)
    def test_write_to_fifo_exception(self, mock_open_file, mock_mkfifo, mock_exists, mock_platform):
        """Test writing to FIFO with exception."""
        mock_platform.return_value = "Linux"
        mock_exists.return_value = True  # FIFO exists
        mock_open_file.side_effect = Exception("Write error")

        from darvis.waybar_status import WaybarStatusManager

        manager = WaybarStatusManager()
        manager.fifo_path = Path("/tmp/test.fifo")
        manager.has_waybar = True

        test_data = {"text": "🤖", "class": "idle"}

        # This should not raise an exception
        manager._write_to_fifo(test_data)

    @patch('platform.system')
    def test_write_to_fifo_no_path(self, mock_platform):
        """Test writing to FIFO when path is None."""
        mock_platform.return_value = "Linux"

        from darvis.waybar_status import WaybarStatusManager

        manager = WaybarStatusManager()
        manager.fifo_path = None
        manager.has_waybar = True

        test_data = {"text": "🤖", "class": "idle"}

        # This should not cause an error
        manager._write_to_fifo(test_data)

    @patch('subprocess.run')
    def test_check_waybar_running_pgrep_success(self, mock_subprocess):
        """Test checking if waybar is running with pgrep - success."""
        mock_result = MagicMock()
        mock_result.returncode = 0  # waybar is running
        mock_result.stdout = "1234\n"
        mock_subprocess.return_value = mock_result

        from darvis.waybar_status import WaybarStatusManager

        manager = WaybarStatusManager()

        result = manager._check_waybar_running()

        self.assertTrue(result)
        mock_subprocess.assert_called_once_with(["pgrep", "-x", "waybar"], capture_output=True, text=True)

    @patch('subprocess.run')
    def test_check_waybar_running_pgrep_failure(self, mock_subprocess):
        """Test checking if waybar is running with pgrep - failure."""
        mock_result = MagicMock()
        mock_result.returncode = 1  # waybar is not running
        mock_result.stdout = ""
        mock_subprocess.return_value = mock_result

        from darvis.waybar_status import WaybarStatusManager

        manager = WaybarStatusManager()

        result = manager._check_waybar_running()

        self.assertFalse(result)

    @patch('subprocess.run')
    def test_check_waybar_running_pgrep_exception(self, mock_subprocess):
        """Test checking if waybar is running with pgrep - exception."""
        mock_subprocess.side_effect = Exception("Subprocess error")

        from darvis.waybar_status import WaybarStatusManager

        manager = WaybarStatusManager()

        result = manager._check_waybar_running()

        self.assertFalse(result)

    @patch('subprocess.run')
    def test_check_waybar_running_ps_fallback(self, mock_subprocess):
        """Test checking if waybar is running with ps fallback."""
        # First call (pgrep) fails, second call (ps) succeeds
        mock_results = [
            MagicMock(returncode=1, stdout=""),  # pgrep fails
            MagicMock(returncode=0, stdout="1234 ? Ssl  10:00:00 /usr/bin/waybar")  # ps succeeds
        ]
        mock_subprocess.side_effect = mock_results

        from darvis.waybar_status import WaybarStatusManager

        manager = WaybarStatusManager()

        result = manager._check_waybar_running()

        self.assertTrue(result)
        self.assertEqual(mock_subprocess.call_count, 2)

    @patch('platform.system')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.unlink')
    def test_cleanup(self, mock_unlink, mock_exists, mock_platform):
        """Test cleanup function."""
        mock_platform.return_value = "Linux"
        mock_exists.return_value = True

        from darvis.waybar_status import WaybarStatusManager

        manager = WaybarStatusManager()
        manager.fifo_path = Path("/tmp/test.fifo")

        manager.cleanup()

        # Verify the FIFO file was deleted
        mock_unlink.assert_called_once()

    @patch('platform.system')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.unlink')
    def test_cleanup_no_file(self, mock_unlink, mock_exists, mock_platform):
        """Test cleanup function when file doesn't exist."""
        mock_platform.return_value = "Linux"
        mock_exists.return_value = False  # File doesn't exist

        from darvis.waybar_status import WaybarStatusManager

        manager = WaybarStatusManager()
        manager.fifo_path = Path("/tmp/test.fifo")

        # This should not cause an error
        manager.cleanup()

        # unlink should not be called since file doesn't exist
        mock_unlink.assert_not_called()

    @patch('platform.system')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.unlink')
    def test_cleanup_exception(self, mock_unlink, mock_exists, mock_platform):
        """Test cleanup function with exception."""
        mock_platform.return_value = "Linux"
        mock_exists.return_value = True
        mock_unlink.side_effect = Exception("Unlink error")

        from darvis.waybar_status import WaybarStatusManager

        manager = WaybarStatusManager()
        manager.fifo_path = Path("/tmp/test.fifo")

        # This should not raise an exception
        manager.cleanup()


class TestGlobalFunctions(unittest.TestCase):
    """Test global functions in the waybar_status module."""

    def test_get_waybar_manager_singleton(self):
        """Test that get_waybar_manager returns the same instance."""
        from darvis.waybar_status import get_waybar_manager

        # Clear any existing instance
        import darvis.waybar_status
        darvis.waybar_status._waybar_manager = None

        manager1 = get_waybar_manager()
        manager2 = get_waybar_manager()

        # Both should be the same instance
        self.assertIs(manager1, manager2)

    @patch('platform.system')
    @patch('pathlib.Path.exists')
    @patch('os.mkfifo')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    @patch('darvis.waybar_status.WaybarStatusManager._check_waybar_running')
    def test_init_waybar(self, mock_check_waybar, mock_json_dump, mock_open_file,
                         mock_mkfifo, mock_exists, mock_platform):
        """Test init_waybar function."""
        mock_platform.return_value = "Linux"
        mock_check_waybar.return_value = True
        mock_exists.return_value = False

        from darvis.waybar_status import init_waybar

        # Clear any existing instance
        import darvis.waybar_status
        darvis.waybar_status._waybar_manager = None

        result = init_waybar()

        self.assertTrue(result)

    @patch('platform.system')
    @patch('darvis.waybar_status.WaybarStatusManager._check_waybar_running')
    def test_init_waybar_failure(self, mock_check_waybar, mock_platform):
        """Test init_waybar function with failure."""
        mock_platform.return_value = "Linux"
        mock_check_waybar.return_value = False

        from darvis.waybar_status import init_waybar

        # Clear any existing instance
        import darvis.waybar_status
        darvis.waybar_status._waybar_manager = None

        result = init_waybar()

        self.assertFalse(result)

    @patch('json.dump')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.mkfifo')
    @patch('pathlib.Path.exists', return_value=True)
    @patch('platform.system', return_value="Linux")
    def test_update_waybar_status(self, mock_platform, mock_exists, mock_mkfifo, mock_open_file, mock_json_dump):
        """Test update_waybar_status function."""
        mock_platform.return_value = "Linux"
        mock_exists.return_value = True

        # Clear any existing instance
        import darvis.waybar_status
        darvis.waybar_status._waybar_manager = None

        from darvis.waybar_status import update_waybar_status

        # Call the function which should trigger the json.dump
        update_waybar_status("idle", "Test tooltip")

        # Verify JSON was dumped with correct data
        # The call should have been made to the mock
        mock_json_dump.assert_called_once_with({"text": "🤖", "class": "idle", "tooltip": "Darvis: Test tooltip"}, ANY)