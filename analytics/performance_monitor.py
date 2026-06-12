"""Real-time performance monitoring for GestureOS."""

from __future__ import annotations

import time
from collections import deque
from typing import Any, Deque, Dict


class PerformanceMonitor:
    """Track FPS and per-frame inference latency."""

    def __init__(self, window_size: int = 60) -> None:
        self._window_size = window_size
        self._frame_times: Deque[float] = deque(maxlen=window_size)
        self._inference_times: Deque[float] = deque(maxlen=window_size)

    def record_frame(self) -> None:
        self._frame_times.append(time.perf_counter())

    def record_inference(self, ms: float) -> None:
        self._inference_times.append(ms)

    def snapshot(self) -> Dict[str, Any]:
        fps = 0
        if len(self._frame_times) >= 2:
            elapsed = self._frame_times[-1] - self._frame_times[0]
            if elapsed > 0:
                fps = int((len(self._frame_times) - 1) / elapsed)

        avg_ms = 0.0
        if self._inference_times:
            avg_ms = round(sum(self._inference_times) / len(self._inference_times), 1)

        return {"fps": fps, "avg_inference_ms": avg_ms}
