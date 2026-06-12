"""Route actions from gesture decisions to the appropriate controller."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("gestureos.router")


class CommandRouter:
    """Dispatch action dicts to the corresponding controller method."""

    def execute(
        self,
        action: Dict[str, Any],
        controllers: Dict[str, Any],
    ) -> Optional[Any]:
        if not action:
            return None

        target = action.get("target")
        operation = action.get("operation")
        if not target or not operation:
            return None

        controller = controllers.get(target)
        if controller is None:
            logger.warning("No controller for target '%s'", target)
            return None

        method = getattr(controller, operation, None)
        if method is None:
            logger.warning(
                "Controller '%s' has no method '%s'",
                target,
                operation,
            )
            return None

        try:
            # Pass through extra action params as kwargs
            kwargs = {
                k: v
                for k, v in action.items()
                if k not in ("target", "operation")
            }
            return method(**kwargs) if kwargs else method()
        except Exception:
            logger.exception("Error executing %s.%s", target, operation)
            return None
