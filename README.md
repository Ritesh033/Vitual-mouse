# GestureOS

GestureOS is a gesture-based human-computer interaction platform for controlling mouse, keyboard, system, voice, and advanced accessibility workflows using camera-based hand gestures.

## Project Structure

- `main.py` - entrypoint for the gesture control system
- `config/` - gesture definitions and runtime configuration
- `vision/` - hand detection, face detection, and tracking modules
- `gesture_engine/` - gesture classification and action mapping
- `mouse_control/`, `keyboard_control/`, `system_control/` - core input controllers
- `voice_control/` - voice command and assistant support
- `air_writing/` - air-writing character recognition
- `sign_language/` - sign language recognition
- `gaming_mode/` - low-latency gesture gaming UI
- `analytics/` - usage metrics and dashboards
- `dashboard/` - web interface for visualization and settings
- `cloud/` - sync, backup, and cloud integration
- `ai_assistant/` - assistant routing and workflow management

## Setup

```bash
pip install -r requirements.txt
python main.py
```

## Development Phases

See `docs/development_phases.md` for the recommended phase plan.
