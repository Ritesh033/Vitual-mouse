"""Shared fixtures for GestureOS tests."""

import sys
import types
from unittest.mock import MagicMock

import pytest


def _stub_module(name, attrs=None):
    """Create a stub module and register it in sys.modules."""
    mod = types.ModuleType(name)
    for attr_name, attr_val in (attrs or {}).items():
        setattr(mod, attr_name, attr_val)
    sys.modules[name] = mod
    return mod


# ---- Stub heavy / unavailable third-party packages before any project import ----

# cv2 stub
_cv2 = _stub_module("cv2", {
    "circle": MagicMock(),
    "line": MagicMock(),
    "rectangle": MagicMock(),
    "addWeighted": MagicMock(),
    "putText": MagicMock(),
    "FONT_HERSHEY_SIMPLEX": 0,
    "flip": MagicMock(side_effect=lambda f, c: f),
    "VideoCapture": MagicMock(),
    "CAP_DSHOW": 0,
    "CAP_PROP_FRAME_WIDTH": 3,
    "CAP_PROP_FRAME_HEIGHT": 4,
    "CAP_PROP_FPS": 5,
    "CAP_PROP_BUFFERSIZE": 38,
    "imshow": MagicMock(),
    "waitKey": MagicMock(return_value=27),
    "destroyAllWindows": MagicMock(),
})

# pyautogui stub
_pyautogui = _stub_module("pyautogui", {
    "hotkey": MagicMock(),
    "press": MagicMock(),
    "screenshot": MagicMock(),
    "FAILSAFE": True,
    "PAUSE": 0.1,
})

# keyboard stub
_keyboard = _stub_module("keyboard", {
    "press_and_release": MagicMock(),
    "send": MagicMock(),
})

# Stub all internal sub-packages that main.py imports but don't exist on disk.
_internal_stubs = {
    "ai_assistant": {},
    "ai_assistant.assistant": {"AIAssistant": MagicMock},
    "analytics": {},
    "analytics.false_positive_tracker": {"FalsePositiveTracker": MagicMock},
    "analytics.metrics_collector": {"MetricsCollector": MagicMock},
    "analytics.performance_monitor": {"PerformanceMonitor": MagicMock},
    "camera": {},
    "camera.distance_estimator": {"DistanceEstimator": MagicMock},
    "config": {},
    "config.gesture_config": {"GestureConfig": MagicMock},
    "gesture_engine": {},
    "gesture_engine.gesture_classifier": {"GestureClassifier": MagicMock},
    "gesture_engine.gesture_mapper": {"GestureMapper": MagicMock},
    "keyboard_control": {},
    "keyboard_control.keyboard_controller": {"KeyboardController": MagicMock},
    "mouse_control": {},
    "mouse_control.cursor_controller": {"CursorController": MagicMock},
    "personalization": {},
    "personalization.adaptive_learning": {"AdaptiveLearning": MagicMock},
    "personalization.user_profiles": {"UserProfiles": MagicMock},
    "system_control": {},
    "system_control.system_controller": {"SystemController": MagicMock},
    "system_control.app_launcher": {"AppLauncher": MagicMock},
    "system_control.window_manager": {"WindowManager": MagicMock},
    "vision": {},
    "vision.hand_detector": {"HandDetector": MagicMock},
    "voice_control": {},
    "voice_control.speech_to_text": {"SpeechToText": MagicMock},
    "smart_home": {},
    "smart_home.smart_home_controller": {"SmartHomeController": MagicMock},
}

for mod_name, attrs in _internal_stubs.items():
    if mod_name not in sys.modules:
        _stub_module(mod_name, attrs)


# ---- Fixtures ----

@pytest.fixture()
def numpy_frame():
    """Return a small fake frame as a numpy-like object with .shape and .copy()."""
    import numpy as np
    return np.zeros((480, 640, 3), dtype=np.uint8)
