"""Multi-monitor cursor navigation for GestureOS."""

from __future__ import annotations

from typing import List

import pyautogui
from screeninfo import get_monitors

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0


class MultiMonitorMouse:
    """Navigate cursor across multiple display monitors."""

    def __init__(self) -> None:
        self._monitors: List = []
        self._current_index = 0
        self._refresh()

    def _refresh(self) -> None:
        try:
            self._monitors = list(get_monitors())
        except Exception:
            self._monitors = []

    def move_to_monitor(self, monitor_index: int) -> bool:
        self._refresh()
        if monitor_index < 0 or monitor_index >= len(self._monitors):
            return False
        mon = self._monitors[monitor_index]
        cx = mon.x + mon.width // 2
        cy = mon.y + mon.height // 2
        pyautogui.moveTo(cx, cy)
        self._current_index = monitor_index
        return True

    def next_monitor(self) -> bool:
        return self.move_to_monitor(
            (self._current_index + 1) % max(1, len(self._monitors))
        )

    def previous_monitor(self) -> bool:
        return self.move_to_monitor(
            (self._current_index - 1) % max(1, len(self._monitors))
        )
