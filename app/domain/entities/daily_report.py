from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from app.domain.entities.base_entity import BaseEntity
from app.domain.exceptions import ValidationError


@dataclass(slots=True)
class DailyReport(BaseEntity):
    """Represents one trainer daily report for a course."""

    course_id: str
    trainer_id: str
    report_date: date
    hours_done: int
    note: str
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        super().__post_init__()

        if not isinstance(self.course_id, str) or not self.course_id.strip():
            raise ValidationError("course_id must be a non-empty string.")

        if not isinstance(self.trainer_id, str) or not self.trainer_id.strip():
            raise ValidationError("trainer_id must be a non-empty string.")

        if not isinstance(self.report_date, date):
            raise ValidationError("report_date must be a date.")

        if isinstance(self.report_date, datetime):
            raise ValidationError("report_date must be a date, not datetime.")

        if not isinstance(self.hours_done, int) or isinstance(self.hours_done, bool):
            raise ValidationError("hours_done must be an integer.")

        if self.hours_done <= 0:
            raise ValidationError("hours_done must be greater than zero.")

        if not isinstance(self.note, str):
            raise ValidationError("note must be a string.")

        if not isinstance(self.created_at, datetime):
            raise ValidationError("created_at must be a datetime.")

        if not isinstance(self.updated_at, datetime):
            raise ValidationError("updated_at must be a datetime.")

        self.course_id = self.course_id.strip()
        self.trainer_id = self.trainer_id.strip()
        self.note = self.note.strip()