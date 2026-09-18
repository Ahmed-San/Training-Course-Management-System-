from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.domain.entities.base_entity import BaseEntity
from app.domain.enums import Grade
from app.domain.exceptions import ValidationError
from app.domain.validation import validate_enum, validate_non_empty


@dataclass(slots=True)
class Evaluation(BaseEntity):
    """Final evaluation associated with one enrollment."""

    enrollment_id: str
    trainer_id: str
    grade: Grade
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        BaseEntity.__post_init__(self)
        self.enrollment_id = validate_non_empty(self.enrollment_id, "enrollment_id")
        self.trainer_id = validate_non_empty(self.trainer_id, "trainer_id")
        self.grade = validate_enum(self.grade, Grade, "grade")

        if not isinstance(self.created_at, datetime) or not isinstance(self.updated_at, datetime):
            raise ValidationError("Evaluation timestamps must be datetime values.")
        try:
            if self.updated_at < self.created_at:
                raise ValidationError("updated_at cannot be earlier than created_at.")
        except TypeError as exc:
            raise ValidationError(
                "Evaluation timestamps must use comparable timezone information."
            ) from exc

    def change_grade(self, new_grade: Grade) -> None:
        """Change the grade only; workflow timestamps are managed by Application."""
        self.grade = validate_enum(new_grade, Grade, "grade")
