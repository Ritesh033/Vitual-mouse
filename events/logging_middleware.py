"""Logging middleware for the GestureOS EventBus."""

from __future__ import annotations

import logging
from typing import Optional

from events.event_middleware import EventMiddleware
from events.event_types import Event

logger = logging.getLogger("gestureos.events")


class LoggingMiddleware(EventMiddleware):
    """Logs every event that passes through the bus."""

    def __init__(self, level: int = logging.DEBUG, prefix: Optional[str] = None) -> None:
        super().__init__()
        self.level = level
        self.prefix = prefix or "[EVENT]"

    def before(self, event: Event) -> Event:
        logger.log(
            self.level,
            "%s %s (source=%s)",
            self.prefix,
            event.type,
            event.source,
        )
        return event
