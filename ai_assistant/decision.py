"""Decision dataclass returned by the AI assistant."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class Decision:
    """Represents the assistant's decision on how to act."""

    intent: Optional[str] = None
    action: Optional[Dict[str, Any]] = None
    confidence: float = 0.0
    should_execute: bool = False
    status: str = "idle"
    context: Optional[Dict[str, Any]] = None
