from __future__ import annotations

from abc import abstractmethod

from app.domain.entities.enrollment import Enrollment
from app.domain.repositories.base_repository import Repository


class EnrollmentRepository(Repository[Enrollment]):
    @abstractmethod
    def get_active_by_trainee(self, trainee_id: str) -> Enrollment | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_course(self, course_id: str) -> list[Enrollment]:
        raise NotImplementedError

    @abstractmethod
    def get_by_trainee(self, trainee_id: str) -> list[Enrollment]:
        raise NotImplementedError
