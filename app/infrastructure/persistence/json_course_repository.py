from __future__ import annotations

from typing import Any

from app.domain.entities.course import Course
from app.domain.repositories.course_repository import CourseRepository
from app.infrastructure.persistence.json_repository import JsonRepository
from app.infrastructure.persistence.serializer import entity_from_dict


class JsonCourseRepository(JsonRepository[Course], CourseRepository):
    """Concrete repository adapter for Course entities backed by JSON persistence."""

    def __init__(
        self,
        *,
        state: dict[str, list[dict[str, Any]]],
        collection_name: str = "courses",
    ) -> None:
        super().__init__(
            state=state,
            collection_name=collection_name,
            entity_type=Course,
        )

    def get_by_manager(self, manager_id: str) -> list[Course]:
        """Retrieve all courses managed by a specific manager (query/filter only)."""
        return [
            entity_from_dict(record, Course)
            for record in self._collection
            if record.get("manager_id") == manager_id
        ]
