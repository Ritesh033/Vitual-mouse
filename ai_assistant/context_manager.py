"""Runtime context manager that tracks the current application state."""

from __future__ import annotations

from typing import Any, Dict


class ContextManager:
    """Maintains and merges runtime context for the AI assistant."""

    def __init__(self) -> None:
        self._context: Dict[str, Any] = {
            "mode": "mouse",
            "active": True,
            "application_category": "unknown",
            "smart_home_active": False,
        }

    def update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        self._context.update(data)
        return dict(self._context)

    def current(self) -> Dict[str, Any]:
        return dict(self._context)

    def get(self, key: str, default: Any = None) -> Any:
        return self._context.get(key, default)
