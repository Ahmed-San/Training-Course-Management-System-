from __future__ import annotations

from typing import Any

from app.domain.entities.assignments import CourseTrainerAssignment, TrainerTraineeAssignment
from app.domain.exceptions import DuplicateError, NotFoundError, ValidationError
from app.domain.repositories.assignment_repository import AssignmentRepository
from app.infrastructure.persistence.serializer import entity_from_dict, entity_to_dict


class JsonAssignmentRepository(AssignmentRepository):
    """JSON adapter for both M3 assignment entities."""

    _COURSE_COLLECTION = "course_trainer_assignments"
    _TRAINEE_COLLECTION = "trainer_trainee_assignments"

    def __init__(self, *, state: dict[str, list[dict[str, Any]]]) -> None:
        self._state = state

    def _course_items(self) -> list[CourseTrainerAssignment]:
        return [
            entity_from_dict(item, CourseTrainerAssignment)
            for item in self._state[self._COURSE_COLLECTION]
        ]

    def _trainee_items(self) -> list[TrainerTraineeAssignment]:
        return [
            entity_from_dict(item, TrainerTraineeAssignment)
            for item in self._state[self._TRAINEE_COLLECTION]
        ]

    @staticmethod
    def _collection_for(entity: object) -> str:
        if isinstance(entity, CourseTrainerAssignment):
            return JsonAssignmentRepository._COURSE_COLLECTION
        if isinstance(entity, TrainerTraineeAssignment):
            return JsonAssignmentRepository._TRAINEE_COLLECTION
        raise ValidationError("Unsupported assignment entity type.")

    def add(self, entity):
        collection_name = self._collection_for(entity)
        collection = self._state[collection_name]
        if self.exists(entity.id):
            raise DuplicateError(f"Assignment with id '{entity.id}' already exists.")
        collection.append(entity_to_dict(entity))
        return entity

    def get_by_id(self, entity_id: str):
        for item in self._course_items():
            if item.id == entity_id:
                return item
        for item in self._trainee_items():
            if item.id == entity_id:
                return item
        return None

    def get_required(self, entity_id: str):
        item = self.get_by_id(entity_id)
        if item is None:
            raise NotFoundError(f"Assignment with id '{entity_id}' was not found.")
        return item

    def get_all(self) -> list:
        return [*self._course_items(), *self._trainee_items()]

    def update(self, entity):
        collection_name = self._collection_for(entity)
        collection = self._state[collection_name]
        for index, record in enumerate(collection):
            if record.get("id") == entity.id:
                collection[index] = entity_to_dict(entity)
                return entity
        raise NotFoundError(f"Assignment with id '{entity.id}' was not found.")

    def delete(self, entity_id: str) -> None:
        for collection_name in (self._COURSE_COLLECTION, self._TRAINEE_COLLECTION):
            collection = self._state[collection_name]
            for index, record in enumerate(collection):
                if record.get("id") == entity_id:
                    collection.pop(index)
                    return
        raise NotFoundError(f"Assignment with id '{entity_id}' was not found.")

    def exists(self, entity_id: str) -> bool:
        return self.get_by_id(entity_id) is not None

    def count(self) -> int:
        return len(self._state[self._COURSE_COLLECTION]) + len(
            self._state[self._TRAINEE_COLLECTION]
        )

    def is_trainer_assigned_to_course(self, trainer_id: str, course_id: str) -> bool:
        return any(
            item.trainer_id == trainer_id and item.course_id == course_id
            for item in self._course_items()
        )

    def is_trainer_assigned_to_trainee(
        self, trainer_id: str, trainee_id: str, course_id: str
    ) -> bool:
        return any(
            item.trainer_id == trainer_id
            and item.trainee_id == trainee_id
            and item.course_id == course_id
            for item in self._trainee_items()
        )

    def get_courses_by_trainer(self, trainer_id: str) -> list[CourseTrainerAssignment]:
        return [item for item in self._course_items() if item.trainer_id == trainer_id]

    def get_trainees_by_trainer(
        self, trainer_id: str, course_id: str
    ) -> list[TrainerTraineeAssignment]:
        return [
            item
            for item in self._trainee_items()
            if item.trainer_id == trainer_id and item.course_id == course_id
        ]
