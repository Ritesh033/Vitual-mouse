"""Application launcher for GestureOS."""

from __future__ import annotations

import logging
import subprocess
import webbrowser

logger = logging.getLogger(__name__)


class AppLauncher:
    COMMANDS = {
        "vscode": ["code"],
        "notepad": ["notepad"],
        "calculator": ["calc"],
    }

    def launch(self, app_name):
        if not app_name:
            return False

        normalized = app_name.strip().lower()
        if normalized == "chrome":
            webbrowser.open("https://www.google.com")
            return True

        command = self.COMMANDS.get(normalized)
        if not command:
            return False

        try:
            subprocess.Popen(command)
            return True
        except FileNotFoundError:
            logger.warning("Executable not found for '%s': %s", normalized, command)
            return False
        except Exception as exc:
            logger.error("Failed to launch '%s': %s", normalized, exc)
            return False
