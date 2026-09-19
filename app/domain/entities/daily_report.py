from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from app.domain.entities.base_entity import BaseEntity
from app.domain.exceptions import ValidationError
from app.domain.validation import validate_non_empty, validate_positive_int


@dataclass(slots=True)
class DailyReport(BaseEntity):
    """Daily training report; course progress is derived from reports."""

    course_id: str
    trainer_id: str
    report_date: date
    hours_done: int
    note: str
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        BaseEntity.__post_init__(self)
        self.course_id = validate_non_empty(self.course_id, "course_id")
        self.trainer_id = validate_non_empty(self.trainer_id, "trainer_id")

        if isinstance(self.report_date, datetime) or not isinstance(self.report_date, date):
            raise ValidationError("report_date must be a date, not datetime.")

        self.hours_done = validate_positive_int(self.hours_done, "hours_done")

        if not isinstance(self.note, str):
            raise ValidationError("note must be a string.")
        self.note = self.note.strip()

        if not isinstance(self.created_at, datetime) or not isinstance(self.updated_at, datetime):
            raise ValidationError("Report timestamps must be datetime values.")
        try:
            if self.updated_at < self.created_at:
                raise ValidationError("updated_at cannot be earlier than created_at.")
        except TypeError as exc:
            raise ValidationError(
                "Report timestamps must use comparable timezone information."
            ) from exc

    def update(
        self,
        *,
        hours_done: int | None = None,
        note: str | None = None,
        report_date: date | None = None,
    ) -> None:
        """Update local report fields after application-level authorization."""
        if hours_done is not None:
            self.hours_done = validate_positive_int(hours_done, "hours_done")

        if note is not None:
            if not isinstance(note, str):
                raise ValidationError("note must be a string.")
            self.note = note.strip()

        if report_date is not None:
            if isinstance(report_date, datetime) or not isinstance(report_date, date):
                raise ValidationError("report_date must be a date, not datetime.")
            self.report_date = report_date

        now = datetime.now(self.updated_at.tzinfo) if self.updated_at.tzinfo else datetime.now()
        if now < self.created_at:
            now = self.created_at
        self.updated_at = now
