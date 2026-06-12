"""Shared helpers for smart-home device control patterns."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def toggle_device_state(smart_home, device_key: str) -> tuple[dict, str]:
    """Read current on/off state for *device_key* and flip it.

    Returns ``(current_state_dict, next_state_str)`` so callers can forward it.
    """
    current = smart_home.get_device_state(device_key) or {}
    next_state = "off" if current.get("state") == "on" else "on"
    return current, next_state


def adjust_thermostat(smart_home, delta: float) -> object:
    """Adjust the thermostat by *delta* degrees (positive or negative)."""
    current = smart_home.get_device_state("thermostat") or {}
    try:
        temperature = float(current.get("temperature", 20)) + delta
    except (ValueError, TypeError) as exc:
        logger.warning("Invalid thermostat temperature value, defaulting to %s: %s", 20 + delta, exc)
        temperature = 20 + delta
    return smart_home.set_thermostat(temperature)
