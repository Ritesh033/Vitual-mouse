import datetime
import logging
import os

import pyautogui

from smart_home.smart_home_controller import SmartHomeController
from system_control.app_launcher import AppLauncher
from system_control.window_manager import WindowManager
from utils.input_helpers import send_key, send_hotkey, press_key, hotkey
from utils.smart_home_helpers import toggle_device_state, adjust_thermostat

logger = logging.getLogger(__name__)

pyautogui.FAILSAFE = False
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
        ret = os.system("rundll32.exe user32.dll,LockWorkStation")
        if ret != 0:
            logger.warning("Lock screen command exited with code %d", ret)

    def close_window(self):
        self.window_manager.close_active()

    def launch_application(self, app_name):
        return self.app_launcher.launch(app_name)

    def open_start_menu(self):
        send_hotkey("windows", "win")

    def task_view(self):
        send_hotkey("windows+tab", "win", "tab")

    def volume_up(self):
        send_key("volume up", "volumeup")

    def volume_down(self):
        send_key("volume down", "volumedown")

    def mute(self):
        send_key("volume mute", "volumemute")

    def open_new_tab(self):
        hotkey("ctrl", "t")

    def close_tab(self):
        hotkey("ctrl", "w")

    def reload_page(self):
        hotkey("ctrl", "r")

    def browser_next(self):
        hotkey("alt", "right")

    def browser_previous(self):
        hotkey("alt", "left")

    def play_pause(self):
        send_key("play/pause media", "playpause")

    def next_track(self):
        send_key("next track", "nexttrack")

    def previous_track(self):
        send_key("previous track", "prevtrack")

    def fast_forward(self):
        press_key("right")

    def rewind(self):
        press_key("left")

    def next_slide(self):
        press_key("right")

    def previous_slide(self):
        press_key("left")

    def toggle_home_mode(self):
        return self.smart_home.toggle_home_mode()

    def smart_home_lights_on(self):
        return self.smart_home.set_lights("all", "on")

    def smart_home_lights_off(self):
        return self.smart_home.set_lights("all", "off")

    def smart_home_lights_room(self, room="living_room"):
        _, next_state = toggle_device_state(self.smart_home, f"lights_{room}")
        return self.smart_home.set_lights(room, next_state)

    def smart_home_thermostat_up(self):
        return adjust_thermostat(self.smart_home, +1)

    def smart_home_thermostat_down(self):
        return adjust_thermostat(self.smart_home, -1)

    def smart_home_door_toggle(self):
        return self.smart_home.toggle_door_lock("front")

    def smart_home_scene(self, scene="movie"):
        return self.smart_home.activate_scene(scene)

    def smart_home_tv(self):
        _, action = toggle_device_state(self.smart_home, "tv")
        return self.smart_home.control_tv(action)

    def smart_home_appliance(self, device="coffee_maker"):
        _, state = toggle_device_state(self.smart_home, device)
        return self.smart_home._send_command(device, {"state": state})
