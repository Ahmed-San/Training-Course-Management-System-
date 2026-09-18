from __future__ import annotations

from abc import abstractmethod

from app.domain.entities.user import User
from app.domain.repositories.base_repository import Repository


class UserRepository(Repository[User]):
    @abstractmethod
    def get_by_username(self, username: str) -> User | None:
        raise NotImplementedError

