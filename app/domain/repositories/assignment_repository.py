from __future__ import annotations

from abc import abstractmethod

from app.domain.entities.assignments import CourseTrainerAssignment, TrainerTraineeAssignment
from app.domain.repositories.base_repository import Repository


class AssignmentRepository(Repository[CourseTrainerAssignment | TrainerTraineeAssignment]):
    """Persistence contract for trainer assignment queries."""

    @abstractmethod
    def is_trainer_assigned_to_course(self, trainer_id: str, course_id: str) -> bool:
        """Check whether a trainer is assigned to a course."""
        raise NotImplementedError

    @abstractmethod
    def is_trainer_assigned_to_trainee(self, trainer_id: str, trainee_id: str, course_id: str) -> bool:
        """Check whether a trainer is assigned to a trainee in a course."""
        raise NotImplementedError

    @abstractmethod
    def get_courses_by_trainer(self, trainer_id: str) -> list[CourseTrainerAssignment]:
        """Return course assignments owned by a trainer."""
        raise NotImplementedError

    @abstractmethod
    def get_trainees_by_trainer(self, trainer_id: str, course_id: str) -> list[TrainerTraineeAssignment]:
        """Return trainee assignments for a trainer within a course."""
        raise NotImplementedError
