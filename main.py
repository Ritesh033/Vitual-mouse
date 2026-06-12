import logging
import time

import cv2

from ai_assistant.assistant import AIAssistant
from analytics.false_positive_tracker import FalsePositiveTracker
from analytics.metrics_collector import MetricsCollector
from analytics.performance_monitor import PerformanceMonitor
from camera.distance_estimator import DistanceEstimator
from config.gesture_config import GestureConfig
from gesture_engine.gesture_classifier import GestureClassifier
from gesture_engine.gesture_mapper import GestureMapper
from keyboard_control.keyboard_controller import KeyboardController
from mouse_control.cursor_controller import CursorController
from personalization.adaptive_learning import AdaptiveLearning
from personalization.user_profiles import UserProfiles
from system_control.system_controller import SystemController
from vision.hand_detector import HandDetector

logger = logging.getLogger(__name__)

DEFAULT_USER_ID = "default_user"


def humanize(value):
    return (value or "idle").replace("_", " ").title()


def draw_virtual_cursor(frame, cursor_position, tracking=False):
    if not cursor_position:
        return frame

    x, y = cursor_position
    color = (70, 235, 110) if tracking else (120, 200, 255)
    cv2.circle(frame, (x, y), 8, color, 2)
    cv2.circle(frame, (x, y), 2, color, -1)
    cv2.line(frame, (x - 12, y), (x + 12, y), color, 1)
    cv2.line(frame, (x, y - 12), (x, y + 12), color, 1)
    return frame


def draw_hand_pointer(frame, hands, tracking=False):
    if not hands:
        return None

    index_tip = hands[0]["pixels"][8]
    color = (65, 245, 115) if tracking else (90, 190, 255)
    cv2.circle(frame, index_tip, 7, color, -1)
    cv2.circle(frame, index_tip, 13, color, 2)
    return index_tip


