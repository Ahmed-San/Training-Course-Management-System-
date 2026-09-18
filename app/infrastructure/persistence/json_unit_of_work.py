from __future__ import annotations

from copy import deepcopy

from app.application.unit_of_work import UnitOfWork
from app.infrastructure.persistence.json_database import JsonDatabase


class JsonUnitOfWork(UnitOfWork):
    """Atomic working copy of the single JSON database document."""

    def __init__(self, database: JsonDatabase) -> None:
        self.database = database
        self.state: dict[str, list[dict]] = {}
        self._original_state: dict[str, list[dict]] = {}
        self._active = False

    def __enter__(self) -> "JsonUnitOfWork":
        self._original_state = self.database.snapshot()
        self.state = deepcopy(self._original_state)
        self._active = True
        return self

    def commit(self) -> None:
        if not self._active:
            return
        self.database.save(self.state)
        self._active = False

    def rollback(self) -> None:
        self.state = deepcopy(self._original_state)
        self._active = False

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        if exc_type is not None:
            self.rollback()
            return False
        self.commit()
        return False
