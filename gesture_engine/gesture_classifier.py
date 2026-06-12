"""Classify hand landmarks into discrete gesture names."""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple


# MediaPipe landmark indices for fingertips and their lower joints.
_TIP_IDS = [4, 8, 12, 16, 20]
_PIP_IDS = [3, 6, 10, 14, 18]


def _fingers_up(landmarks: List[Tuple[float, float, float]]) -> List[int]:
    """Return a 5-element list (thumb..pinky) with 1 if the finger is up."""
    if len(landmarks) < 21:
        return [0, 0, 0, 0, 0]

    fingers = []
    # Thumb: compare x of tip vs IP joint (works for right hand)
    if landmarks[_TIP_IDS[0]][0] < landmarks[_PIP_IDS[0]][0]:
        fingers.append(1)
    else:
        fingers.append(0)

    # Other four fingers: tip y < PIP y ⇒ finger is up
    for i in range(1, 5):
        if landmarks[_TIP_IDS[i]][1] < landmarks[_PIP_IDS[i]][1]:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers


def _pinch_distance(
    landmarks: List[Tuple[float, float, float]],
    finger_a: int = 4,
    finger_b: int = 8,
) -> float:
    a = landmarks[finger_a]
    b = landmarks[finger_b]
    return math.hypot(a[0] - b[0], a[1] - b[1])


class GestureClassifier:
    """Rule-based gesture classification from normalized hand landmarks."""

    PINCH_THRESHOLD = 0.045

    def predict(self, hands: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Return ``{"gesture": <name>, "is_pointer": bool, ...}``."""
        if not hands:
            return {"gesture": None, "is_pointer": False, "fingers": []}

        normalized = hands[0]["normalized"]
        fingers = _fingers_up(normalized)

        gesture: Optional[str] = None
        is_pointer = False

        thumb_index = _pinch_distance(normalized, 4, 8)
        thumb_middle = _pinch_distance(normalized, 4, 12)

        # Pointer – index finger only
        if fingers == [0, 1, 0, 0, 0]:
            gesture = "pointer"
            is_pointer = True

        # Left click – thumb + index pinch
        elif thumb_index < self.PINCH_THRESHOLD and fingers[2:] == [0, 0, 0]:
            gesture = "left_click"

        # Right click – thumb + middle pinch
        elif thumb_middle < self.PINCH_THRESHOLD and fingers[1] == 0:
            gesture = "right_click"

        # Scroll – four fingers up (no thumb)
        elif fingers == [0, 1, 1, 1, 1]:
            gesture = "scroll"

        # Fist – drag / hold
        elif fingers == [0, 0, 0, 0, 0]:
            gesture = "pinch_and_hold"

        # Open palm – stop cursor
        elif fingers == [1, 1, 1, 1, 1]:
            gesture = "stop_cursor"

        # Victory / peace – two fingers
        elif fingers == [0, 1, 1, 0, 0]:
            gesture = "victory"

        # Three-finger tap – middle click
        elif fingers == [1, 1, 1, 0, 0]:
            gesture = "middle_click"

        return {
            "gesture": gesture,
            "is_pointer": is_pointer,
            "fingers": fingers,
        }
