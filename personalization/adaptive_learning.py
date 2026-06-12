"""Adaptive learning module that adjusts gesture recognition per user."""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, Dict

from personalization.user_profiles import UserProfiles

logger = logging.getLogger("gestureos.adaptive")


class AdaptiveLearning:
    """Tracks per-user gesture accuracy and adjusts thresholds over time."""

    def __init__(self, profiles: UserProfiles) -> None:
        self._profiles = profiles
        self._success: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self._failure: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

    def record_success(self, user_id: str, gesture: str) -> None:
        self._success[user_id][gesture] += 1

    def record_failure(self, user_id: str, gesture: str) -> None:
        self._failure[user_id][gesture] += 1

    def accuracy(self, user_id: str, gesture: str) -> float:
        s = self._success[user_id].get(gesture, 0)
        f = self._failure[user_id].get(gesture, 0)
        total = s + f
        return s / total if total > 0 else 1.0

    def suggested_threshold(self, user_id: str, gesture: str, base: float = 0.7) -> float:
        acc = self.accuracy(user_id, gesture)
        if acc < 0.6:
            return min(0.95, base + 0.15)
        if acc > 0.9:
            return max(0.5, base - 0.1)
        return base
