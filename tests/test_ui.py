"""
Unit tests for the Darvis UI module.
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os
import queue
import threading
import socket

# Add the darvis module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestDarvisUI(unittest.TestCase):
    """Test cases for the UI module functions and DarvisGUI class."""

    @patch('tkinter.Tk')
    @patch('tkinter.BooleanVar')
    @patch('queue.Queue')
    @patch('darvis.ui.DarvisGUI.init_web_sync')
    @patch('darvis.ui.DarvisGUI.setup_ui')
    @patch('darvis.ui.DarvisGUI.bind_events')
    @patch('darvis.ui.DarvisGUI.setup_system_tray')
    @patch('darvis.ui.DarvisGUI.start_voice_processing')
    @patch('darvis.ui.DarvisGUI.start_message_processing')
    def test_darvis_gui_initialization(self, mock_start_msg, mock_start_voice, mock_setup_tray,
                                       mock_bind, mock_setup_ui, mock_init_web, mock_queue,
                                       mock_boolvar, mock_tk):
        """Test DarvisGUI initialization."""
        from darvis.ui import DarvisGUI

        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        mock_queue_instance = MagicMock()
        mock_queue.return_value = mock_queue_instance
        mock_boolvar.side_effect = [MagicMock(), MagicMock()]

        gui = DarvisGUI()

        # Check that Tkinter was called
        mock_tk.assert_called_once()
        self.assertIsNotNone(gui.msg_queue)
        self.assertIsNotNone(gui.wake_words)
        self.assertIsNotNone(gui.ai_mode)
        self.assertIsNotNone(gui.listening_mode)

    @patch('tkinter.Tk')
    @patch('tkinter.BooleanVar')
    @patch('queue.Queue')
    @patch('darvis.ui.DarvisGUI.init_web_sync')
    @patch('darvis.ui.DarvisGUI.setup_ui')
    @patch('darvis.ui.DarvisGUI.bind_events')
    @patch('darvis.ui.DarvisGUI.setup_system_tray')
    @patch('darvis.ui.DarvisGUI.start_voice_processing')
    @patch('darvis.ui.DarvisGUI.start_message_processing')
    def test_display_message(self, mock_start_msg, mock_start_voice, mock_setup_tray,
                             mock_bind, mock_setup_ui, mock_init_web, mock_queue,
                             mock_boolvar, mock_tk):
        """Test display_message functionality."""
        from darvis.ui import DarvisGUI

        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        mock_queue_instance = MagicMock()
        mock_queue.return_value = mock_queue_instance
        mock_boolvar.side_effect = [MagicMock(), MagicMock()]

        gui = DarvisGUI()

        # Mock the text widget
        mock_text = MagicMock()
        gui.text_info = mock_text

        # Test display_message
        test_message = "Test message"
        gui.display_message(test_message)

        # Verify the text widget was configured and text was inserted
        mock_text.config.assert_called()
        mock_text.insert.assert_called()
        mock_text.see.assert_called_with('end')

    @patch('tkinter.Tk')
    @patch('tkinter.BooleanVar')
    @patch('queue.Queue')
    @patch('darvis.ui.DarvisGUI.send_to_web')
    @patch('darvis.ui.DarvisGUI.init_web_sync')
    @patch('darvis.ui.DarvisGUI.setup_ui')
    @patch('darvis.ui.DarvisGUI.bind_events')
    @patch('darvis.ui.DarvisGUI.setup_system_tray')
    @patch('darvis.ui.DarvisGUI.start_voice_processing')
    @patch('darvis.ui.DarvisGUI.start_message_processing')
    def test_submit_manual_input(self, mock_start_msg, mock_start_voice, mock_setup_tray,
                                 mock_bind, mock_setup_ui, mock_init_web, mock_send_web,
                                 mock_queue, mock_boolvar, mock_tk):
        """Test manual input submission."""
        from darvis.ui import DarvisGUI

        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        mock_queue_instance = MagicMock()
        mock_queue.return_value = mock_queue_instance
        mock_boolvar.side_effect = [MagicMock(), MagicMock()]

        gui = DarvisGUI()

        # Mock the entry widget
        mock_entry = MagicMock()
        mock_entry.get.return_value = "test input"
        gui.manual_input_entry = mock_entry

        # Mock display_message
        gui.display_message = MagicMock()

        # Mock threading and AI processing to avoid real execution in tests
        with patch('threading.Thread') as mock_thread, \
             patch('darvis.ui.process_ai_query') as mock_ai:

            mock_ai.return_value = ("Test response", "session123")

            # Call submit_manual_input
            gui.submit_manual_input()

            # Verify the input was processed
            mock_entry.get.assert_called_once()
            mock_entry.delete.assert_called_once_with(0, 'end')
            gui.display_message.assert_called()
            mock_send_web.assert_called_once_with("test input")

            # Verify thread was started for AI processing
            mock_thread.assert_called_once()
            # The thread target should be the processing method
            call_args = mock_thread.call_args
            self.assertEqual(call_args[1]['target'], gui._process_ai_query_threaded)
            self.assertEqual(call_args[1]['args'], ("test input",))

    @patch('tkinter.Tk')
    @patch('tkinter.BooleanVar')
    @patch('queue.Queue')
    @patch('darvis.ui.process_ai_query')
    @patch('darvis.ui.DarvisGUI.init_web_sync')
    @patch('darvis.ui.DarvisGUI.setup_ui')
    @patch('darvis.ui.DarvisGUI.bind_events')
    @patch('darvis.ui.DarvisGUI.setup_system_tray')
    @patch('darvis.ui.DarvisGUI.start_voice_processing')
    @patch('darvis.ui.DarvisGUI.start_message_processing')
    def test_process_ai_query_threaded_success(self, mock_start_msg, mock_start_voice, mock_setup_tray,
                                               mock_bind, mock_setup_ui, mock_init_web, mock_ai_process,
                                               mock_queue, mock_boolvar, mock_tk):
        """Test successful AI query processing in thread."""
        from darvis.ui import DarvisGUI

        mock_ai_process.return_value = ("AI response", "session123")

        mock_root = MagicMock()
        # Patch the after method to execute the callback immediately for testing
        mock_root.after = lambda delay, func, *args: func(*args)
        mock_tk.return_value = mock_root
        mock_queue_instance = MagicMock()
        mock_queue.return_value = mock_queue_instance
        mock_boolvar.side_effect = [MagicMock(), MagicMock()]

        gui = DarvisGUI()
        gui._display_ai_response = MagicMock()

        # Test _process_ai_query_threaded
        gui._process_ai_query_threaded("test query")

        # Verify AI was called and response display was scheduled
        mock_ai_process.assert_called_once_with("test query")
        # The _display_ai_response should have been called since we patched after() to execute immediately
        gui._display_ai_response.assert_called_once_with("AI response")

    @patch('tkinter.Tk')
    @patch('tkinter.BooleanVar')
    @patch('queue.Queue')
    @patch('darvis.ui.process_ai_query')
    @patch('darvis.ui.DarvisGUI.init_web_sync')
    @patch('darvis.ui.DarvisGUI.setup_ui')
    @patch('darvis.ui.DarvisGUI.bind_events')
    @patch('darvis.ui.DarvisGUI.setup_system_tray')
    @patch('darvis.ui.DarvisGUI.start_voice_processing')
    @patch('darvis.ui.DarvisGUI.start_message_processing')
    def test_process_ai_query_threaded_error(self, mock_start_msg, mock_start_voice, mock_setup_tray,
                                             mock_bind, mock_setup_ui, mock_init_web, mock_ai_process,
                                             mock_queue, mock_boolvar, mock_tk):
        """Test AI query processing with error in thread."""
        from darvis.ui import DarvisGUI

        mock_ai_process.side_effect = Exception("AI error")

        mock_root = MagicMock()
        # Patch the after method to execute the callback immediately for testing
        mock_root.after = lambda delay, func, *args: func(*args)
        mock_tk.return_value = mock_root
        mock_queue_instance = MagicMock()
        mock_queue.return_value = mock_queue_instance
        mock_boolvar.side_effect = [MagicMock(), MagicMock()]

        gui = DarvisGUI()
        gui._display_ai_response = MagicMock()

        # Test _process_ai_query_threaded with error
        gui._process_ai_query_threaded("test query")

        # Verify error handling
        mock_ai_process.assert_called_once_with("test query")
        # The _display_ai_response should have been called with the error message
        gui._display_ai_response.assert_called_once()
        # Check that the error message was passed to the display function
        error_message = gui._display_ai_response.call_args[0][0]
        self.assertIn("Error processing query", error_message)

    @patch('tkinter.Tk')
    @patch('tkinter.BooleanVar')
    @patch('queue.Queue')
    @patch('darvis.ui.DarvisGUI.init_web_sync')
    @patch('darvis.ui.DarvisGUI.setup_ui')
    @patch('darvis.ui.DarvisGUI.bind_events')
    @patch('darvis.ui.DarvisGUI.setup_system_tray')
    @patch('darvis.ui.DarvisGUI.start_voice_processing')
    @patch('darvis.ui.DarvisGUI.start_message_processing')
    def test_display_ai_response(self, mock_start_msg, mock_start_voice, mock_setup_tray,
                                 mock_bind, mock_setup_ui, mock_init_web, mock_queue,
                                 mock_boolvar, mock_tk):
        """Test displaying AI response."""
        from darvis.ui import DarvisGUI

        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        mock_queue_instance = MagicMock()
        mock_queue.return_value = mock_queue_instance
        mock_boolvar.side_effect = [MagicMock(), MagicMock()]

        gui = DarvisGUI()
        gui.display_message = MagicMock()
        gui.glow_logo = MagicMock()

        # Mock speak function
        with patch('darvis.ui.speak') as mock_speak:
            gui._display_ai_response("Test response")

            # Verify response was displayed
            gui.display_message.assert_any_call("AI: Test response\n")
            # Verify speak was called
            mock_speak.assert_called_once_with("Test response")
            # Verify glow was scheduled to stop
            mock_root.after.assert_called_once()

    @patch('socket.socket')
    def test_init_web_sync_connection_success(self, mock_socket_class):
        """Test web sync initialization with successful connection."""
        from darvis.ui import DarvisGUI

        # Mock socket instance
        mock_socket_instance = MagicMock()
        mock_socket_instance.connect_ex.return_value = 0  # Successful connection
        mock_socket_class.return_value = mock_socket_instance

        gui = DarvisGUI()
        gui.connect_to_web_app = MagicMock()

        gui.init_web_sync()

        # Verify connection was attempted and web sync was enabled
        mock_socket_instance.connect_ex.assert_called()
        gui.connect_to_web_app.assert_called_once()

    @patch('socket.socket')
    def test_init_web_sync_connection_failure(self, mock_socket_class):
        """Test web sync initialization with failed connection."""
        from darvis.ui import DarvisGUI

        # Mock socket instance
        mock_socket_instance = MagicMock()
        mock_socket_instance.connect_ex.return_value = 1  # Failed connection
        mock_socket_class.return_value = mock_socket_instance

        gui = DarvisGUI()
        gui.connect_to_web_app = MagicMock()

        gui.init_web_sync()

        # Verify connection was attempted but web sync was not enabled
        mock_socket_instance.connect_ex.assert_called()
        gui.connect_to_web_app.assert_not_called()
        self.assertFalse(gui.web_sync_enabled)

    @patch('socket.socket')
    def test_init_web_sync_exception_handling(self, mock_socket_class):
        """Test web sync initialization with exception."""
        from darvis.ui import DarvisGUI

        # Mock socket to raise an exception
        mock_socket_class.side_effect = Exception("Socket error")

        gui = DarvisGUI()

        # This should not raise an exception
        gui.init_web_sync()

        # Web sync should remain disabled
        self.assertFalse(gui.web_sync_enabled)

    def test_copy_chat(self):
        """Test copying chat to clipboard."""
        from darvis.ui import DarvisGUI

        gui = DarvisGUI()
        mock_text_widget = MagicMock()
        mock_text_widget.get.return_value = "Test chat content"
        gui.text_info = mock_text_widget
        gui.root = MagicMock()

        gui.copy_chat()

        # Verify text was retrieved and copied to clipboard
        mock_text_widget.get.assert_called_once_with("1.0", "end")
        gui.root.clipboard_clear.assert_called_once()
        gui.root.clipboard_append.assert_called_once_with("Test chat content")

    def test_glow_logo_normal_state(self):
        """Test logo glow functionality - normal state."""
        from darvis.ui import DarvisGUI

        gui = DarvisGUI()
        gui.logo_label = MagicMock()
        gui.base_logo_image = MagicMock()

        gui.glow_logo(False)

        # Verify normal logo was restored
        gui.logo_label.config.assert_called_once()
        self.assertEqual(gui.current_logo_state, "normal")

    def test_glow_logo_wake_state(self):
        """Test logo glow functionality - wake state."""
        from darvis.ui import DarvisGUI

        gui = DarvisGUI()
        gui.logo_label = MagicMock()
        gui.wake_glow_image = MagicMock()

        gui.glow_logo(True, ai_active=False)

        # Verify wake glow was applied
        gui.logo_label.config.assert_called_once()
        self.assertEqual(gui.current_logo_state, "wake")

    def test_glow_logo_ai_state(self):
        """Test logo glow functionality - AI state."""
        from darvis.ui import DarvisGUI

        gui = DarvisGUI()
        gui.logo_label = MagicMock()
        gui.ai_glow_image = MagicMock()

        gui.glow_logo(True, ai_active=True)

        # Verify AI glow was applied
        gui.logo_label.config.assert_called_once()
        self.assertEqual(gui.current_logo_state, "ai")

    def test_create_eye_glow(self):
        """Test eye glow creation."""
        from darvis.ui import DarvisGUI
        from PIL import Image

        # Create a simple test image
        test_image = Image.new('RGBA', (100, 100), (255, 255, 255, 255))

        gui = DarvisGUI()
        result = gui.create_eye_glow(test_image, (255, 0, 0, 255))

        # Verify result is an image
        self.assertIsNotNone(result)
        self.assertEqual(result.size, (100, 100))

    def test_quit_app(self):
        """Test quitting the application."""
        from darvis.ui import DarvisGUI

        gui = DarvisGUI()
        gui.web_socket = MagicMock()
        gui.tray_icon = MagicMock()
        gui.root = MagicMock()

        with patch('darvis.ui.update_waybar_status') as mock_update_waybar:
            gui.quit_app()

            # Verify waybar status was updated
            mock_update_waybar.assert_called_once_with("idle", "Darvis: Exited")
            # Verify socket was disconnected
            gui.web_socket.disconnect.assert_called_once()
            # Verify tray icon was stopped
            gui.tray_icon.stop.assert_called_once()
            # Verify root was quit
            gui.root.quit.assert_called_once()

    def test_quit_app_without_components(self):
        """Test quitting when components are not initialized."""
        from darvis.ui import DarvisGUI

        gui = DarvisGUI()
        gui.web_socket = None
        gui.tray_icon = None
        gui.root = MagicMock()

        with patch('darvis.ui.update_waybar_status') as mock_update_waybar:
            gui.quit_app()

            # Verify waybar status was updated
            mock_update_waybar.assert_called_once_with("idle", "Darvis: Exited")
            # Verify root was quit
            gui.root.quit.assert_called_once()

    def test_quit_app_with_disconnection_error(self):
        """Test quitting when socket disconnection fails."""
        from darvis.ui import DarvisGUI

        gui = DarvisGUI()
        gui.web_socket = MagicMock()
        gui.web_socket.disconnect.side_effect = Exception("Disconnection error")
        gui.tray_icon = MagicMock()
        gui.root = MagicMock()

        with patch('darvis.ui.update_waybar_status'):
            # This should not raise an exception
            gui.quit_app()

            # Tray icon should still be stopped
            gui.tray_icon.stop.assert_called_once()
            # Root should still be quit
            gui.root.quit.assert_called_once()

    @patch('tkinter.Tk')
    @patch('tkinter.BooleanVar')
    @patch('queue.Queue')
    @patch('darvis.ui.DarvisGUI.init_web_sync')
    @patch('darvis.ui.DarvisGUI.setup_ui')
    @patch('darvis.ui.DarvisGUI.bind_events')
    @patch('darvis.ui.DarvisGUI.setup_system_tray')
    @patch('darvis.ui.DarvisGUI.start_voice_processing')
    @patch('darvis.ui.DarvisGUI.start_message_processing')
    def test_send_to_web_when_connected(self, mock_start_msg, mock_start_voice, mock_setup_tray,
                                        mock_bind, mock_setup_ui, mock_init_web, mock_queue,
                                        mock_boolvar, mock_tk):
        """Test sending message to web when connected."""
        from darvis.ui import DarvisGUI

        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        mock_queue_instance = MagicMock()
        mock_queue.return_value = mock_queue_instance
        mock_boolvar.side_effect = [MagicMock(), MagicMock()]

        gui = DarvisGUI()
        gui.web_connected = True
        gui.web_socket = MagicMock()

        gui.send_to_web("test message")

        # Verify message was sent to web
        gui.web_socket.emit.assert_called_once_with("chat_message", {"message": "test message"})

    @patch('tkinter.Tk')
    @patch('tkinter.BooleanVar')
    @patch('queue.Queue')
    @patch('darvis.ui.DarvisGUI.init_web_sync')
    @patch('darvis.ui.DarvisGUI.setup_ui')
    @patch('darvis.ui.DarvisGUI.bind_events')
    @patch('darvis.ui.DarvisGUI.setup_system_tray')
    @patch('darvis.ui.DarvisGUI.start_voice_processing')
    @patch('darvis.ui.DarvisGUI.start_message_processing')
    def test_send_to_web_when_not_connected(self, mock_start_msg, mock_start_voice, mock_setup_tray,
                                            mock_bind, mock_setup_ui, mock_init_web, mock_queue,
                                            mock_boolvar, mock_tk):
        """Test sending message to web when not connected."""
        from darvis.ui import DarvisGUI

        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        mock_queue_instance = MagicMock()
        mock_queue.return_value = mock_queue_instance
        mock_boolvar.side_effect = [MagicMock(), MagicMock()]

        gui = DarvisGUI()
        gui.web_connected = False
        gui.web_socket = MagicMock()

        # This should not cause an error
        gui.send_to_web("test message")

        # Socket should not be called
        gui.web_socket.emit.assert_not_called()

    @patch('tkinter.Tk')
    @patch('tkinter.BooleanVar')
    @patch('queue.Queue')
    @patch('darvis.ui.DarvisGUI.init_web_sync')
    @patch('darvis.ui.DarvisGUI.setup_ui')
    @patch('darvis.ui.DarvisGUI.bind_events')
    @patch('darvis.ui.DarvisGUI.setup_system_tray')
    @patch('darvis.ui.DarvisGUI.start_voice_processing')
    @patch('darvis.ui.DarvisGUI.start_message_processing')
    def test_send_to_web_emit_error(self, mock_start_msg, mock_start_voice, mock_setup_tray,
                                    mock_bind, mock_setup_ui, mock_init_web, mock_queue,
                                    mock_boolvar, mock_tk):
        """Test sending message to web when emit fails."""
        from darvis.ui import DarvisGUI

        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        mock_queue_instance = MagicMock()
        mock_queue.return_value = mock_queue_instance
        mock_boolvar.side_effect = [MagicMock(), MagicMock()]

        gui = DarvisGUI()
        gui.web_connected = True
        gui.web_socket = MagicMock()
        gui.web_socket.emit.side_effect = Exception("Emit error")

        # This should not cause an error
        gui.send_to_web("test message")

        # Socket should be called but error handled
        gui.web_socket.emit.assert_called_once()

    @patch('darvis.ui.update_waybar_status')
    def test__display_ai_response_updates_waybar(self, mock_update_waybar):
        """Test that _display_ai_response updates waybar status."""
        from darvis.ui import DarvisGUI

        gui = DarvisGUI()
        gui.display_message = MagicMock()
        gui.glow_logo = MagicMock()

        with patch('darvis.ui.speak'):
            # Reset the mock call count to ignore any initial calls
            mock_update_waybar.reset_mock()
            gui._display_ai_response("Test response")

            # Verify waybar status was updated
            mock_update_waybar.assert_called_once_with("speaking", "Speaking response...")

    @patch('darvis.ui.update_waybar_status')
    def test__process_ai_query_threaded_updates_waybar(self, mock_update_waybar):
        """Test that _process_ai_query_threaded updates waybar status."""
        from darvis.ui import DarvisGUI

        mock_root = MagicMock()
        with patch('tkinter.Tk', return_value=mock_root), \
             patch('tkinter.BooleanVar', side_effect=[MagicMock(), MagicMock()]), \
             patch('queue.Queue', return_value=MagicMock()), \
             patch('darvis.ui.DarvisGUI.init_web_sync'), \
             patch('darvis.ui.DarvisGUI.setup_ui'), \
             patch('darvis.ui.DarvisGUI.bind_events'), \
             patch('darvis.ui.DarvisGUI.setup_system_tray'), \
             patch('darvis.ui.DarvisGUI.start_voice_processing'), \
             patch('darvis.ui.DarvisGUI.start_message_processing'), \
             patch('darvis.ui.process_ai_query', return_value=("Test response", "session123")):

            gui = DarvisGUI()
            gui._display_ai_response = MagicMock()

            # Reset mock to ignore initial calls
            mock_update_waybar.reset_mock()
            
            gui._process_ai_query_threaded("test query")

            # Verify waybar status was updated
            # Wait for async calls to complete
            import time
            time.sleep(0.1)
            
            # Check that the expected calls were made
            calls_made = [call[0] for call in mock_update_waybar.call_args_list]
            expected_calls = [("thinking", "Thinking about: test query..."), ("success", "Response delivered")]
            
            for expected_call in expected_calls:
                self.assertIn(expected_call, calls_made)


class TestGlobalFunctions(unittest.TestCase):
    """Test global functions in the UI module."""

    def test_init_gui(self):
        """Test initializing GUI instance."""
        from darvis.ui import init_gui, get_gui

        # Clear any existing instance
        import darvis.ui
        darvis.ui._gui_instance = None

        gui = init_gui()

        # Verify instance was created and returned
        self.assertIsNotNone(gui)
        self.assertEqual(gui, get_gui())

    def test_get_gui_none(self):
        """Test getting GUI when none exists."""
        from darvis.ui import get_gui

        # Clear any existing instance
        import darvis.ui
        darvis.ui._gui_instance = None

        result = get_gui()

        # Should return None
        self.assertIsNone(result)

    @patch('darvis.ui.DarvisGUI')
    def test_main_function(self, mock_gui_class):
        """Test main function."""
        from darvis.ui import main

        mock_gui_instance = MagicMock()
        mock_gui_class.return_value = mock_gui_instance

        # This should not raise an exception
        main()

        # Verify GUI was initialized and run
        mock_gui_class.assert_called_once()
        mock_gui_instance.run.assert_called_once()