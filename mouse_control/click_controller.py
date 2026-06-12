"""Click operations for GestureOS virtual mouse."""

from __future__ import annotations

import pyautogui

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0


class ClickController:
    """Provides left, right, double, middle, and auto-click operations."""

    def left_click(self) -> None:
        pyautogui.click()

    def right_click(self) -> None:
        pyautogui.rightClick()

    def double_click(self) -> None:
        pyautogui.doubleClick()

    def triple_click(self) -> None:
        pyautogui.tripleClick()

    def middle_click(self) -> None:
        pyautogui.middleClick()
