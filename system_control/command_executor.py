"""Secure command executor for GestureOS.

This replaces the original CommandExecutor that used ``os.system`` and
``os.startfile`` with a hardened implementation that:
- Uses ``subprocess.run`` instead of ``os.system`` (no shell injection)
- Uses ``webbrowser.open`` instead of ``os.startfile`` (cross-platform)
- Keeps ``pyautogui.FAILSAFE = True``
- Validates intents against an allow-list
"""

from __future__ import annotations

import logging
import subprocess
import sys
import webbrowser
from typing import Dict, FrozenSet, Optional

import pyautogui

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0

logger = logging.getLogger("gestureos.executor")

ALLOWED_INTENTS: FrozenSet[str] = frozenset({
    "open_browser",
    "close_window",
    "volume_up",
    "volume_down",
    "screenshot",
    "open_vscode",
    "shutdown",
    "restart",
    "lock_screen",
})


class CommandExecutor:
    """Execute validated system intents in a safe manner."""

    def execute(self, intent: str) -> Optional[bool]:
        if intent not in ALLOWED_INTENTS:
            logger.warning("Rejected unknown intent: %s", intent)
            return None

        if intent == "open_browser":
            webbrowser.open("https://www.google.com")

        elif intent == "close_window":
            pyautogui.hotkey("alt", "f4")

        elif intent == "volume_up":
            pyautogui.press("volumeup")

        elif intent == "volume_down":
            pyautogui.press("volumedown")

        elif intent == "screenshot":
            pyautogui.hotkey("win", "printscreen")

        elif intent == "open_vscode":
            subprocess.Popen(["code"], close_fds=True, shell=False)

        elif intent == "shutdown":
            if sys.platform == "win32":
                subprocess.run(
                    ["shutdown", "/s", "/t", "5"],
                    check=False,
                )
            else:
                subprocess.run(
                    ["systemctl", "poweroff"],
                    check=False,
                )

        elif intent == "restart":
            if sys.platform == "win32":
                subprocess.run(
                    ["shutdown", "/r", "/t", "5"],
                    check=False,
                )
            else:
                subprocess.run(
                    ["systemctl", "reboot"],
                    check=False,
                )

        elif intent == "lock_screen":
            if sys.platform == "win32":
                subprocess.run(
                    ["rundll32.exe", "user32.dll,LockWorkStation"],
                    check=False,
                )
            else:
                subprocess.run(["loginctl", "lock-session"], check=False)

        return True
