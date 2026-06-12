"""Consolidated system-control stubs.

Several top-level modules (``brightness``, ``volume``, ``screenshot``,
``lock_screen``, ``shutdown``) defined near-identical placeholder classes.
This module provides a shared ``LevelControl`` base for increase/decrease
pairs and re-exports each concrete stub so existing imports keep working.
"""

from __future__ import annotations


class LevelControl:
    """Base for controls that expose an increase/decrease pair."""

    def increase(self):
        pass

    def decrease(self):
        pass


class BrightnessControl(LevelControl):
    """Brightness control stub (inherits increase/decrease)."""


class VolumeControl(LevelControl):
    """Volume control stub (inherits increase/decrease)."""


class Screenshot:
    """Screenshot capture stub."""

    def capture(self):
        pass


class LockScreen:
    """Lock-screen stub."""

    def lock(self):
        pass


class Shutdown:
    """Shutdown / restart stub."""

    def shutdown(self):
        pass

    def restart(self):
        pass
