"""Shared input helpers to eliminate duplicated keyboard/pyautogui patterns."""

from __future__ import annotations

import logging

import pyautogui
import keyboard as kb

logger = logging.getLogger(__name__)


def send_key(keyboard_key: str, pyautogui_key: str) -> None:
    """Send a key via the ``keyboard`` library, falling back to ``pyautogui``.

    This replaces the repeated try/except pattern found throughout
    ``SystemController`` where every media/system key is sent with
    ``keyboard.send`` and, on failure, retried with ``pyautogui.press``.
    """
    try:
        kb.send(keyboard_key)
    except Exception as exc:
        logger.debug("keyboard module failed for %r, falling back to pyautogui: %s", keyboard_key, exc)
        pyautogui.press(pyautogui_key)


def send_hotkey(keyboard_combo: str, *pyautogui_keys: str) -> None:
    """Press a hotkey combo via ``keyboard``, falling back to ``pyautogui``.

    Covers the pattern where ``keyboard.press_and_release`` is tried first
    (e.g. ``"windows+tab"``) and ``pyautogui.hotkey`` is used on failure.
    """
    try:
        kb.press_and_release(keyboard_combo)
    except Exception as exc:
        logger.debug("keyboard module failed for %r, falling back to pyautogui: %s", keyboard_combo, exc)
        pyautogui.hotkey(*pyautogui_keys)


def press_key(key: str) -> None:
    """Press a single key via ``pyautogui``."""
    pyautogui.press(key)


def hotkey(*keys: str) -> None:
    """Press a hotkey combination via ``pyautogui``."""
    pyautogui.hotkey(*keys)
