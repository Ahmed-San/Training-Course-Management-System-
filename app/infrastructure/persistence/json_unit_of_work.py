from __future__ import annotations

from copy import deepcopy

from app.application.unit_of_work import UnitOfWork
from app.domain.entities.course import Course
from app.domain.entities.trainee import Trainee
from app.domain.entities.trainer import Trainer
from app.infrastructure.persistence.json_database import JsonDatabase
from app.infrastructure.persistence.json_assignment_repository import (
    JsonAssignmentRepository,
)
from app.infrastructure.persistence.json_course_repository import JsonCourseRepository
from app.infrastructure.persistence.json_enrollment_repository import (
    JsonEnrollmentRepository,
)
from app.infrastructure.persistence.json_repository import JsonRepository


class JsonUnitOfWork(UnitOfWork):
    """Atomic working copy of the single JSON database document."""

    def __init__(self, database: JsonDatabase) -> None:
        self.database = database
        self.state: dict[str, list[dict]] = {}
        self._original_state: dict[str, list[dict]] = {}
        self._active = False
        self.course_repository = None
        self.trainee_repository = None
        self.trainer_repository = None
        self.enrollment_repository = None
        self.assignment_repository = None

    def __enter__(self) -> "JsonUnitOfWork":
        self._original_state = self.database.snapshot()
        self.state = deepcopy(self._original_state)
        self.course_repository = JsonCourseRepository(state=self.state)
        self.trainee_repository = JsonRepository(
            state=self.state,
            collection_name="trainees",
            entity_type=Trainee,
        )
        self.trainer_repository = JsonRepository(
            state=self.state,
            collection_name="trainers",
            entity_type=Trainer,
        )
        self.enrollment_repository = JsonEnrollmentRepository(
            state=self.state,
            collection_name="enrollments",
        )
        self.assignment_repository = JsonAssignmentRepository(state=self.state)
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
