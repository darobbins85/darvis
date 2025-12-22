"""
Unit tests for the speech recognition module.
"""

import pytest
from unittest.mock import patch, MagicMock
from darvis.speech import speak, listen, list_microphones


class TestSpeech:
    """Test cases for speech functionality."""

    @patch('darvis.speech.pyttsx3')
    def test_speak_success(self, mock_pyttsx3):
        """Test successful text-to-speech."""
        mock_engine = MagicMock()
        mock_pyttsx3.init.return_value = mock_engine

        speak("Hello world")

        mock_pyttsx3.init.assert_called_once()
        mock_engine.say.assert_called_once_with("Hello world")
        mock_engine.runAndWait.assert_called_once()

    @patch('darvis.speech.pyttsx3')
    def test_speak_tts_error(self, mock_pyttsx3):
        """Test TTS error handling."""
        mock_pyttsx3.init.side_effect = Exception("TTS failed")

        # Should not raise exception
        speak("Hello world")

        mock_pyttsx3.init.assert_called_once()

    @patch('darvis.speech.sr')
    def test_listen_success(self, mock_sr):
        """Test successful speech recognition."""
        # Mock the recognizer and microphone
        mock_recognizer = MagicMock()
        mock_microphone = MagicMock()
        mock_audio = MagicMock()

        mock_sr.Recognizer.return_value = mock_recognizer
        mock_sr.Microphone.return_value.__enter__ = MagicMock(return_value=mock_microphone)
        mock_sr.Microphone.return_value.__exit__ = MagicMock(return_value=None)
        mock_recognizer.listen.return_value = mock_audio
        mock_recognizer.recognize_google.return_value = "hello world"

        result = listen()

        assert result == "hello world"
        mock_recognizer.listen.assert_called_once()
        mock_recognizer.recognize_google.assert_called_once_with(mock_audio)

    @patch('darvis.speech.sr')
    def test_listen_unknown_value_error(self, mock_sr):
        """Test handling of unknown speech."""
        mock_recognizer = MagicMock()
        mock_microphone = MagicMock()
        mock_audio = MagicMock()

        mock_sr.Recognizer.return_value = mock_recognizer
        mock_sr.Microphone.return_value.__enter__ = MagicMock(return_value=mock_microphone)
        mock_sr.Microphone.return_value.__exit__ = MagicMock(return_value=None)
        mock_recognizer.listen.return_value = mock_audio
        mock_recognizer.recognize_google.side_effect = mock_sr.UnknownValueError()

        result = listen()

        assert result == ""
        mock_recognizer.recognize_google.assert_called_once()

    @patch('darvis.speech.sr')
    def test_listen_request_error(self, mock_sr):
        """Test handling of API errors."""
        mock_recognizer = MagicMock()
        mock_microphone = MagicMock()
        mock_audio = MagicMock()

        mock_sr.Recognizer.return_value = mock_recognizer
        mock_sr.Microphone.return_value.__enter__ = MagicMock(return_value=mock_microphone)
        mock_sr.Microphone.return_value.__exit__ = MagicMock(return_value=None)
        mock_recognizer.listen.return_value = mock_audio
        mock_recognizer.recognize_google.side_effect = mock_sr.RequestError("API error")

        result = listen()

        assert result == ""
        mock_recognizer.recognize_google.assert_called_once()

    @patch('darvis.speech.sr')
    def test_listen_microphone_error(self, mock_sr):
        """Test handling of microphone errors."""
        mock_sr.Microphone.side_effect = OSError("Microphone not found")

        result = listen()

        assert result == ""

    @patch('darvis.speech.sr')
    @patch('builtins.print')
    def test_list_microphones(self, mock_print, mock_sr):
        """Test microphone listing."""
        mock_sr.Microphone.list_microphone_names.return_value = ["Mic 1", "Mic 2"]

        list_microphones()

        mock_print.assert_any_call("Available microphones:")
        mock_print.assert_any_call("Index 0: Mic 1")
        mock_print.assert_any_call("Index 1: Mic 2")