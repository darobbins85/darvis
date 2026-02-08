"""
Unit tests for the Darvis GUI (ui.py).

Tests GUI constructor, widget creation, and basic functionality.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the darvis module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestDarvisGUI(unittest.TestCase):
    """Test cases for the DarvisGUI class."""

    @patch('tkinter.Tk')
    @patch('tkinter.BooleanVar')
    @patch('queue.Queue')
    @patch('darvis.ui.DarvisGUI.init_web_sync')
    @patch('darvis.ui.DarvisGUI.setup_ui')
    @patch('darvis.ui.DarvisGUI.bind_events')
    @patch('darvis.ui.DarvisGUI.setup_system_tray')
    @patch('darvis.ui.DarvisGUI.start_voice_processing')
    @patch('darvis.ui.DarvisGUI.start_message_processing')
    def test_constructor_basic(self, mock_start_msg, mock_start_voice, mock_setup_tray,
                              mock_bind, mock_setup_ui, mock_init_web, mock_queue,
                              mock_boolvar, mock_tk):
        """Test that DarvisGUI constructor initializes basic attributes."""
        from darvis.ui import DarvisGUI

        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        mock_queue_instance = MagicMock()
        mock_queue.return_value = mock_queue_instance
        mock_boolvar.side_effect = [MagicMock(), MagicMock()]

        gui = DarvisGUI()

        # Check that Tkinter was called
        mock_tk.assert_called_once()

        # Check basic attributes
        self.assertIsNotNone(gui.msg_queue)
        self.assertIsNotNone(gui.wake_words)
        self.assertIsNotNone(gui.ai_mode)
        self.assertIsNotNone(gui.listening_mode)

        # Check web sync attributes
        self.assertFalse(gui.web_sync_enabled)
        self.assertIsNone(gui.web_socket)
        self.assertFalse(gui.web_connected)

    @patch('tkinter.Tk')
    @patch('tkinter.BooleanVar')
    @patch('queue.Queue')
    @patch('darvis.ui.DarvisGUI.init_web_sync')
    @patch('darvis.ui.DarvisGUI.setup_ui')
    @patch('darvis.ui.DarvisGUI.bind_events')
    @patch('darvis.ui.DarvisGUI.setup_system_tray')
    @patch('darvis.ui.DarvisGUI.start_voice_processing')
    @patch('darvis.ui.DarvisGUI.start_message_processing')
    def test_setup_ui_creates_widgets(self, mock_start_msg, mock_start_voice, mock_setup_tray,
                                     mock_bind, mock_setup_ui, mock_init_web, mock_queue,
                                     mock_boolvar, mock_tk):
        """Test that setup_ui creates the expected widgets."""
        from darvis.ui import DarvisGUI

        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        mock_queue_instance = MagicMock()
        mock_queue.return_value = mock_queue_instance
        mock_boolvar.side_effect = [MagicMock(), MagicMock()]

        gui = DarvisGUI()

        # Mock the text widget
        mock_text = MagicMock()
        mock_root.nametowidget = MagicMock(return_value=mock_text)

        # Call setup_ui
        gui.setup_ui()

        # Check that widgets were created on the root
        self.assertTrue(mock_root.configure.called)
        self.assertTrue(mock_root.geometry.called)

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
        """Test that display_message adds text to the text widget."""
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
        mock_text.insert.assert_called_with('end', test_message)
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
    def test_process_ai_query_success(self, mock_start_msg, mock_start_voice, mock_setup_tray,
                                     mock_bind, mock_setup_ui, mock_init_web, mock_ai_process,
                                     mock_queue, mock_boolvar, mock_tk):
        """Test successful AI query processing."""
        from darvis.ui import DarvisGUI

        mock_ai_process.return_value = ("AI response", "session123")

        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        mock_queue_instance = MagicMock()
        mock_queue.return_value = mock_queue_instance
        mock_boolvar.side_effect = [MagicMock(), MagicMock()]

        gui = DarvisGUI()
        gui.display_message = MagicMock()

        # Test _process_ai_query_threaded
        gui._process_ai_query_threaded("test query")

        # Verify AI was called and response displayed
        mock_ai_process.assert_called_once_with("test query")
        gui.display_message.assert_called_once_with("AI: AI response\n")

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
    def test_process_ai_query_error(self, mock_start_msg, mock_start_voice, mock_setup_tray,
                                   mock_bind, mock_setup_ui, mock_init_web, mock_ai_process,
                                   mock_queue, mock_boolvar, mock_tk):
        """Test AI query processing with error."""
        from darvis.ui import DarvisGUI

        mock_ai_process.side_effect = Exception("AI error")

        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        mock_queue_instance = MagicMock()
        mock_queue.return_value = mock_queue_instance
        mock_boolvar.side_effect = [MagicMock(), MagicMock()]

        gui = DarvisGUI()
        gui.display_message = MagicMock()

        # Test _process_ai_query_threaded with error
        gui._process_ai_query_threaded("test query")

        # Verify error handling
        mock_ai_process.assert_called_once_with("test query")
        gui.display_message.assert_called_once()
        # Check that error message was displayed
        call_args = gui.display_message.call_args[0][0]
        self.assertIn("Error processing query", call_args)


if __name__ == '__main__':
    unittest.main()