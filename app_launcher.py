"""Application launcher for GestureOS."""

from __future__ import annotations

import subprocess
import webbrowser


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
        except Exception:
            return False
