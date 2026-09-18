from __future__ import annotations

import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Any

from app.domain.exceptions import StorageError

DEFAULT_COLLECTIONS = (
    "users",
    "trainees",
    "trainers",
    "courses",
    "enrollments",
    "evaluations",
    "daily_reports",
    "course_trainer_assignments",
    "trainer_trainee_assignments",
)


class JsonDatabase:
    """Low-level JSON document store. It knows storage, not domain rules."""

    def __init__(self, path: Path, collections: tuple[str, ...] = DEFAULT_COLLECTIONS) -> None:
        self.path = Path(path)
        self.collections = collections

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.save(self.empty_state())

    def empty_state(self) -> dict[str, list[dict[str, Any]]]:
        return {name: [] for name in self.collections}

    def load(self) -> dict[str, list[dict[str, Any]]]:
        self.initialize()
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise StorageError(f"Unable to load database: {self.path}") from exc

        if not isinstance(raw, dict):
            raise StorageError("Database root must be a JSON object.")

        state: dict[str, list[dict[str, Any]]] = {}
        for name, value in raw.items():
            if not isinstance(name, str) or not isinstance(value, list):
                raise StorageError("Every database collection must be a JSON array.")
            if not all(isinstance(record, dict) for record in value):
                raise StorageError(f"Collection '{name}' must contain JSON objects.")
            state[name] = value

        for name in self.collections:
            state.setdefault(name, [])
        return state

    def save(self, state: dict[str, list[dict[str, Any]]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        normalized = self._normalize_state(state)
        temp_path = self.path.with_suffix(self.path.suffix + ".tmp")
        try:
            payload = json.dumps(normalized, indent=2, ensure_ascii=False) + "\n"
            with temp_path.open("w", encoding="utf-8", newline="\n") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            temp_path.replace(self.path)
        except OSError as exc:
            raise StorageError(f"Unable to save database: {self.path}") from exc
        finally:
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except OSError:
                    pass

    def snapshot(self) -> dict[str, list[dict[str, Any]]]:
        return deepcopy(self.load())

    def _normalize_state(
        self, state: dict[str, list[dict[str, Any]]]
    ) -> dict[str, list[dict[str, Any]]]:
        normalized: dict[str, list[dict[str, Any]]] = {}
        for name, value in state.items():
            if not isinstance(name, str) or not isinstance(value, list):
                raise StorageError("Every database collection must be a list.")
            if not all(isinstance(record, dict) for record in value):
                raise StorageError(f"Collection '{name}' must contain dictionaries.")
            normalized[name] = value

        for name in self.collections:
            normalized.setdefault(name, [])
        return normalized
