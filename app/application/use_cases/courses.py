from __future__ import annotations

from dataclasses import dataclass

from app.domain.entities.course import Course
from app.domain.repositories.course_repository import CourseRepository


@dataclass(frozen=True, slots=True)
class CreateCourseRequest:
    id: str
    name: str
    total_hours: int
    description: str
    order_index: int
    manager_id: str


# Backward-compatibility alias
CreateCourseDTO = CreateCourseRequest


@dataclass(frozen=True, slots=True)
class UpdateCourseRequest:
    id: str
    name: str | None = None
    total_hours: int | None = None
    description: str | None = None
    order_index: int | None = None
    manager_id: str | None = None


# Backward-compatibility alias
UpdateCourseDTO = UpdateCourseRequest


class CreateCourseUseCase:
    """Use case to validate and create a new Course entity."""

    def __init__(self, course_repo: CourseRepository) -> None:
        self._course_repo = course_repo

    def execute(self, request: CreateCourseRequest) -> Course:
        course = Course(
            id=request.id,
            name=request.name,
            total_hours=request.total_hours,
            description=request.description,
            order_index=request.order_index,
            manager_id=request.manager_id,
        )
        return self._course_repo.add(course)


class UpdateCourseUseCase:
    """Use case to update an existing Course entity."""

    def __init__(self, course_repo: CourseRepository) -> None:
        self._course_repo = course_repo

    def execute(self, request: UpdateCourseRequest) -> Course:
        existing = self._course_repo.get_required(request.id)
        updated = Course(
            id=existing.id,
            name=request.name if request.name is not None else existing.name,
            total_hours=request.total_hours if request.total_hours is not None else existing.total_hours,
            description=request.description if request.description is not None else existing.description,
            order_index=request.order_index if request.order_index is not None else existing.order_index,
            manager_id=request.manager_id if request.manager_id is not None else existing.manager_id,
        )
        return self._course_repo.update(updated)


class ViewCourseUseCase:
    """Use case to view a single Course entity by ID."""

    def __init__(self, course_repo: CourseRepository) -> None:
        self._course_repo = course_repo

    def execute(self, course_id: str) -> Course:
        return self._course_repo.get_required(course_id)


class ListCoursesUseCase:
    """Use case to list all Course entities or filter by manager."""

    def __init__(self, course_repo: CourseRepository) -> None:
        self._course_repo = course_repo

    def execute(self, manager_id: str | None = None) -> list[Course]:
        if manager_id:
            return self._course_repo.get_by_manager(manager_id)
        return self._course_repo.get_all()
