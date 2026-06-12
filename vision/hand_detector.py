"""Hand detection and landmark extraction using MediaPipe."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import cv2
import mediapipe as mp
import numpy as np


class HandDetector:
    """Detects hands and extracts landmark data from camera frames."""

    _LANDMARK_COUNT = 21

    def __init__(
        self,
        max_num_hands: int = 2,
        detection_confidence: float = 0.6,
        tracking_confidence: float = 0.65,
        model_complexity: int = 0,
        draw_landmarks: bool = False,
    ) -> None:
        self.max_num_hands = max_num_hands
        self.draw_landmarks = draw_landmarks
        self._mp_hands = mp.solutions.hands
        self._mp_draw = mp.solutions.drawing_utils
        self._hands = self._mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            model_complexity=model_complexity,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )

    def process(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Process a BGR frame and return a list of detected hands.

        Each hand dict contains:
            ``pixels``      – list of (x, y) pixel coordinates per landmark
            ``normalized``  – list of (x, y, z) normalized coordinates
            ``handedness``  – ``"Left"`` or ``"Right"``
        """
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self._hands.process(rgb)

        if not results.multi_hand_landmarks:
            return []

        hands: List[Dict[str, Any]] = []
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            pixels: List[Tuple[int, int]] = []
            normalized: List[Tuple[float, float, float]] = []
            for lm in hand_landmarks.landmark:
                px, py = int(lm.x * w), int(lm.y * h)
                pixels.append((px, py))
                normalized.append((lm.x, lm.y, lm.z))

            handedness = "Right"
            if results.multi_handedness and idx < len(results.multi_handedness):
                handedness = results.multi_handedness[idx].classification[0].label

            hands.append(
                {
                    "pixels": pixels,
                    "normalized": normalized,
                    "handedness": handedness,
                }
            )

            if self.draw_landmarks:
                self._mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self._mp_hands.HAND_CONNECTIONS,
                )

        return hands

    def close(self) -> None:
        self._hands.close()
