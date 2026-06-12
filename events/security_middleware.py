"""Security middleware for the GestureOS EventBus."""

from __future__ import annotations

import logging
from typing import FrozenSet

from events.event_middleware import EventMiddleware
from events.event_types import Event

logger = logging.getLogger("gestureos.security")

DEFAULT_BLOCKED_EVENTS: FrozenSet[str] = frozenset({
    "shutdown",
    "restart",
    "format_disk",
    "delete_all",
})


class SecurityMiddleware(EventMiddleware):
    """Blocks dangerous event types from propagating through the bus."""

    def __init__(self, blocked_events: FrozenSet[str] = DEFAULT_BLOCKED_EVENTS) -> None:
        super().__init__()
        self._blocked_events = blocked_events

    def block(self, event: Event) -> bool:
        if event.type in self._blocked_events:
            logger.warning("Blocked dangerous event: %s", event.type)
            return True
        return False
