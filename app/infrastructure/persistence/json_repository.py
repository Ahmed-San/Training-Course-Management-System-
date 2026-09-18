from __future__ import annotations

from typing import Any, Generic, TypeVar

from app.domain.entities.base_entity import BaseEntity
from app.domain.exceptions import DuplicateError, NotFoundError
from app.domain.repositories.base_repository import Repository
from app.infrastructure.persistence.serializer import entity_from_dict, entity_to_dict

TEntity = TypeVar("TEntity", bound=BaseEntity)


class JsonRepository(Repository[TEntity], Generic[TEntity]):
    """Generic repository implementation backed by one JSON document.

    The repository mutates the Unit-of-Work state supplied to it. It never
    decides business rules and it never writes the file after each method.
    """

    def __init__(
        self,
        *,
        state: dict[str, list[dict[str, Any]]],
        collection_name: str,
        entity_type: type[TEntity],
    ) -> None:
        self._state = state
        self._collection_name = collection_name
        self._entity_type = entity_type

    @property
    def _collection(self) -> list[dict[str, Any]]:
        return self._state[self._collection_name]

    def add(self, entity: TEntity) -> TEntity:
        if self.exists(entity.id):
            raise DuplicateError(
                f"{self._entity_type.__name__} with id '{entity.id}' already exists."
            )
        self._collection.append(entity_to_dict(entity))
        return entity

    def get_by_id(self, entity_id: str) -> TEntity | None:
        record = next((item for item in self._collection if item.get("id") == entity_id), None)
        if record is None:
            return None
        return entity_from_dict(record, self._entity_type)

    def get_required(self, entity_id: str) -> TEntity:
        entity = self.get_by_id(entity_id)
        if entity is None:
            raise NotFoundError(
                f"{self._entity_type.__name__} with id '{entity_id}' was not found."
            )
        return entity

    def get_all(self) -> list[TEntity]:
        return [entity_from_dict(item, self._entity_type) for item in self._collection]

    def update(self, entity: TEntity) -> TEntity:
        for index, record in enumerate(self._collection):
            if record.get("id") == entity.id:
                self._collection[index] = entity_to_dict(entity)
                return entity
        raise NotFoundError(
            f"{self._entity_type.__name__} with id '{entity.id}' was not found."
        )

    def delete(self, entity_id: str) -> None:
        for index, record in enumerate(self._collection):
            if record.get("id") == entity_id:
                self._collection.pop(index)
                return
        raise NotFoundError(
            f"{self._entity_type.__name__} with id '{entity_id}' was not found."
        )

    def exists(self, entity_id: str) -> bool:
        return any(item.get("id") == entity_id for item in self._collection)

    def count(self) -> int:
        return len(self._collection)
