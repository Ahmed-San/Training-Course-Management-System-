from __future__ import annotations

from abc import abstractmethod

from app.domain.entities.course import Course
from app.domain.repositories.base_repository import Repository


class CourseRepository(Repository[Course]):
    """Specialized repository interface for Course entities."""

    @abstractmethod
    def get_by_manager(self, manager_id: str) -> list[Course]:
        """Retrieve all courses managed by a specific manager."""
        raise NotImplementedError
