"""Tests for window_manager.py."""

from unittest.mock import MagicMock, patch

import pytest

from window_manager import WindowManager


class TestWindowManager:
    def setup_method(self):
        self.wm = WindowManager()

    def test_tile_left(self):
        import pyautogui

        pyautogui.hotkey.reset_mock()
        self.wm.tile_left()
        pyautogui.hotkey.assert_called_once_with("win", "left")

    def test_tile_right(self):
        import pyautogui

        pyautogui.hotkey.reset_mock()
        self.wm.tile_right()
        pyautogui.hotkey.assert_called_once_with("win", "right")

    def test_maximize(self):
        import pyautogui

        pyautogui.hotkey.reset_mock()
        self.wm.maximize()
        pyautogui.hotkey.assert_called_once_with("win", "up")

    def test_minimize(self):
        import pyautogui

        pyautogui.hotkey.reset_mock()
        self.wm.minimize()
        pyautogui.hotkey.assert_called_once_with("win", "down")

    def test_close_active(self):
        import pyautogui

        pyautogui.hotkey.reset_mock()
        self.wm.close_active()
        pyautogui.hotkey.assert_called_once_with("alt", "f4")
