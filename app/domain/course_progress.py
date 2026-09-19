from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from app.domain.enums import CourseStatus
from app.domain.validation import validate_non_negative_int, validate_positive_int


@dataclass(frozen=True, slots=True)
class CourseProgress:
    completed_hours: int
    remaining_hours: int
    status: CourseStatus


def _reported_hours_value(item: object) -> int:
    value = getattr(item, "hours_done", item)
    return validate_non_negative_int(value, "reported_hours item")


def calculate_course_progress(
    *,
    total_hours: int,
    reported_hours: Iterable[object],
) -> CourseProgress:
    """Derive course progress from course total hours and current reports."""
    total_hours = validate_positive_int(total_hours, "total_hours")
    completed_hours = sum(_reported_hours_value(item) for item in reported_hours)
    remaining_hours = max(total_hours - completed_hours, 0)

    if completed_hours == 0:
        status = CourseStatus.NOT_STARTED
    elif completed_hours < total_hours:
        status = CourseStatus.IN_PROGRESS
    else:
        status = CourseStatus.COMPLETED

    return CourseProgress(
        completed_hours=completed_hours,
        remaining_hours=remaining_hours,
        status=status,
    )