def draw_information(
    frame,
    gesture_name,
    active,
    mode,
    application,
    info_text="",
    distance_text="",
    performance=None,
    pending_voice=None,
):
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (frame.shape[1], 118), (8, 8, 8), -1)
    cv2.addWeighted(overlay, 0.62, frame, 0.38, 0, frame)

    status_text = f"Gesture: {gesture_name or 'None'} | Active: {active} | Mode: {mode} | App: {application}"
    cv2.putText(frame, status_text, (12, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (230, 230, 230), 2)

    if info_text:
        cv2.putText(frame, info_text, (12, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.54, (195, 235, 195), 2)
    if distance_text:
        cv2.putText(frame, distance_text, (12, 74), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (205, 205, 205), 1)

    if pending_voice:
        evidence = pending_voice.get("evidence")
        voice_text = evidence.raw_value or evidence.intent
        cv2.putText(frame, f"Confirm: {voice_text}", (12, 96), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (170, 220, 245), 1)

    if performance:
        perf_text = f"FPS {performance['fps']} | Loop {performance['avg_inference_ms']} ms | V voice | U undo false action | Q quit"
        cv2.putText(frame, perf_text, (12, 114), cv2.FONT_HERSHEY_SIMPLEX, 0.43, (180, 180, 180), 1)

    return frame


def capture_voice_command(voice_runtime):
    if voice_runtime.get("speech") is None:
        try:
            from voice_control.speech_to_text import SpeechToText

            voice_runtime["speech"] = SpeechToText()
        except Exception as exc:
            return None, f"Voice unavailable: {exc}"

    try:
        text = voice_runtime["speech"].listen(timeout=4, phrase_time_limit=6)
    except Exception as exc:
        return None, f"Voice error: {exc}"

    if not text:
        return None, "Voice not understood."
    return text, f"Voice: {text}"


def apply_decision(decision, hands, controllers, router, active, mode, freeze_cursor):
    action = decision.action or {}
    target = action.get("target")
    operation = action.get("operation")
    info_text = humanize(decision.intent)

    if target == "assistant":
        if operation == "switch_mouse_mode":
            return active, "mouse", False, "Mouse mode"
        if operation == "switch_keyboard_mode":
            return active, "keyboard", freeze_cursor, "Keyboard mode"
        if operation == "activate_system":
            return True, mode, False, "Activation complete"
        if operation == "sleep_system":
            return False, mode, False, "Sleep mode"
        return active, mode, freeze_cursor, info_text

    if target == "mouse":
        if not active or mode != "mouse":
            return active, mode, freeze_cursor, "Mouse intent ignored in current mode"
        if operation == "move_cursor" and hands and not freeze_cursor:
            controllers["mouse"].move_cursor(hands[0]["normalized"][8])
            return active, mode, False, "Cursor tracking"
        if operation == "stop_cursor":
            return active, mode, True, "Cursor frozen"
        if operation == "drag_hold":
            controllers["mouse"].start_drag()
            return active, mode, False, "Dragging"
        try:
            router.execute(action, controllers)
        except Exception as exc:
            logger.error("Router failed to execute mouse action %s: %s", operation, exc)
            return active, mode, freeze_cursor, f"Mouse action failed: {operation}"
        return active, mode, False, info_text

    if target == "keyboard":
        if not active:
            return active, mode, freeze_cursor, "Keyboard intent ignored while sleeping"
        try:
            router.execute(action, controllers)
        except Exception as exc:
            logger.error("Router failed to execute keyboard action %s: %s", operation, exc)
            return active, mode, freeze_cursor, f"Keyboard action failed: {operation}"
        return active, mode, freeze_cursor, info_text

    if target == "system":
        if not active:
            return active, mode, freeze_cursor, "System intent ignored while sleeping"
        try:
            result = router.execute(action, controllers)
        except Exception as exc:
            logger.error("Router failed to execute system action %s: %s", operation, exc)
            return active, mode, freeze_cursor, f"System action failed: {operation}"
        if operation == "capture_screenshot" and result:
            return active, mode, freeze_cursor, f"Screenshot saved: {result}"
        if operation == "launch_application":
            app_name = action.get("app_name", "app")
            return active, mode, freeze_cursor, f"Opened {app_name}" if result else f"Could not open {app_name}"
        return active, mode, freeze_cursor, info_text

    return active, mode, freeze_cursor, info_text


def execute_decision(decision, hands, controllers, router, active, mode,
                     freeze_cursor, metrics):
    """Apply a decision and record bookkeeping metrics.

    Consolidates the duplicated apply → humanize → record_gesture sequence
    that was repeated for both gesture and voice code-paths.
    """
    active, mode, freeze_cursor, info_text = apply_decision(
        decision, hands, controllers, router, active, mode, freeze_cursor,
    )
    last_action = humanize(decision.intent)
    if decision.intent not in {"move_cursor", "drag_hold"}:
        metrics.record_gesture(decision.intent, decision.confidence)
    return active, mode, freeze_cursor, info_text, last_action


def build_cursor_controller(config):
    sensitivity = config.data.get("sensitivity", {})
    cursor_speed = sensitivity.get("cursor_speed", 1.15)
    smoothing_enabled = sensitivity.get("smoothing", True)
    return CursorController(
        smoothing=sensitivity.get("smoothing_factor", 4) if smoothing_enabled else 1,
        speed=cursor_speed,
        deadzone_px=sensitivity.get("deadzone_px", 2),
        edge_margin=sensitivity.get("edge_margin", 0.07),
        adaptive_smoothing=sensitivity.get("adaptive_smoothing", True),
    )


def main():
    config = GestureConfig("config/gestures.yaml")
    debug_settings = config.data.get("debug", {})
    camera_settings = config.data.get("camera", {})

    detector = HandDetector(
        max_num_hands=2,
        detection_confidence=camera_settings.get("detection_confidence", 0.6),
        tracking_confidence=camera_settings.get("tracking_confidence", 0.65),
        model_complexity=camera_settings.get("model_complexity", 0),
        draw_landmarks=debug_settings.get("show_landmarks", False),
    )
    classifier = GestureClassifier()
    mapper = GestureMapper(config)
    mouse_controller = build_cursor_controller(config)
    keyboard_controller = KeyboardController()
    system_controller = SystemController()

    profiles = UserProfiles()
    profiles.ensure_user(DEFAULT_USER_ID, {"display_name": "Primary User"})
    assistant = AIAssistant(adaptive_learning=AdaptiveLearning(profiles))

    metrics = MetricsCollector()
    false_positive_tracker = FalsePositiveTracker()
    performance_monitor = PerformanceMonitor()
    distance_estimator = DistanceEstimator(camera_settings.get("distance_calibration", 9.5))

    min_distance_cm = camera_settings.get("min_distance_cm", 25)
    max_distance_cm = camera_settings.get("max_distance_cm", 170)
    ideal_distance_cm = camera_settings.get("ideal_distance_cm", 65)

    cam_index = camera_settings.get("index", 0)
    capture = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
    if not capture.isOpened():
        logger.warning("CAP_DSHOW backend failed for camera %d, retrying with default backend", cam_index)
        capture = cv2.VideoCapture(cam_index)
    if not capture.isOpened():
        raise RuntimeError("Cannot open webcam. Check camera permissions and try again.")
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, camera_settings.get("width", 960))
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_settings.get("height", 540))
    capture.set(cv2.CAP_PROP_FPS, camera_settings.get("fps", 60))
    capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    controllers = {
        "mouse": mouse_controller,
        "keyboard": keyboard_controller,
        "system": system_controller,
    }
    router = assistant.command_router
    voice_runtime = {"speech": None}

    active = True
    mode = "mouse"
    freeze_cursor = False
    last_action = "Waiting..."
    info_text = "AI mouse ready"
    session_started = time.time()
    executed_actions = 0
    rejected_actions = 0
    lost_tracking_frames = 0

    try:
        while True:
            performance_monitor.record_frame()
            frame_started = time.perf_counter()

            success, frame = capture.read()
            if not success:
                logger.error("Failed to read frame from camera — ending capture loop")
                break

            if camera_settings.get("flip_horizontal", True):
                frame = cv2.flip(frame, 1)

            hands = detector.process(frame)
            gesture_prediction = classifier.predict(hands)
            gesture_name = gesture_prediction.get("gesture")
            gesture_action = None
            pointer_tracking = False
            distance_text = ""
            distance_measure = {
                "distance_cm": None,
                "quality": 0.0,
                "in_active_zone": False,
                "message": "No hand",
            }

            runtime_context = assistant.context_manager.update(
                {
                    "mode": mode,
                    "active": active,
                    "smart_home_active": system_controller.smart_home.home_mode_active,
                }
            )

            if hands:
                lost_tracking_frames = 0
                distance_measure = distance_estimator.measure(
                    hands[0]["normalized"],
                    min_distance_cm=min_distance_cm,
                    max_distance_cm=max_distance_cm,
                    ideal_distance_cm=ideal_distance_cm,
                )
                distance_cm = distance_measure["distance_cm"]
                runtime_context.update(
                    {
                        "distance_cm": distance_cm,
                        "tracking_quality": distance_measure["quality"],
                        "active_zone": distance_measure["in_active_zone"],
                    }
                )
                if distance_cm is not None:
                    distance_text = f"Distance: {distance_cm:.0f} cm | Quality: {distance_measure['quality']:.2f} | {distance_measure['message']}"

                if distance_measure["in_active_zone"]:
                    gesture_action = mapper.get_action(gesture_name, runtime_context)
                    if (
                        gesture_prediction.get("is_pointer")
                        and active
                        and mode == "mouse"
                        and not freeze_cursor
                    ):
                        mouse_controller.move_cursor(hands[0]["normalized"][8])
                        pointer_tracking = True
                        info_text = "Cursor tracking"
                        last_action = "Move Cursor"
                else:
                    info_text = distance_measure["message"]
            else:
                lost_tracking_frames += 1
                if lost_tracking_frames == 3:
                    mouse_controller.reset_tracking()

            decision = assistant.decide(
                DEFAULT_USER_ID,
                gesture_prediction=gesture_prediction,
                gesture_action=gesture_action,
                context=runtime_context,
            )

            if decision.should_execute:
                if decision.intent == "move_cursor" and pointer_tracking:
                    last_action = humanize(decision.intent)
                else:
                    active, mode, freeze_cursor, info_text, last_action = execute_decision(
                        decision, hands, controllers, router,
                        active, mode, freeze_cursor, metrics,
                    )
                    executed_actions += 1
            elif decision.status == "awaiting_confirmation":
                info_text = f"Confirm {humanize(decision.intent)}"
                last_action = humanize(decision.intent)
            elif decision.status == "blocked":
                info_text = "Blocked by security policy"

            if mouse_controller.is_dragging and gesture_name != "pinch_and_hold":
                mouse_controller.stop_drag()

            frame_latency_ms = (time.perf_counter() - frame_started) * 1000.0
            performance_monitor.record_inference(frame_latency_ms)
            performance_snapshot = performance_monitor.snapshot()
            current_context = decision.context or assistant.context_manager.current()

            hand_cursor = draw_hand_pointer(frame, hands, pointer_tracking)
            visual_cursor = hand_cursor if pointer_tracking else mouse_controller.frame_cursor_position(frame.shape[1], frame.shape[0])
            frame = draw_information(
                frame,
                gesture_name,
                active,
                mode,
                current_context.get("application_category", "unknown"),
                info_text or last_action,
                distance_text,
                performance_snapshot,
                assistant.pending_voice,
            )
            frame = draw_virtual_cursor(frame, visual_cursor, tracking=pointer_tracking)

            cv2.imshow("GestureOS AI Mouse", frame)

            key = cv2.waitKey(1) & 0xFF
            if key in {ord("q"), 27}:
                break
            if key == ord("v"):
                voice_text, voice_message = capture_voice_command(voice_runtime)
                info_text = voice_message
                if voice_text:
                    voice_decision = assistant.update_voice_command(
                        DEFAULT_USER_ID,
                        voice_text,
                        context={"mode": mode, "active": active},
                    )
                    if voice_decision.should_execute:
                        active, mode, freeze_cursor, info_text, last_action = execute_decision(
                            voice_decision, hands, controllers, router,
                            active, mode, freeze_cursor, metrics,
                        )
                        executed_actions += 1
            if key == ord("u") and assistant.last_decision:
                if assistant.handle_feedback(False, user_id=DEFAULT_USER_ID):
                    rejected_actions += 1
                    false_positive_tracker.record(assistant.last_decision.intent, assistant.last_decision.context)
                    info_text = f"Rejected {humanize(assistant.last_decision.intent)}"

    except KeyboardInterrupt:
        logger.info("Gesture tracking stopped by user.")
    except Exception as exc:
        logger.critical("Unexpected error in main loop: %s", exc, exc_info=True)
    finally:
        capture.release()
        cv2.destroyAllWindows()

        session_duration = max(1, int(time.time() - session_started))
        accuracy = 1.0 if executed_actions == 0 else max(0.0, (executed_actions - rejected_actions) / executed_actions)
        metrics.record_session(session_duration, round(accuracy, 3))
        try:
            metrics.save()
        except Exception as exc:
            logger.error("Failed to save session metrics: %s", exc)


if __name__ == "__main__":
    main()
