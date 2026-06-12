"""Window management utilities."""

from utils.input_helpers import hotkey


class WindowManager:
    def tile_left(self):
        hotkey("win", "left")

    def tile_right(self):
        hotkey("win", "right")

    def maximize(self):
        hotkey("win", "up")

    def minimize(self):
        hotkey("win", "down")

    def close_active(self):
        hotkey("alt", "f4")
