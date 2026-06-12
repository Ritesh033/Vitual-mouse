"""Tests for system_controller.py."""

import os
from unittest.mock import MagicMock, patch

import pytest

from system_controller import SystemController


class TestSystemController:
    def setup_method(self):
        self.ctrl = SystemController()

    # --- capture_screenshot ---

    def test_capture_screenshot_creates_folder(self, tmp_path):
        folder = str(tmp_path / "shots")
        with patch("system_controller.pyautogui.screenshot") as mock_ss:
            path = self.ctrl.capture_screenshot(output_folder=folder)
        assert os.path.isdir(folder)
        assert path.startswith(folder)
        assert path.endswith(".png")
        mock_ss.assert_called_once_with(path)

    def test_capture_screenshot_default_folder(self):
        with patch("system_controller.pyautogui.screenshot"):
            with patch("system_controller.os.makedirs") as mock_mkdir:
                path = self.ctrl.capture_screenshot()
        mock_mkdir.assert_called_once_with("screenshots", exist_ok=True)
        assert "screenshot_" in path

    # --- lock_screen ---

    def test_lock_screen(self):
        with patch("system_controller.os.system") as mock_sys:
            self.ctrl.lock_screen()
        mock_sys.assert_called_once_with("rundll32.exe user32.dll,LockWorkStation")

    # --- close_window ---

    def test_close_window_delegates(self):
        self.ctrl.window_manager = MagicMock()
        self.ctrl.close_window()
        self.ctrl.window_manager.close_active.assert_called_once()

    # --- launch_application ---

    def test_launch_application_delegates(self):
        self.ctrl.app_launcher = MagicMock()
        self.ctrl.app_launcher.launch.return_value = True
        assert self.ctrl.launch_application("chrome") is True
        self.ctrl.app_launcher.launch.assert_called_once_with("chrome")

    # --- open_start_menu ---

    def test_open_start_menu_keyboard(self):
        import keyboard as kb

        kb.press_and_release.reset_mock()
        kb.press_and_release.side_effect = None
        self.ctrl.open_start_menu()
        kb.press_and_release.assert_called_once_with("windows")

    def test_open_start_menu_fallback(self):
        import keyboard as kb
        import pyautogui

        kb.press_and_release.side_effect = Exception("fail")
        pyautogui.press.reset_mock()
        self.ctrl.open_start_menu()
        pyautogui.press.assert_called_once_with("win")

    # --- task_view ---

    def test_task_view_keyboard(self):
        import keyboard as kb

        kb.press_and_release.reset_mock()
        kb.press_and_release.side_effect = None
        self.ctrl.task_view()
        kb.press_and_release.assert_called_once_with("windows+tab")

    def test_task_view_fallback(self):
        import keyboard as kb
        import pyautogui

        kb.press_and_release.side_effect = Exception("fail")
        pyautogui.hotkey.reset_mock()
        self.ctrl.task_view()
        pyautogui.hotkey.assert_called_once_with("win", "tab")

    # --- volume ---

    def test_volume_up(self):
        import keyboard as kb

        kb.send.reset_mock()
        kb.send.side_effect = None
        self.ctrl.volume_up()
        kb.send.assert_called_once_with("volume up")

    def test_volume_up_fallback(self):
        import keyboard as kb
        import pyautogui

        kb.send.side_effect = Exception("fail")
        pyautogui.press.reset_mock()
        self.ctrl.volume_up()
        pyautogui.press.assert_called_once_with("volumeup")

    def test_volume_down(self):
        import keyboard as kb

        kb.send.reset_mock()
        kb.send.side_effect = None
        self.ctrl.volume_down()
        kb.send.assert_called_once_with("volume down")

    def test_volume_down_fallback(self):
        import keyboard as kb
        import pyautogui

        kb.send.side_effect = Exception("fail")
        pyautogui.press.reset_mock()
        self.ctrl.volume_down()
        pyautogui.press.assert_called_once_with("volumedown")

    def test_mute(self):
        import keyboard as kb

        kb.send.reset_mock()
        kb.send.side_effect = None
        self.ctrl.mute()
        kb.send.assert_called_once_with("volume mute")

    def test_mute_fallback(self):
        import keyboard as kb
        import pyautogui

        kb.send.side_effect = Exception("fail")
        pyautogui.press.reset_mock()
        self.ctrl.mute()
        pyautogui.press.assert_called_once_with("volumemute")

    # --- browser ---

    def test_open_new_tab(self):
        import pyautogui

        pyautogui.hotkey.reset_mock()
        self.ctrl.open_new_tab()
        pyautogui.hotkey.assert_called_once_with("ctrl", "t")

    def test_close_tab(self):
        import pyautogui

        pyautogui.hotkey.reset_mock()
        self.ctrl.close_tab()
        pyautogui.hotkey.assert_called_once_with("ctrl", "w")

    def test_reload_page(self):
        import pyautogui

        pyautogui.hotkey.reset_mock()
        self.ctrl.reload_page()
        pyautogui.hotkey.assert_called_once_with("ctrl", "r")

    def test_browser_next(self):
        import pyautogui

        pyautogui.hotkey.reset_mock()
        self.ctrl.browser_next()
        pyautogui.hotkey.assert_called_once_with("alt", "right")

    def test_browser_previous(self):
        import pyautogui

        pyautogui.hotkey.reset_mock()
        self.ctrl.browser_previous()
        pyautogui.hotkey.assert_called_once_with("alt", "left")

    # --- media ---

    def test_play_pause(self):
        import keyboard as kb

        kb.send.reset_mock()
        kb.send.side_effect = None
        self.ctrl.play_pause()
        kb.send.assert_called_once_with("play/pause media")

    def test_play_pause_fallback(self):
        import keyboard as kb
        import pyautogui

        kb.send.side_effect = Exception("fail")
        pyautogui.press.reset_mock()
        self.ctrl.play_pause()
        pyautogui.press.assert_called_once_with("playpause")

    def test_next_track(self):
        import keyboard as kb

        kb.send.reset_mock()
        kb.send.side_effect = None
        self.ctrl.next_track()
        kb.send.assert_called_once_with("next track")

    def test_previous_track(self):
        import keyboard as kb

        kb.send.reset_mock()
        kb.send.side_effect = None
        self.ctrl.previous_track()
        kb.send.assert_called_once_with("previous track")

    def test_fast_forward(self):
        import pyautogui

        pyautogui.press.reset_mock()
        self.ctrl.fast_forward()
        pyautogui.press.assert_called_once_with("right")

    def test_rewind(self):
        import pyautogui

        pyautogui.press.reset_mock()
        self.ctrl.rewind()
        pyautogui.press.assert_called_once_with("left")

    # --- slides ---

    def test_next_slide(self):
        import pyautogui

        pyautogui.press.reset_mock()
        self.ctrl.next_slide()
        pyautogui.press.assert_called_once_with("right")

    def test_previous_slide(self):
        import pyautogui

        pyautogui.press.reset_mock()
        self.ctrl.previous_slide()
        pyautogui.press.assert_called_once_with("left")

    # --- smart home ---

    def test_toggle_home_mode(self):
        self.ctrl.smart_home = MagicMock()
        self.ctrl.smart_home.toggle_home_mode.return_value = True
        assert self.ctrl.toggle_home_mode() is True

    def test_smart_home_lights_on(self):
        self.ctrl.smart_home = MagicMock()
        self.ctrl.smart_home_lights_on()
        self.ctrl.smart_home.set_lights.assert_called_once_with("all", "on")

    def test_smart_home_lights_off(self):
        self.ctrl.smart_home = MagicMock()
        self.ctrl.smart_home_lights_off()
        self.ctrl.smart_home.set_lights.assert_called_once_with("all", "off")

    def test_smart_home_lights_room_toggles(self):
        self.ctrl.smart_home = MagicMock()
        self.ctrl.smart_home.get_device_state.return_value = {"state": "on"}
        self.ctrl.smart_home_lights_room("bedroom")
        self.ctrl.smart_home.set_lights.assert_called_once_with("bedroom", "off")

    def test_smart_home_lights_room_off_to_on(self):
        self.ctrl.smart_home = MagicMock()
        self.ctrl.smart_home.get_device_state.return_value = {"state": "off"}
        self.ctrl.smart_home_lights_room()
        self.ctrl.smart_home.set_lights.assert_called_once_with("living_room", "on")

    def test_smart_home_lights_room_none_state(self):
        self.ctrl.smart_home = MagicMock()
        self.ctrl.smart_home.get_device_state.return_value = None
        self.ctrl.smart_home_lights_room()
        self.ctrl.smart_home.set_lights.assert_called_once_with("living_room", "on")

    def test_smart_home_thermostat_up(self):
        self.ctrl.smart_home = MagicMock()
        self.ctrl.smart_home.get_device_state.return_value = {"temperature": 22}
        self.ctrl.smart_home_thermostat_up()
        self.ctrl.smart_home.set_thermostat.assert_called_once_with(23.0)

    def test_smart_home_thermostat_down(self):
        self.ctrl.smart_home = MagicMock()
        self.ctrl.smart_home.get_device_state.return_value = {"temperature": 22}
        self.ctrl.smart_home_thermostat_down()
        self.ctrl.smart_home.set_thermostat.assert_called_once_with(21.0)

    def test_smart_home_thermostat_default(self):
        self.ctrl.smart_home = MagicMock()
        self.ctrl.smart_home.get_device_state.return_value = None
        self.ctrl.smart_home_thermostat_up()
        self.ctrl.smart_home.set_thermostat.assert_called_once_with(21.0)

    def test_smart_home_door_toggle(self):
        self.ctrl.smart_home = MagicMock()
        self.ctrl.smart_home_door_toggle()
        self.ctrl.smart_home.toggle_door_lock.assert_called_once_with("front")

    def test_smart_home_scene(self):
        self.ctrl.smart_home = MagicMock()
        self.ctrl.smart_home_scene("party")
        self.ctrl.smart_home.activate_scene.assert_called_once_with("party")

    def test_smart_home_scene_default(self):
        self.ctrl.smart_home = MagicMock()
        self.ctrl.smart_home_scene()
        self.ctrl.smart_home.activate_scene.assert_called_once_with("movie")

    def test_smart_home_tv_toggle_on(self):
        self.ctrl.smart_home = MagicMock()
        self.ctrl.smart_home.get_device_state.return_value = {"state": "off"}
        self.ctrl.smart_home_tv()
        self.ctrl.smart_home.control_tv.assert_called_once_with("on")

    def test_smart_home_tv_toggle_off(self):
        self.ctrl.smart_home = MagicMock()
        self.ctrl.smart_home.get_device_state.return_value = {"state": "on"}
        self.ctrl.smart_home_tv()
        self.ctrl.smart_home.control_tv.assert_called_once_with("off")

    def test_smart_home_appliance_toggle(self):
        self.ctrl.smart_home = MagicMock()
        self.ctrl.smart_home.get_device_state.return_value = {"state": "on"}
        self.ctrl.smart_home_appliance("coffee_maker")
        self.ctrl.smart_home._send_command.assert_called_once_with(
            "coffee_maker", {"state": "off"}
        )

    def test_smart_home_appliance_default(self):
        self.ctrl.smart_home = MagicMock()
        self.ctrl.smart_home.get_device_state.return_value = None
        self.ctrl.smart_home_appliance()
        self.ctrl.smart_home._send_command.assert_called_once_with(
            "coffee_maker", {"state": "on"}
        )
