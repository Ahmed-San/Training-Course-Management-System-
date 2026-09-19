from __future__ import annotations

from abc import abstractmethod

from app.domain.entities.enrollment import Enrollment
from app.domain.repositories.base_repository import Repository


class EnrollmentRepository(Repository[Enrollment]):
    """Persistence contract for enrollment lifecycle queries."""

    @abstractmethod
    def get_active_by_trainee(self, trainee_id: str) -> Enrollment | None:
        """Return the trainee's active enrollment, if one exists."""
        raise NotImplementedError

    @abstractmethod
    def get_by_course(self, course_id: str) -> list[Enrollment]:
        """Return all enrollments belonging to a course."""
        raise NotImplementedError

    @abstractmethod
    def get_by_trainee(self, trainee_id: str) -> list[Enrollment]:
        """Return all enrollments belonging to a trainee."""
        raise NotImplementedError
