from __future__ import annotations

from abc import ABC, abstractmethod


class UnitOfWork(ABC):
    """Application contract for atomic multi-repository operations."""

    @abstractmethod
    def __enter__(self) -> "UnitOfWork":
        raise NotImplementedError

    @abstractmethod
    def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def rollback(self) -> None:
        raise NotImplementedError

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        if exc_type is not None:
            self.rollback()
            return False
        self.commit()
        return False
