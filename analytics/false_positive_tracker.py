"""Track false-positive gesture detections for continuous improvement."""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Any, Dict, List, Optional


class FalsePositiveTracker:
    """Records rejected gestures so the system can learn from mistakes."""

    def __init__(self) -> None:
        self._records: List[Dict[str, Any]] = []
        self._counts: Dict[str, int] = defaultdict(int)

    def record(self, intent: str, context: Optional[Dict[str, Any]] = None) -> None:
        self._counts[intent] += 1
        self._records.append(
            {
                "intent": intent,
                "context": context or {},
                "timestamp": time.time(),
            }
        )

    def summary(self) -> Dict[str, int]:
        return dict(self._counts)

    @property
    def total(self) -> int:
        return sum(self._counts.values())
