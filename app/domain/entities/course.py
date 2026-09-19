from __future__ import annotations

from dataclasses import dataclass

from app.domain.entities.base_entity import BaseEntity
from app.domain.enums import CourseStatus
from app.domain.exceptions import ValidationError
from app.domain.validation import validate_non_empty, validate_positive_int


@dataclass(slots=True)
class Course(BaseEntity):
    """Course entity owned by Domain implementation.

    Fields:
    - id: str, non-empty (inherited from BaseEntity)
    - name: str, non-empty
    - total_hours: int, > 0
    - description: str, non-empty
    - order_index: int, >= 1
    - manager_id: str, non-empty
    """

    name: str
    total_hours: int
    description: str
    order_index: int
    manager_id: str

    def __post_init__(self) -> None:
        BaseEntity.__post_init__(self)
        self.name = validate_non_empty(self.name, "Course name")
        self.total_hours = validate_positive_int(self.total_hours, "Total hours")
        self.description = validate_non_empty(self.description, "Course description")
        if isinstance(self.order_index, bool) or not isinstance(self.order_index, int) or self.order_index < 1:
            raise ValidationError("Order index must be an integer greater than or equal to 1.")
        self.manager_id = validate_non_empty(self.manager_id, "Manager ID")

    def _validate_completed_hours(self, completed_hours: int) -> int:
        if isinstance(completed_hours, bool) or not isinstance(completed_hours, int) or completed_hours < 0:
            raise ValidationError("Completed hours must be a non-negative integer.")
        return completed_hours

    def calculate_remaining_hours(self, completed_hours: int) -> int:
        """Calculate remaining hours derived from total_hours and completed_hours."""
        valid_completed = self._validate_completed_hours(completed_hours)
        return max(self.total_hours - valid_completed, 0)

    def is_completed(self, completed_hours: int) -> bool:
        """Determine if course completion criteria is satisfied."""
        valid_completed = self._validate_completed_hours(completed_hours)
        return valid_completed >= self.total_hours

    def get_status(self, completed_hours: int) -> CourseStatus:
        """Determine derived course status based on completed_hours."""
        valid_completed = self._validate_completed_hours(completed_hours)
        if valid_completed == 0:
            return CourseStatus.NOT_STARTED
        elif valid_completed >= self.total_hours:
            return CourseStatus.COMPLETED
        else:
            return CourseStatus.IN_PROGRESS
