"""Speech-to-text using SpeechRecognition for GestureOS voice commands."""

from __future__ import annotations

from typing import Optional

import speech_recognition as sr


class SpeechToText:
    """Capture and transcribe microphone audio using Google STT."""

    def __init__(self) -> None:
        self._recognizer = sr.Recognizer()
        self._microphone = sr.Microphone()
        # Calibrate for ambient noise once
        with self._microphone as source:
            self._recognizer.adjust_for_ambient_noise(source, duration=0.5)

    def listen(
        self,
        timeout: int = 4,
        phrase_time_limit: int = 6,
    ) -> Optional[str]:
        """Listen for speech and return the transcript, or None."""
        try:
            with self._microphone as source:
                audio = self._recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit,
                )
            text = self._recognizer.recognize_google(audio)
            return str(text).strip() if text else None
        except (sr.UnknownValueError, sr.WaitTimeoutError):
            return None
        except sr.RequestError:
            return None
