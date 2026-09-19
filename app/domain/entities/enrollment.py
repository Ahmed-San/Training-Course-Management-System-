from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.domain.entities.base_entity import BaseEntity
from app.domain.enums import EnrollmentStatus
from app.domain.exceptions import BusinessRuleError, ValidationError
from app.domain.validation import validate_enum, validate_non_empty


@dataclass(slots=True)
class Enrollment(BaseEntity):
    """Connect one trainee to one course through an explicit lifecycle."""

    trainee_id: str
    course_id: str
    status: EnrollmentStatus
    completed_at: datetime | None = None

    def __post_init__(self) -> None:
        BaseEntity.__post_init__(self)
        self.trainee_id = validate_non_empty(self.trainee_id, "trainee_id")
        self.course_id = validate_non_empty(self.course_id, "course_id")
        self.status = validate_enum(self.status, EnrollmentStatus, "status")
        if self.completed_at is not None and not isinstance(self.completed_at, datetime):
            raise ValidationError("completed_at must be a datetime or None.")
        if self.status is EnrollmentStatus.ACTIVE and self.completed_at is not None:
            raise ValidationError("An active enrollment cannot have completed_at.")
        if self.status is EnrollmentStatus.COMPLETED and self.completed_at is None:
            raise ValidationError("A completed enrollment requires completed_at.")

    def complete(self, completed_at: datetime) -> None:
        """Move an active enrollment to completed exactly once."""
        if not isinstance(completed_at, datetime):
            raise ValidationError("completed_at must be a datetime.")
        if self.is_completed():
            raise BusinessRuleError("Enrollment is already completed.")
        self.status = EnrollmentStatus.COMPLETED
        self.completed_at = completed_at

    def is_active(self) -> bool:
        """Return whether the enrollment can still be completed."""
        return self.status is EnrollmentStatus.ACTIVE

    def is_completed(self) -> bool:
        """Return whether the enrollment has reached its terminal state."""
        return self.status is EnrollmentStatus.COMPLETED
