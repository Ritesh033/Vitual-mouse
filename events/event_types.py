"""Event definitions for the GestureOS event system."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class Event:
    """Represents a single event flowing through the GestureOS EventBus."""

    type: str
    data: Dict[str, Any] = field(default_factory=dict)
    source: str = "unknown"
    timestamp: float = field(default_factory=time.time)
    propagate: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def stop_propagation(self) -> None:
        self.propagate = False

    def with_metadata(self, key: str, value: Any) -> "Event":
        self.metadata[key] = value
        return self


@dataclass
class GestureEvent(Event):
    """Event emitted when a gesture is recognized."""

    gesture_name: Optional[str] = None
    confidence: float = 0.0
    hand_index: int = 0


@dataclass
class SystemEvent(Event):
    """Event for system-level operations (shutdown, lock, screenshot, etc.)."""

    operation: Optional[str] = None
    target: Optional[str] = None


@dataclass
class VoiceEvent(Event):
    """Event emitted when a voice command is captured."""

    transcript: Optional[str] = None
    intent: Optional[str] = None
