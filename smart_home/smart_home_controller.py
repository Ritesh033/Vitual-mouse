"""Smart home device controller for GestureOS.

This is a local stub that stores device state in-memory. Replace the
``_send_command`` method with your IoT platform's API client (e.g.
Home Assistant, Tuya, SmartThings) for real hardware control.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("gestureos.smarthome")


class SmartHomeController:
    """Manage smart home devices via an in-memory state store."""

    def __init__(self) -> None:
        self.home_mode_active: bool = False
        self._devices: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Core
    # ------------------------------------------------------------------

    def toggle_home_mode(self) -> bool:
        self.home_mode_active = not self.home_mode_active
        logger.info("Home mode: %s", "ON" if self.home_mode_active else "OFF")
        return self.home_mode_active

    def get_device_state(self, device_id: str) -> Optional[Dict[str, Any]]:
        return self._devices.get(device_id)

    def set_device_state(self, device_id: str, state: Dict[str, Any]) -> bool:
        self._devices[device_id] = state
        logger.info("Device %s → %s", device_id, state)
        return True

    # ------------------------------------------------------------------
    # Convenience wrappers
    # ------------------------------------------------------------------

    def set_lights(self, zone: str, state: str) -> bool:
        return self.set_device_state(f"lights_{zone}", {"state": state})

    def set_thermostat(self, temperature: float) -> bool:
        return self.set_device_state("thermostat", {"temperature": temperature})

    def toggle_door_lock(self, door: str) -> bool:
        current = self.get_device_state(f"lock_{door}") or {}
        new_state = "unlocked" if current.get("state") == "locked" else "locked"
        return self.set_device_state(f"lock_{door}", {"state": new_state})

    def activate_scene(self, scene: str) -> bool:
        logger.info("Activated scene: %s", scene)
        return self.set_device_state(f"scene_{scene}", {"active": True})

    def control_tv(self, action: str) -> bool:
        return self.set_device_state("tv", {"state": action})

    def _send_command(self, device_id: str, command: Dict[str, Any]) -> bool:
        """Hook for real IoT platform integration."""
        return self.set_device_state(device_id, command)
