"""Gesture usage metrics collection for GestureOS."""

from __future__ import annotations

import json
import logging
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger("gestureos.metrics")


class MetricsCollector:
    """Collects gesture counts, confidence, and session stats."""

    def __init__(self, output_path: str = "analytics_data.json") -> None:
        self._output_path = Path(output_path)
        self._gesture_counts: Dict[str, int] = defaultdict(int)
        self._gesture_confidences: Dict[str, List[float]] = defaultdict(list)
        self._sessions: List[Dict[str, Any]] = []
        self._start_time = time.time()

    def record_gesture(self, intent: str, confidence: float) -> None:
        self._gesture_counts[intent] += 1
        self._gesture_confidences[intent].append(confidence)

    def record_session(self, duration_seconds: int, accuracy: float) -> None:
        self._sessions.append(
            {
                "duration_seconds": duration_seconds,
                "accuracy": accuracy,
                "timestamp": time.time(),
            }
        )

    def save(self) -> None:
        summary: Dict[str, Any] = {}
        for gesture, count in self._gesture_counts.items():
            confs = self._gesture_confidences.get(gesture, [])
            avg = sum(confs) / len(confs) if confs else 0.0
            summary[gesture] = {"count": count, "avg_confidence": round(avg, 4)}

        data = {
            "gestures": summary,
            "sessions": self._sessions,
        }
        try:
            with open(self._output_path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2)
            logger.info("Metrics saved to %s", self._output_path)
        except OSError as exc:
            logger.error("Failed to save metrics: %s", exc)

    def summary(self) -> Dict[str, Any]:
        return dict(self._gesture_counts)
