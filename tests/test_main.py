"""Tests for main.py helper functions."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from main import (
    apply_decision,
    capture_voice_command,
    draw_hand_pointer,
    draw_information,
    draw_virtual_cursor,
    humanize,
)


# ---------- humanize ----------


class TestHumanize:
    def test_replaces_underscores(self):
        assert humanize("move_cursor") == "Move Cursor"

    def test_none_returns_idle(self):
        assert humanize(None) == "Idle"

    def test_empty_string_returns_idle(self):
        assert humanize("") == "Idle"

    def test_single_word(self):
        assert humanize("scroll") == "Scroll"

    def test_multi_underscore(self):
        assert humanize("open_new_tab") == "Open New Tab"

    def test_already_clean(self):
        assert humanize("Click") == "Click"


# ---------- draw_virtual_cursor ----------


class TestDrawVirtualCursor:
    def test_returns_frame_unchanged_when_no_position(self, numpy_frame):
        result = draw_virtual_cursor(numpy_frame, None)
        assert result is numpy_frame

    def test_draws_tracking_cursor(self, numpy_frame):
        import cv2

        cv2.circle.reset_mock()
        cv2.line.reset_mock()
        result = draw_virtual_cursor(numpy_frame, (100, 200), tracking=True)
        assert result is numpy_frame
        assert cv2.circle.call_count == 2
        assert cv2.line.call_count == 2

    def test_draws_non_tracking_cursor(self, numpy_frame):
        import cv2

        cv2.circle.reset_mock()
        cv2.line.reset_mock()
        draw_virtual_cursor(numpy_frame, (50, 60), tracking=False)
        assert cv2.circle.call_count == 2
        # First circle call: frame, center, radius, colour, thickness
        args = cv2.circle.call_args_list[0][0]
        assert args[1] == (50, 60)  # center position
        assert args[3] == (120, 200, 255)  # non-tracking colour


# ---------- draw_hand_pointer ----------


class TestDrawHandPointer:
    def test_returns_none_when_no_hands(self, numpy_frame):
        assert draw_hand_pointer(numpy_frame, None) is None
        assert draw_hand_pointer(numpy_frame, []) is None

    def test_returns_index_tip(self, numpy_frame):
        hands = [{"pixels": {8: (320, 240)}}]
        result = draw_hand_pointer(numpy_frame, hands, tracking=False)
        assert result == (320, 240)

    def test_tracking_colour_differs(self, numpy_frame):
        import cv2

        cv2.circle.reset_mock()
        hands = [{"pixels": {8: (100, 100)}}]
        draw_hand_pointer(numpy_frame, hands, tracking=True)
        # First circle: frame, center, radius, colour, thickness
        colour_used = cv2.circle.call_args_list[0][0][3]
        assert colour_used == (65, 245, 115)  # tracking colour

    def test_non_tracking_colour(self, numpy_frame):
        import cv2

        cv2.circle.reset_mock()
        hands = [{"pixels": {8: (50, 50)}}]
        draw_hand_pointer(numpy_frame, hands, tracking=False)
        # filled circle colour should be (90, 190, 255)
        colour_arg = cv2.circle.call_args_list[0][0][3]
        assert colour_arg == (90, 190, 255)


# ---------- draw_information ----------


class TestDrawInformation:
    def test_returns_frame(self, numpy_frame):
        result = draw_information(numpy_frame, "fist", True, "mouse", "chrome")
        assert result is numpy_frame

    def test_info_text_drawn(self, numpy_frame):
        import cv2

        cv2.putText.reset_mock()
        draw_information(numpy_frame, "fist", True, "mouse", "chrome", info_text="Hello")
        texts = [c[0][1] for c in cv2.putText.call_args_list]
        assert any("Hello" in t for t in texts)

    def test_distance_text_drawn(self, numpy_frame):
        import cv2

        cv2.putText.reset_mock()
        draw_information(
            numpy_frame, "fist", True, "mouse", "chrome", distance_text="50 cm"
        )
        texts = [c[0][1] for c in cv2.putText.call_args_list]
        assert any("50 cm" in t for t in texts)

    def test_performance_drawn(self, numpy_frame):
        import cv2

        cv2.putText.reset_mock()
        perf = {"fps": 30, "avg_inference_ms": 12}
        draw_information(
            numpy_frame, "fist", True, "mouse", "chrome", performance=perf
        )
        texts = [c[0][1] for c in cv2.putText.call_args_list]
        assert any("FPS 30" in t for t in texts)

    def test_pending_voice_drawn(self, numpy_frame):
        import cv2

        cv2.putText.reset_mock()
        evidence = SimpleNamespace(raw_value="open chrome", intent="launch_app")
        pending = {"evidence": evidence}
        draw_information(
            numpy_frame,
            "fist",
            True,
            "mouse",
            "chrome",
            pending_voice=pending,
        )
        texts = [c[0][1] for c in cv2.putText.call_args_list]
        assert any("open chrome" in t for t in texts)

    def test_pending_voice_falls_back_to_intent(self, numpy_frame):
        import cv2

        cv2.putText.reset_mock()
        evidence = SimpleNamespace(raw_value=None, intent="launch_app")
        pending = {"evidence": evidence}
        draw_information(
            numpy_frame, "fist", True, "mouse", "chrome", pending_voice=pending
        )
        texts = [c[0][1] for c in cv2.putText.call_args_list]
        assert any("launch_app" in t for t in texts)


# ---------- apply_decision ----------


class TestApplyDecision:
    @staticmethod
    def _decision(intent, action, should_execute=True, confidence=0.9, status="ok", context=None):
        return SimpleNamespace(
            intent=intent,
            action=action,
            should_execute=should_execute,
            confidence=confidence,
            status=status,
            context=context,
        )

    # --- assistant target ---

    def test_switch_mouse_mode(self):
        d = self._decision("switch_mouse_mode", {"target": "assistant", "operation": "switch_mouse_mode"})
        active, mode, freeze, info = apply_decision(d, [], {}, MagicMock(), True, "keyboard", True)
        assert mode == "mouse"
        assert freeze is False

    def test_switch_keyboard_mode(self):
        d = self._decision("switch_keyboard", {"target": "assistant", "operation": "switch_keyboard_mode"})
        active, mode, freeze, info = apply_decision(d, [], {}, MagicMock(), True, "mouse", False)
        assert mode == "keyboard"

    def test_activate_system(self):
        d = self._decision("activate", {"target": "assistant", "operation": "activate_system"})
        active, mode, freeze, info = apply_decision(d, [], {}, MagicMock(), False, "mouse", False)
        assert active is True

    def test_sleep_system(self):
        d = self._decision("sleep", {"target": "assistant", "operation": "sleep_system"})
        active, mode, freeze, info = apply_decision(d, [], {}, MagicMock(), True, "mouse", False)
        assert active is False

    def test_unknown_assistant_operation(self):
        d = self._decision("something", {"target": "assistant", "operation": "unknown"})
        active, mode, freeze, info = apply_decision(d, [], {}, MagicMock(), True, "mouse", False)
        assert active is True

    # --- mouse target ---

    def test_mouse_ignored_when_inactive(self):
        d = self._decision("click", {"target": "mouse", "operation": "click"})
        active, mode, freeze, info = apply_decision(d, [], {}, MagicMock(), False, "mouse", False)
        assert "ignored" in info.lower()

    def test_mouse_ignored_in_keyboard_mode(self):
        d = self._decision("click", {"target": "mouse", "operation": "click"})
        active, mode, freeze, info = apply_decision(d, [], {}, MagicMock(), True, "keyboard", False)
        assert "ignored" in info.lower()

    def test_move_cursor(self):
        mouse_ctrl = MagicMock()
        controllers = {"mouse": mouse_ctrl}
        hands = [{"normalized": {8: (0.5, 0.5)}}]
        d = self._decision("move", {"target": "mouse", "operation": "move_cursor"})
        active, mode, freeze, info = apply_decision(d, hands, controllers, MagicMock(), True, "mouse", False)
        mouse_ctrl.move_cursor.assert_called_once_with((0.5, 0.5))
        assert "tracking" in info.lower()

    def test_move_cursor_frozen(self):
        mouse_ctrl = MagicMock()
        controllers = {"mouse": mouse_ctrl}
        hands = [{"normalized": {8: (0.5, 0.5)}}]
        d = self._decision("move", {"target": "mouse", "operation": "move_cursor"})
        router = MagicMock()
        active, mode, freeze, info = apply_decision(d, hands, controllers, router, True, "mouse", True)
        mouse_ctrl.move_cursor.assert_not_called()
        router.execute.assert_called_once()

    def test_stop_cursor(self):
        d = self._decision("stop", {"target": "mouse", "operation": "stop_cursor"})
        active, mode, freeze, info = apply_decision(d, [], {}, MagicMock(), True, "mouse", False)
        assert freeze is True

    def test_drag_hold(self):
        mouse_ctrl = MagicMock()
        controllers = {"mouse": mouse_ctrl}
        d = self._decision("drag", {"target": "mouse", "operation": "drag_hold"})
        active, mode, freeze, info = apply_decision(d, [], controllers, MagicMock(), True, "mouse", False)
        mouse_ctrl.start_drag.assert_called_once()
        assert "dragging" in info.lower()

    def test_other_mouse_operation(self):
        router = MagicMock()
        d = self._decision("click", {"target": "mouse", "operation": "click"})
        active, mode, freeze, info = apply_decision(d, [], {"mouse": MagicMock()}, router, True, "mouse", False)
        router.execute.assert_called_once()

    # --- keyboard target ---

    def test_keyboard_ignored_while_sleeping(self):
        d = self._decision("type", {"target": "keyboard", "operation": "type"})
        active, mode, freeze, info = apply_decision(d, [], {}, MagicMock(), False, "keyboard", False)
        assert "ignored" in info.lower()

    def test_keyboard_action_executed(self):
        router = MagicMock()
        controllers = {"keyboard": MagicMock()}
        d = self._decision("type", {"target": "keyboard", "operation": "type"})
        active, mode, freeze, info = apply_decision(d, [], controllers, router, True, "keyboard", False)
        router.execute.assert_called_once()

    # --- system target ---

    def test_system_ignored_while_sleeping(self):
        d = self._decision("screenshot", {"target": "system", "operation": "capture_screenshot"})
        active, mode, freeze, info = apply_decision(d, [], {}, MagicMock(), False, "mouse", False)
        assert "ignored" in info.lower()

    def test_system_screenshot(self):
        router = MagicMock(execute=MagicMock(return_value="/path/shot.png"))
        d = self._decision("screenshot", {"target": "system", "operation": "capture_screenshot"})
        active, mode, freeze, info = apply_decision(d, [], {}, router, True, "mouse", False)
        assert "screenshot" in info.lower()

    def test_system_launch_app_success(self):
        router = MagicMock(execute=MagicMock(return_value=True))
        d = self._decision("launch", {"target": "system", "operation": "launch_application", "app_name": "chrome"})
        active, mode, freeze, info = apply_decision(d, [], {}, router, True, "mouse", False)
        assert "opened" in info.lower()

    def test_system_launch_app_failure(self):
        router = MagicMock(execute=MagicMock(return_value=False))
        d = self._decision("launch", {"target": "system", "operation": "launch_application", "app_name": "blender"})
        active, mode, freeze, info = apply_decision(d, [], {}, router, True, "mouse", False)
        assert "could not" in info.lower()

    # --- unknown target ---

    def test_unknown_target_passthrough(self):
        d = self._decision("foo", {"target": "unknown", "operation": "bar"})
        active, mode, freeze, info = apply_decision(d, [], {}, MagicMock(), True, "mouse", False)
        assert active is True

    # --- None action ---

    def test_none_action_fields(self):
        d = self._decision("idle", None)
        active, mode, freeze, info = apply_decision(d, [], {}, MagicMock(), True, "mouse", False)
        assert active is True


# ---------- capture_voice_command ----------


class TestCaptureVoiceCommand:
    def test_lazy_initializes_speech(self):
        runtime = {"speech": None}
        with patch.dict("sys.modules", {"voice_control.speech_to_text": MagicMock()}):
            from voice_control.speech_to_text import SpeechToText

            mock_stt = MagicMock()
            mock_stt.listen.return_value = "hello"
            SpeechToText.return_value = mock_stt
            text, msg = capture_voice_command(runtime)
        assert runtime["speech"] is not None

    def test_returns_none_on_init_failure(self):
        runtime = {"speech": None}
        with patch.dict("sys.modules", {"voice_control.speech_to_text": MagicMock()}) as patched:
            from voice_control import speech_to_text

            speech_to_text.SpeechToText = MagicMock(side_effect=RuntimeError("no mic"))
            text, msg = capture_voice_command(runtime)
        assert text is None
        assert "unavailable" in msg.lower()

    def test_returns_none_when_not_understood(self):
        mock_stt = MagicMock()
        mock_stt.listen.return_value = None
        runtime = {"speech": mock_stt}
        text, msg = capture_voice_command(runtime)
        assert text is None
        assert "not understood" in msg.lower()

    def test_returns_text_on_success(self):
        mock_stt = MagicMock()
        mock_stt.listen.return_value = "open chrome"
        runtime = {"speech": mock_stt}
        text, msg = capture_voice_command(runtime)
        assert text == "open chrome"
        assert "open chrome" in msg

    def test_listen_exception(self):
        mock_stt = MagicMock()
        mock_stt.listen.side_effect = RuntimeError("timeout")
        runtime = {"speech": mock_stt}
        text, msg = capture_voice_command(runtime)
        assert text is None
        assert "error" in msg.lower()
