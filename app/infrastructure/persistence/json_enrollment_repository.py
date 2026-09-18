from __future__ import annotations

from typing import Any

from app.domain.entities.enrollment import Enrollment
from app.domain.enums import EnrollmentStatus
from app.domain.repositories.enrollment_repository import EnrollmentRepository
from app.infrastructure.persistence.json_repository import JsonRepository


class JsonEnrollmentRepository(JsonRepository[Enrollment], EnrollmentRepository):
    """JSON adapter for enrollment storage and enrollment-specific queries."""

    def get_active_by_trainee(self, trainee_id: str) -> Enrollment | None:
        return next(
            (
                item
                for item in self.get_all()
                if item.trainee_id == trainee_id
                and item.status is EnrollmentStatus.ACTIVE
            ),
            None,
        )

    def get_by_course(self, course_id: str) -> list[Enrollment]:
        return [item for item in self.get_all() if item.course_id == course_id]

    def get_by_trainee(self, trainee_id: str) -> list[Enrollment]:
        return [item for item in self.get_all() if item.trainee_id == trainee_id]
