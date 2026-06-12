import datetime
import os
import subprocess
import sys

import pyautogui
import keyboard
from smart_home.smart_home_controller import SmartHomeController
from system_control.app_launcher import AppLauncher
from system_control.window_manager import WindowManager

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0


class SystemController:
    def __init__(self):
        self.app_launcher = AppLauncher()
        self.window_manager = WindowManager()
        self.smart_home = SmartHomeController()

    def capture_screenshot(self, output_folder="screenshots"):
        os.makedirs(output_folder, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        path = os.path.join(output_folder, filename)
        pyautogui.screenshot(path)
        return path

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
        except Exception:
            pyautogui.press("win")

    def task_view(self):
        try:
            keyboard.press_and_release("windows+tab")
        except Exception:
            pyautogui.hotkey("win", "tab")

    def volume_up(self):
        try:
            keyboard.send("volume up")
        except Exception:
            pyautogui.press("volumeup")

    def volume_down(self):
        try:
            keyboard.send("volume down")
        except Exception:
            pyautogui.press("volumedown")

    def mute(self):
        try:
            keyboard.send("volume mute")
        except Exception:
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
        except Exception:
            pyautogui.press("playpause")

    def next_track(self):
        try:
            keyboard.send("next track")
        except Exception:
            pyautogui.press("nexttrack")

    def previous_track(self):
        try:
            keyboard.send("previous track")
        except Exception:
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
        temperature = float(current.get("temperature", 20)) + 1
        return self.smart_home.set_thermostat(temperature)

    def smart_home_thermostat_down(self):
        current = self.smart_home.get_device_state("thermostat") or {}
        temperature = float(current.get("temperature", 20)) - 1
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
