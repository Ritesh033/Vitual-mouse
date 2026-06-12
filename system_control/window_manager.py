"""Window management utilities."""

import pyautogui

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0


class WindowManager:
    def tile_left(self) -> None:
        pyautogui.hotkey("win", "left")

    def tile_right(self) -> None:
        pyautogui.hotkey("win", "right")

    def maximize(self) -> None:
        pyautogui.hotkey("win", "up")

    def minimize(self) -> None:
        pyautogui.hotkey("win", "down")

    def close_active(self) -> None:
        pyautogui.hotkey("alt", "f4")

    def show_desktop(self) -> None:
        pyautogui.hotkey("win", "d")

    def switch_app(self) -> None:
        pyautogui.hotkey("alt", "tab")

    def snap_top(self) -> None:
        pyautogui.hotkey("win", "up")

    def snap_bottom(self) -> None:
        pyautogui.hotkey("win", "down")
