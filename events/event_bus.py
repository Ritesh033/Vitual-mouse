"""EventBus with middleware pipeline for GestureOS."""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Callable, Dict, List, Optional

from events.event_middleware import EventMiddleware
from events.event_types import Event

logger = logging.getLogger("gestureos.eventbus")

Listener = Callable[[Event], None]


class EventBus:
    """
    Central event dispatcher with an ordered middleware pipeline.

    Usage::

        bus = EventBus()
        bus.add_middleware(LoggingMiddleware())
        bus.add_middleware(SecurityMiddleware())

        bus.subscribe("gesture_detected", handler_fn)
        bus.emit(Event(type="gesture_detected", data={...}))
    """

    def __init__(self) -> None:
        self._middleware: List[EventMiddleware] = []
        self._listeners: Dict[str, List[Listener]] = defaultdict(list)

    # ------------------------------------------------------------------
    # Middleware management
    # ------------------------------------------------------------------

    def add_middleware(self, middleware: EventMiddleware) -> None:
        self._middleware.append(middleware)

    def remove_middleware(self, middleware: EventMiddleware) -> None:
        self._middleware.remove(middleware)

    # ------------------------------------------------------------------
    # Subscriptions
    # ------------------------------------------------------------------

    def subscribe(self, event_type: str, listener: Listener) -> None:
        self._listeners[event_type].append(listener)

    def unsubscribe(self, event_type: str, listener: Listener) -> None:
        listeners = self._listeners.get(event_type, [])
        if listener in listeners:
            listeners.remove(listener)

    # ------------------------------------------------------------------
    # Emit
    # ------------------------------------------------------------------

    def emit(self, event: Event) -> Optional[Event]:
        """
        Push *event* through the middleware pipeline, then dispatch to
        all listeners registered for ``event.type``.

        Returns the (possibly modified) event, or ``None`` if a
        middleware blocked propagation.
        """
        for mw in self._middleware:
            event = mw(event)
            if not event.propagate:
                logger.debug("Event %s blocked by %s", event.type, type(mw).__name__)
                return None

        for listener in self._listeners.get(event.type, []):
            try:
                listener(event)
            except Exception:
                logger.exception(
                    "Listener %s raised for event %s",
                    listener,
                    event.type,
                )
        return event

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def middleware_stats(self) -> List[Dict]:
        return [
            {"name": type(mw).__name__, **mw.statistics()}
            for mw in self._middleware
        ]
