"""Base middleware class for the GestureOS EventBus pipeline."""

from __future__ import annotations

import time
from abc import ABC
from typing import Dict, Optional

from events.event_types import Event


class EventMiddleware(ABC):
    """
    Base middleware for GestureOS EventBus.

    Middleware can modify, validate, block, log, and collect analytics
    on events flowing through the bus.
    """

    def __init__(self) -> None:
        self.processed_events: int = 0
        self.blocked_events: int = 0
        self.last_event_type: Optional[str] = None
        self.last_processed_time: Optional[float] = None

    def before(self, event: Event) -> Event:
        """Executed before processing. Override if needed."""
        return event

    def after(self, event: Event) -> Event:
        """Executed after processing. Override if needed."""
        return event

    def validate(self, event: Event) -> bool:
        """Return True if the event is structurally valid."""
        return (
            event is not None
            and hasattr(event, "type")
            and bool(event.type)
        )

    def block(self, event: Event) -> bool:
        """Return True to prevent event propagation."""
        return False

    def __call__(self, event: Event) -> Event:
        if not self.validate(event):
            raise ValueError("Invalid event received by middleware.")

        if self.block(event):
            self.blocked_events += 1
            event.stop_propagation()
            return event

        event = self.before(event)

        self.processed_events += 1
        self.last_event_type = event.type
        self.last_processed_time = time.time()

        event = self.after(event)
        return event

    def statistics(self) -> Dict:
        return {
            "processed_events": self.processed_events,
            "blocked_events": self.blocked_events,
            "last_event_type": self.last_event_type,
            "last_processed_time": self.last_processed_time,
        }

    def reset(self) -> None:
        self.processed_events = 0
        self.blocked_events = 0
        self.last_event_type = None
        self.last_processed_time = None
