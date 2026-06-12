"""Estimate the distance between the user's hand and the camera."""

from __future__ import annotations

import math
from typing import Any, Dict, List, Tuple


class DistanceEstimator:
    """Uses palm width in normalized coordinates to approximate hand distance."""

    def __init__(self, calibration_factor: float = 9.5) -> None:
        self._calibration = calibration_factor

    def measure(
        self,
        normalized_landmarks: List[Tuple[float, float, float]],
        min_distance_cm: float = 25,
        max_distance_cm: float = 170,
        ideal_distance_cm: float = 65,
    ) -> Dict[str, Any]:
        if not normalized_landmarks or len(normalized_landmarks) < 21:
            return {
                "distance_cm": None,
                "quality": 0.0,
                "in_active_zone": False,
                "message": "No hand",
            }

        wrist = normalized_landmarks[0]
        middle_mcp = normalized_landmarks[9]
        palm_size = math.hypot(
            wrist[0] - middle_mcp[0],
            wrist[1] - middle_mcp[1],
        )

        if palm_size < 1e-6:
            return {
                "distance_cm": None,
                "quality": 0.0,
                "in_active_zone": False,
                "message": "Palm not measurable",
            }

        distance_cm = self._calibration / palm_size

        in_zone = min_distance_cm <= distance_cm <= max_distance_cm
        quality = max(
            0.0,
            1.0 - abs(distance_cm - ideal_distance_cm) / (max_distance_cm - min_distance_cm),
        )

        if distance_cm < min_distance_cm:
            message = "Too close"
        elif distance_cm > max_distance_cm:
            message = "Too far"
        else:
            message = "Active zone"

        return {
            "distance_cm": distance_cm,
            "quality": quality,
            "in_active_zone": in_zone,
            "message": message,
        }
