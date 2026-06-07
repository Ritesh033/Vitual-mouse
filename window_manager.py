"""Window management utilities."""

import pyautogui


class WindowManager:
    def tile_left(self):
        pyautogui.hotkey("win", "left")

    def tile_right(self):
        pyautogui.hotkey("win", "right")

    def maximize(self):
        pyautogui.hotkey("win", "up")

    def minimize(self):
        pyautogui.hotkey("win", "down")

    def close_active(self):
        pyautogui.hotkey("alt", "f4")
