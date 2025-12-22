"""
Speech recognition and text-to-speech functionality.
"""

import speech_recognition as sr
from typing import Optional
from .config import ENERGY_THRESHOLD, LISTEN_TIMEOUT, PHRASE_TIME_LIMIT


def speak(text: str) -> None:
    """
    Convert text to speech using pyttsx3 TTS engine.

    Args:
        text: The text to speak aloud

    Note:
        Silently ignores TTS errors to prevent application interruption.
        Text feedback is still provided through the GUI.
    """
    try:
        import pyttsx3

        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception:
        # Silently ignore TTS errors - text feedback is still shown
        pass


def listen(device_index: Optional[int] = None) -> str:
    """
    Capture and transcribe voice input using Google Speech Recognition.

    Args:
        device_index: Specific microphone device index to use.
                     If None, uses system default.

    Returns:
        Lowercase transcribed text from speech, or empty string on errors.

    Raises:
        No exceptions - gracefully handles all audio/speech errors.

    Note:
        Manual input is handled separately through the GUI input field.
        This function focuses solely on voice-to-text conversion.
    """
    r = sr.Recognizer()
    r.energy_threshold = ENERGY_THRESHOLD
    try:
        with sr.Microphone(device_index=device_index) as source:
            audio = r.listen(
                source, timeout=LISTEN_TIMEOUT, phrase_time_limit=PHRASE_TIME_LIMIT
            )
        try:
            return r.recognize_google(audio).lower()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            print(f"API error: {e}")
            return ""
    except OSError as e:
        print(f"Microphone error: {e}")
        return ""
    except sr.WaitTimeoutError:
        return ""


def list_microphones() -> None:
    """
    Enumerate and display all available microphone devices.

    Prints a numbered list of microphone names with their indices.
    Useful for troubleshooting audio input issues and configuring
    the correct microphone device.

    Output format:
        Index 0: Microphone Name
        Index 1: Another Microphone Name
        ...
    """
    r = sr.Recognizer()
    microphones = sr.Microphone.list_microphone_names()
    print("Available microphones:")
    for i, name in enumerate(microphones):
        print(f"Index {i}: {name}")
