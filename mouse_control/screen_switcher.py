"""Switch the active cursor between multiple monitors."""

from __future__ import annotations

from typing import List

import pyautogui
from screeninfo import get_monitors

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0


class ScreenSwitcher:
    """Teleports the cursor to the center of a specified monitor."""

    def __init__(self) -> None:
        self._monitors: List = []
        self._refresh()

    def _refresh(self) -> None:
        try:
            self._monitors = list(get_monitors())
        except Exception:
            self._monitors = []

    def switch_to(self, monitor_index: int = 0) -> bool:
        self._refresh()
        if monitor_index < 0 or monitor_index >= len(self._monitors):
            return False
        mon = self._monitors[monitor_index]
        cx = mon.x + mon.width // 2
        cy = mon.y + mon.height // 2
        pyautogui.moveTo(cx, cy)
        return True
