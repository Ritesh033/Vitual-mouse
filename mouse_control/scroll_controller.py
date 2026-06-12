"""Scroll controller for GestureOS virtual mouse."""

from __future__ import annotations

import pyautogui

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0


class ScrollController:
    """Provides vertical and horizontal scroll operations."""

    def vertical_scroll(self, amount: int = 3) -> None:
        pyautogui.scroll(amount)

    def horizontal_scroll(self, amount: int = 3) -> None:
        pyautogui.hscroll(amount)
