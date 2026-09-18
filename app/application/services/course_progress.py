from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from app.domain.enums import CourseStatus
from app.domain.exceptions import ValidationError


@dataclass(frozen=True, slots=True)
class CourseProgress:
    completed_hours: int
    remaining_hours: int
    status: CourseStatus


def calculate_course_progress(
    *,
    total_hours: int,
    reported_hours: Iterable[int],
) -> CourseProgress:
    """Calculate course progress from daily reports."""

    if not isinstance(total_hours, int) or isinstance(total_hours, bool):
        raise ValidationError("total_hours must be an integer.")

    if total_hours <= 0:
        raise ValidationError("total_hours must be greater than zero.")

    completed = 0

    for hours in reported_hours:
        if not isinstance(hours, int) or isinstance(hours, bool):
            raise ValidationError("Reported hours must be integers.")

        if hours <= 0:
            raise ValidationError("Reported hours must be greater than zero.")

        completed += hours

    remaining = max(total_hours - completed, 0)

    if completed == 0:
        status = CourseStatus.NOT_STARTED
    elif completed < total_hours:
        status = CourseStatus.IN_PROGRESS
    else:
        status = CourseStatus.COMPLETED

    return CourseProgress(
        completed_hours=completed,
        remaining_hours=remaining,
        status=status,
    )
