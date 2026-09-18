from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from app.domain.enums import CourseStatus


@dataclass(frozen=True, slots=True)
class CourseProgress:
    completed_hours: int
    remaining_hours: int
    status: CourseStatus


def calculate_course_progress(
    *, total_hours: int, reported_hours: Iterable[int]
) -> CourseProgress:
    """Calculate course progress from reports without mutating any entity."""
    completed = sum(reported_hours)
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
