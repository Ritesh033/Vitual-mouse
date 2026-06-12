"""Tests for app_launcher.py."""

from unittest.mock import MagicMock, patch

from app_launcher import AppLauncher


class TestAppLauncher:
    def setup_method(self):
        self.launcher = AppLauncher()

    # --- launch() ---

    def test_launch_empty_name_returns_false(self):
        assert self.launcher.launch("") is False
        assert self.launcher.launch(None) is False

    def test_launch_chrome_opens_browser(self):
        with patch("app_launcher.webbrowser.open") as mock_open:
            result = self.launcher.launch("chrome")
            mock_open.assert_called_once_with("https://www.google.com")
            assert result is True

    def test_launch_chrome_case_insensitive(self):
        with patch("app_launcher.webbrowser.open") as mock_open:
            assert self.launcher.launch("  Chrome  ") is True
            mock_open.assert_called_once()

    def test_launch_known_app(self):
        with patch("app_launcher.subprocess.Popen") as mock_popen:
            assert self.launcher.launch("vscode") is True
            mock_popen.assert_called_once_with(["code"])

    def test_launch_notepad(self):
        with patch("app_launcher.subprocess.Popen") as mock_popen:
            assert self.launcher.launch("notepad") is True
            mock_popen.assert_called_once_with(["notepad"])

    def test_launch_calculator(self):
        with patch("app_launcher.subprocess.Popen") as mock_popen:
            assert self.launcher.launch("calculator") is True
            mock_popen.assert_called_once_with(["calc"])

    def test_launch_unknown_app_returns_false(self):
        assert self.launcher.launch("photoshop") is False

    def test_launch_popen_exception(self):
        with patch("app_launcher.subprocess.Popen", side_effect=OSError("not found")):
            assert self.launcher.launch("vscode") is False

    def test_commands_dict_structure(self):
        assert isinstance(AppLauncher.COMMANDS, dict)
        for key, val in AppLauncher.COMMANDS.items():
            assert isinstance(key, str)
            assert isinstance(val, list)
