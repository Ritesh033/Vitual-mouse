"""Analytics middleware for the GestureOS EventBus."""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Dict, List

from events.event_middleware import EventMiddleware
from events.event_types import Event


class AnalyticsMiddleware(EventMiddleware):
    """Collects per-event-type counts and timing information."""

    def __init__(self) -> None:
        super().__init__()
        self._counts: Dict[str, int] = defaultdict(int)
        self._latencies: Dict[str, List[float]] = defaultdict(list)
        self._event_start: float = 0.0

    def before(self, event: Event) -> Event:
        self._event_start = time.perf_counter()
        self._counts[event.type] += 1
        return event

    def after(self, event: Event) -> Event:
        elapsed_ms = (time.perf_counter() - self._event_start) * 1000.0
        self._latencies[event.type].append(elapsed_ms)
        return event

    def summary(self) -> Dict:
        result: Dict = {}
        for event_type, count in self._counts.items():
            latencies = self._latencies.get(event_type, [])
            avg_ms = sum(latencies) / len(latencies) if latencies else 0.0
            result[event_type] = {
                "count": count,
                "avg_latency_ms": round(avg_ms, 3),
            }
        return result

    def reset(self) -> None:
        super().reset()
        self._counts.clear()
        self._latencies.clear()
