"""Keyboard shortcut controller for GestureOS."""

from __future__ import annotations

from typing import List

import pyautogui

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0


class KeyboardController:
    """Execute keyboard shortcuts and key presses via gestures."""

    # Common shortcut map used by the gesture engine
    SHORTCUTS = {
        "copy": ["ctrl", "c"],
        "paste": ["ctrl", "v"],
        "cut": ["ctrl", "x"],
        "undo": ["ctrl", "z"],
        "redo": ["ctrl", "y"],
        "select_all": ["ctrl", "a"],
        "save": ["ctrl", "s"],
        "print": ["ctrl", "p"],
        "switch_app": ["alt", "tab"],
        "show_desktop": ["win", "d"],
        "file_explorer": ["win", "e"],
        "find": ["ctrl", "f"],
        "new_window": ["ctrl", "n"],
        "close_window": ["alt", "f4"],
        "fullscreen": ["f11"],
    }

    def press_key(self, key: str) -> None:
        pyautogui.press(key)

    def hotkey(self, *keys: str) -> None:
        pyautogui.hotkey(*keys)

    def type_text(self, text: str, interval: float = 0.02) -> None:
        pyautogui.typewrite(text, interval=interval)

    def execute_shortcut(self, name: str) -> bool:
        keys = self.SHORTCUTS.get(name)
        if not keys:
            return False
        pyautogui.hotkey(*keys)
        return True

    def press_keys(self, keys: List[str]) -> None:
        if len(keys) == 1:
            pyautogui.press(keys[0])
        else:
            pyautogui.hotkey(*keys)
