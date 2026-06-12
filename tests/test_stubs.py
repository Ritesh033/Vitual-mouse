"""Tests for stub modules: brightness, volume, screenshot, lock_screen, shutdown."""

from brightness import BrightnessControl
from lock_screen import LockScreen
from screenshot import Screenshot
from shutdown import Shutdown
from volume import VolumeControl


class TestBrightnessControl:
    def test_instantiates(self):
        bc = BrightnessControl()
        assert bc is not None

    def test_increase_returns_none(self):
        assert BrightnessControl().increase() is None

    def test_decrease_returns_none(self):
        assert BrightnessControl().decrease() is None


class TestVolumeControl:
    def test_instantiates(self):
        vc = VolumeControl()
        assert vc is not None

    def test_increase_returns_none(self):
        assert VolumeControl().increase() is None

    def test_decrease_returns_none(self):
        assert VolumeControl().decrease() is None


class TestScreenshot:
    def test_instantiates(self):
        s = Screenshot()
        assert s is not None

    def test_capture_returns_none(self):
        assert Screenshot().capture() is None


class TestLockScreen:
    def test_instantiates(self):
        ls = LockScreen()
        assert ls is not None

    def test_lock_returns_none(self):
        assert LockScreen().lock() is None


class TestShutdown:
    def test_instantiates(self):
        sd = Shutdown()
        assert sd is not None

    def test_shutdown_returns_none(self):
        assert Shutdown().shutdown() is None

    def test_restart_returns_none(self):
        assert Shutdown().restart() is None
