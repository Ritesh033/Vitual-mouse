"""User profile management for GestureOS personalization."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("gestureos.profiles")


class UserProfiles:
    """Store and retrieve per-user preference profiles."""

    def __init__(self, storage_path: str = "user_profiles.json") -> None:
        self._path = Path(storage_path)
        self._profiles: Dict[str, Dict[str, Any]] = self._load()

    def _load(self) -> Dict[str, Dict[str, Any]]:
        if self._path.exists():
            try:
                with open(self._path, "r", encoding="utf-8") as fh:
                    return json.load(fh)
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def _save(self) -> None:
        try:
            with open(self._path, "w", encoding="utf-8") as fh:
                json.dump(self._profiles, fh, indent=2)
        except OSError as exc:
            logger.error("Failed to save profiles: %s", exc)

    def ensure_user(self, user_id: str, defaults: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if user_id not in self._profiles:
            self._profiles[user_id] = defaults or {}
            self._save()
        return self._profiles[user_id]

    def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self._profiles.get(user_id)

    def update_profile(self, user_id: str, data: Dict[str, Any]) -> None:
        profile = self._profiles.setdefault(user_id, {})
        profile.update(data)
        self._save()

    def list_users(self):
        return list(self._profiles.keys())
