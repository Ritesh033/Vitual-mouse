"""Smooth cursor movement from normalized hand coordinates."""

from __future__ import annotations

from typing import Optional, Tuple

import pyautogui
from screeninfo import get_monitors

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0


class CursorController:
    """Maps normalized hand coordinates to screen cursor position."""

    def __init__(
        self,
        smoothing: int = 4,
        speed: float = 1.15,
        deadzone_px: int = 2,
        edge_margin: float = 0.07,
        adaptive_smoothing: bool = True,
    ) -> None:
        self.smoothing = max(1, smoothing)
        self.speed = speed
        self.deadzone_px = deadzone_px
        self.edge_margin = edge_margin
        self.adaptive_smoothing = adaptive_smoothing

        try:
            mon = get_monitors()[0]
            self._screen_w = mon.width
            self._screen_h = mon.height
        except Exception:
            self._screen_w, self._screen_h = pyautogui.size()

        self._prev_x: Optional[float] = None
        self._prev_y: Optional[float] = None
        self._is_dragging = False

    # ------------------------------------------------------------------

    @property
    def is_dragging(self) -> bool:
        return self._is_dragging

    # ------------------------------------------------------------------

    def move_cursor(self, normalized_point: Tuple[float, ...]) -> None:
        nx, ny = normalized_point[0], normalized_point[1]

        margin = self.edge_margin
        nx = (nx - margin) / (1.0 - 2 * margin)
        ny = (ny - margin) / (1.0 - 2 * margin)
        nx = max(0.0, min(1.0, nx))
        ny = max(0.0, min(1.0, ny))

        target_x = nx * self._screen_w * self.speed
        target_y = ny * self._screen_h * self.speed
        target_x = max(0, min(self._screen_w - 1, target_x))
        target_y = max(0, min(self._screen_h - 1, target_y))

        if self._prev_x is None:
            self._prev_x = target_x
            self._prev_y = target_y
        else:
            s = self.smoothing
            self._prev_x = self._prev_x + (target_x - self._prev_x) / s
            self._prev_y = self._prev_y + (target_y - self._prev_y) / s

        dx = abs(self._prev_x - (pyautogui.position()[0]))
        dy = abs(self._prev_y - (pyautogui.position()[1]))
        if dx > self.deadzone_px or dy > self.deadzone_px:
            pyautogui.moveTo(int(self._prev_x), int(self._prev_y))

    # ------------------------------------------------------------------

    def start_drag(self) -> None:
        if not self._is_dragging:
            pyautogui.mouseDown()
            self._is_dragging = True

    def stop_drag(self) -> None:
        if self._is_dragging:
            pyautogui.mouseUp()
            self._is_dragging = False

    # ------------------------------------------------------------------

    def reset_tracking(self) -> None:
        self._prev_x = None
        self._prev_y = None

    def frame_cursor_position(self, frame_w: int, frame_h: int) -> Optional[Tuple[int, int]]:
        pos = pyautogui.position()
        fx = int(pos[0] / self._screen_w * frame_w)
        fy = int(pos[1] / self._screen_h * frame_h)
        return (fx, fy)

    def zoom_in(self) -> None:
        pyautogui.hotkey("ctrl", "plus")

    def zoom_out(self) -> None:
        pyautogui.hotkey("ctrl", "minus")
