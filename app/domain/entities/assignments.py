from __future__ import annotations

from dataclasses import dataclass

from app.domain.entities.base_entity import BaseEntity
from app.domain.validation import validate_non_empty


@dataclass(slots=True)
class CourseTrainerAssignment(BaseEntity):
    """Associate a trainer with a course."""

    course_id: str
    trainer_id: str

    def __post_init__(self) -> None:
        BaseEntity.__post_init__(self)
        self.course_id = validate_non_empty(self.course_id, "course_id")
        self.trainer_id = validate_non_empty(self.trainer_id, "trainer_id")


@dataclass(slots=True)
class TrainerTraineeAssignment(BaseEntity):
    """Associate a trainer with a trainee inside a specific course."""

    course_id: str
    trainer_id: str
    trainee_id: str

    def __post_init__(self) -> None:
        BaseEntity.__post_init__(self)
        self.course_id = validate_non_empty(self.course_id, "course_id")
        self.trainer_id = validate_non_empty(self.trainer_id, "trainer_id")
        self.trainee_id = validate_non_empty(self.trainee_id, "trainee_id")