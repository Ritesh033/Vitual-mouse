"""Drag-and-drop controller for GestureOS virtual mouse."""

from __future__ import annotations

import pyautogui

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0


class DragController:
    """Manages mouse drag state."""

    def __init__(self) -> None:
        self._dragging = False

    @property
    def is_dragging(self) -> bool:
        return self._dragging

    def start_drag(self) -> None:
        if not self._dragging:
            pyautogui.mouseDown()
            self._dragging = True

    def stop_drag(self) -> None:
        if self._dragging:
            pyautogui.mouseUp()
            self._dragging = False
