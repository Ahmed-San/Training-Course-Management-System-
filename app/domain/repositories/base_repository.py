from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from app.domain.entities.base_entity import BaseEntity

TEntity = TypeVar("TEntity", bound=BaseEntity)


class Repository(ABC, Generic[TEntity]):
    """Generic persistence contract shared by all entity repositories."""

    @abstractmethod
    def add(self, entity: TEntity) -> TEntity:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, entity_id: str) -> TEntity | None:
        raise NotImplementedError

    @abstractmethod
    def get_all(self) -> list[TEntity]:
        raise NotImplementedError

    @abstractmethod
    def update(self, entity: TEntity) -> TEntity:
        raise NotImplementedError

    @abstractmethod
    def delete(self, entity_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def exists(self, entity_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def count(self) -> int:
        raise NotImplementedError


# Alias for backward compatibility
BaseRepository = Repository
