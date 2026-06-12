import datetime
import logging
import os
import subprocess
import sys

import pyautogui
import keyboard

from smart_home.smart_home_controller import SmartHomeController
from system_control.app_launcher import AppLauncher
from system_control.window_manager import WindowManager

logger = logging.getLogger(__name__)

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0


class SystemController:
    def __init__(self):
        self.app_launcher = AppLauncher()
        self.window_manager = WindowManager()
        self.smart_home = SmartHomeController()

    def capture_screenshot(self, output_folder="screenshots"):
        try:
            os.makedirs(output_folder, exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            path = os.path.join(output_folder, filename)
            pyautogui.screenshot(path)
            return path
        except OSError as exc:
            logger.error("Failed to save screenshot to %s: %s", output_folder, exc)
            return None
        except Exception as exc:
            logger.error("Screenshot capture failed: %s", exc)
            return None

    def lock_screen(self):
        if sys.platform == "win32":
            subprocess.run(
                ["rundll32.exe", "user32.dll,LockWorkStation"],
                check=False,
            )
        else:
            subprocess.run(["loginctl", "lock-session"], check=False)

    def close_window(self):
        self.window_manager.close_active()

    def launch_application(self, app_name):
        return self.app_launcher.launch(app_name)

    def open_start_menu(self):
        try:
            keyboard.press_and_release("windows")
        except Exception as exc:
            logger.debug("keyboard module failed for open_start_menu, falling back to pyautogui: %s", exc)
            pyautogui.press("win")

    def task_view(self):
        try:
            keyboard.press_and_release("windows+tab")
        except Exception as exc:
            logger.debug("keyboard module failed for task_view, falling back to pyautogui: %s", exc)
            pyautogui.hotkey("win", "tab")

    def volume_up(self):
        try:
            keyboard.send("volume up")
        except Exception as exc:
            logger.debug("keyboard module failed for volume_up, falling back to pyautogui: %s", exc)
            pyautogui.press("volumeup")

    def volume_down(self):
        try:
            keyboard.send("volume down")
        except Exception as exc:
            logger.debug("keyboard module failed for volume_down, falling back to pyautogui: %s", exc)
            pyautogui.press("volumedown")

    def mute(self):
        try:
            keyboard.send("volume mute")
        except Exception as exc:
            logger.debug("keyboard module failed for mute, falling back to pyautogui: %s", exc)
            pyautogui.press("volumemute")

    def open_new_tab(self):
        pyautogui.hotkey("ctrl", "t")

    def close_tab(self):
        pyautogui.hotkey("ctrl", "w")

    def reload_page(self):
        pyautogui.hotkey("ctrl", "r")

    def browser_next(self):
        pyautogui.hotkey("alt", "right")

    def browser_previous(self):
        pyautogui.hotkey("alt", "left")

    def play_pause(self):
        try:
            keyboard.send("play/pause media")
        except Exception as exc:
            logger.debug("keyboard module failed for play_pause, falling back to pyautogui: %s", exc)
            pyautogui.press("playpause")

    def next_track(self):
        try:
            keyboard.send("next track")
        except Exception as exc:
            logger.debug("keyboard module failed for next_track, falling back to pyautogui: %s", exc)
            pyautogui.press("nexttrack")

    def previous_track(self):
        try:
            keyboard.send("previous track")
        except Exception as exc:
            logger.debug("keyboard module failed for previous_track, falling back to pyautogui: %s", exc)
            pyautogui.press("prevtrack")

    def fast_forward(self):
        pyautogui.press("right")

    def rewind(self):
        pyautogui.press("left")

    def next_slide(self):
        pyautogui.press("right")

    def previous_slide(self):
        pyautogui.press("left")

    def toggle_home_mode(self):
        return self.smart_home.toggle_home_mode()

    def smart_home_lights_on(self):
        return self.smart_home.set_lights("all", "on")

    def smart_home_lights_off(self):
        return self.smart_home.set_lights("all", "off")

    def smart_home_lights_room(self, room="living_room"):
        current = self.smart_home.get_device_state(f"lights_{room}") or {}
        next_state = "off" if current.get("state") == "on" else "on"
        return self.smart_home.set_lights(room, next_state)

    def smart_home_thermostat_up(self):
        current = self.smart_home.get_device_state("thermostat") or {}
        try:
            temperature = float(current.get("temperature", 20)) + 1
        except (ValueError, TypeError) as exc:
            logger.warning("Invalid thermostat temperature value, defaulting to 21: %s", exc)
            temperature = 21
        return self.smart_home.set_thermostat(temperature)

    def smart_home_thermostat_down(self):
        current = self.smart_home.get_device_state("thermostat") or {}
        try:
            temperature = float(current.get("temperature", 20)) - 1
        except (ValueError, TypeError) as exc:
            logger.warning("Invalid thermostat temperature value, defaulting to 19: %s", exc)
            temperature = 19
        return self.smart_home.set_thermostat(temperature)

    def smart_home_door_toggle(self):
        return self.smart_home.toggle_door_lock("front")

    def smart_home_scene(self, scene="movie"):
        return self.smart_home.activate_scene(scene)

    def smart_home_tv(self):
        current = self.smart_home.get_device_state("tv") or {}
        action = "off" if current.get("state") == "on" else "on"
        return self.smart_home.control_tv(action)

    def smart_home_appliance(self, device="coffee_maker"):
        current = self.smart_home.get_device_state(device) or {}
        state = "off" if current.get("state") == "on" else "on"
        return self.smart_home._send_command(device, {"state": state})
