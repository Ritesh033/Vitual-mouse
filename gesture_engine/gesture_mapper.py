"""Map recognized gesture names to executable action descriptors."""

from __future__ import annotations

from typing import Any, Dict, Optional

from config.gesture_config import GestureConfig


class GestureMapper:
    """Looks up the action associated with a gesture name in the config."""

    def __init__(self, config: GestureConfig) -> None:
        self._gestures: Dict[str, Dict[str, Any]] = config.data.get("gestures", {})

    def get_action(
        self,
        gesture_name: Optional[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        if not gesture_name:
            return None

        entry = self._gestures.get(gesture_name)
        if entry is None:
            return None

        action = dict(entry.get("action", {}))

        # Let context override the target when in a specific mode
        if context and "mode" in context:
            mode = context["mode"]
            if mode == "keyboard" and action.get("target") == "mouse":
                return None

        return action or None
