"""Core AI assistant that decides whether to execute gesture actions."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from ai_assistant.command_router import CommandRouter
from ai_assistant.context_manager import ContextManager
from ai_assistant.decision import Decision
from personalization.adaptive_learning import AdaptiveLearning

logger = logging.getLogger("gestureos.assistant")

# Events that require voice confirmation before executing
_CONFIRMATION_REQUIRED = frozenset({
    "shutdown",
    "restart",
    "lock_screen",
    "format_disk",
    "delete_all",
})

# Events blocked entirely by the security policy
_BLOCKED_INTENTS = frozenset({
    "format_disk",
    "delete_all",
})


class AIAssistant:
    """High-level decision engine for GestureOS.

    Integrates gesture predictions, voice commands, context, and
    adaptive learning to produce :class:`Decision` objects that the
    main loop executes.
    """

    def __init__(self, adaptive_learning: Optional[AdaptiveLearning] = None) -> None:
        self.context_manager = ContextManager()
        self.command_router = CommandRouter()
        self.adaptive_learning = adaptive_learning
        self.last_decision: Optional[Decision] = None
        self.pending_voice: Optional[Dict[str, Any]] = None

    # ------------------------------------------------------------------
    # Main decision entry-point
    # ------------------------------------------------------------------

    def decide(
        self,
        user_id: str,
        gesture_prediction: Optional[Dict[str, Any]] = None,
        gesture_action: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Decision:
        if context:
            self.context_manager.update(context)

        if not gesture_action:
            return Decision(status="idle")

        intent = gesture_action.get("operation")
        confidence = (gesture_prediction or {}).get("confidence", 0.8)

        if intent in _BLOCKED_INTENTS:
            return Decision(
                intent=intent,
                action=gesture_action,
                confidence=confidence,
                should_execute=False,
                status="blocked",
                context=self.context_manager.current(),
            )

        if intent in _CONFIRMATION_REQUIRED and self.pending_voice is None:
            return Decision(
                intent=intent,
                action=gesture_action,
                confidence=confidence,
                should_execute=False,
                status="awaiting_confirmation",
                context=self.context_manager.current(),
            )

        # Adjust threshold based on adaptive learning
        threshold = 0.5
        if self.adaptive_learning:
            threshold = self.adaptive_learning.suggested_threshold(
                user_id, intent or "", base=0.5
            )

        should_execute = confidence >= threshold

        decision = Decision(
            intent=intent,
            action=gesture_action,
            confidence=confidence,
            should_execute=should_execute,
            status="executed" if should_execute else "low_confidence",
            context=self.context_manager.current(),
        )

        if should_execute and self.adaptive_learning and intent:
            self.adaptive_learning.record_success(user_id, intent)

        self.last_decision = decision
        return decision

    # ------------------------------------------------------------------
    # Voice command support
    # ------------------------------------------------------------------

    def update_voice_command(
        self,
        user_id: str,
        text: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Decision:
        if context:
            self.context_manager.update(context)

        intent = self._parse_voice_intent(text)
        action = self._build_voice_action(intent)

        decision = Decision(
            intent=intent,
            action=action,
            confidence=0.9,
            should_execute=action is not None,
            status="executed" if action else "unrecognized",
            context=self.context_manager.current(),
        )
        self.last_decision = decision
        self.pending_voice = None
        return decision

    # ------------------------------------------------------------------
    # Feedback
    # ------------------------------------------------------------------

    def handle_feedback(self, accepted: bool, user_id: str = "") -> bool:
        if not self.last_decision or not self.last_decision.intent:
            return False
        if self.adaptive_learning:
            if accepted:
                self.adaptive_learning.record_success(user_id, self.last_decision.intent)
            else:
                self.adaptive_learning.record_failure(user_id, self.last_decision.intent)
        return True

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_voice_intent(text: str) -> str:
        text = text.lower().strip()
        keyword_map = {
            "mouse": "switch_mouse_mode",
            "keyboard": "switch_keyboard_mode",
            "volume up": "volume_up",
            "volume down": "volume_down",
            "screenshot": "capture_screenshot",
            "open chrome": "launch_application",
            "open browser": "launch_application",
            "lock": "lock_screen",
            "mute": "mute",
            "play": "play_pause",
            "pause": "play_pause",
            "next": "next_track",
            "previous": "previous_track",
            "scroll up": "scroll_up",
            "scroll down": "scroll_down",
            "zoom in": "zoom_in",
            "zoom out": "zoom_out",
            "sleep": "sleep_system",
            "wake": "activate_system",
        }
        for keyword, intent in keyword_map.items():
            if keyword in text:
                return intent
        return "unknown"

    @staticmethod
    def _build_voice_action(intent: str) -> Optional[Dict[str, Any]]:
        if intent == "unknown":
            return None
        if intent.startswith("switch_"):
            return {"target": "assistant", "operation": intent}
        if intent in ("volume_up", "volume_down", "mute", "play_pause",
                       "next_track", "previous_track", "capture_screenshot",
                       "lock_screen"):
            return {"target": "system", "operation": intent}
        if intent == "launch_application":
            return {"target": "system", "operation": intent, "app_name": "chrome"}
        if intent in ("scroll_up", "scroll_down", "zoom_in", "zoom_out"):
            return {"target": "mouse", "operation": intent}
        if intent in ("sleep_system", "activate_system"):
            return {"target": "assistant", "operation": intent}
        return None
