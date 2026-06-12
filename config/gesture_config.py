"""Gesture configuration loader for GestureOS."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml


class GestureConfig:
    """Loads and provides access to the gesture configuration YAML."""

    def __init__(self, path: str = "config/gestures.yaml") -> None:
        self._path = Path(path)
        self.data: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        if not self._path.exists():
            return self._defaults()
        with open(self._path, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or self._defaults()

    @staticmethod
    def _defaults() -> Dict[str, Any]:
        return {
            "camera": {
                "detection_confidence": 0.6,
                "tracking_confidence": 0.65,
                "model_complexity": 0,
                "width": 960,
                "height": 540,
                "fps": 60,
                "flip_horizontal": True,
                "distance_calibration": 9.5,
                "min_distance_cm": 25,
                "max_distance_cm": 170,
                "ideal_distance_cm": 65,
            },
            "sensitivity": {
                "cursor_speed": 1.15,
                "smoothing": True,
                "smoothing_factor": 4,
                "deadzone_px": 2,
                "edge_margin": 0.07,
                "adaptive_smoothing": True,
            },
            "gestures": {},
            "debug": {"show_landmarks": False},
        }

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def reload(self) -> None:
        self.data = self._load()
