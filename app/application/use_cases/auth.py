from __future__ import annotations

from app.application.dto.requests import LoginRequest
from app.application.unit_of_work import UnitOfWork
from app.domain.entities.user import User
from app.domain.exceptions import AuthenticationError


class LoginUseCase:
    def __init__(self, uow_factory, password_hasher) -> None:
        self._uow_factory = uow_factory
        self._password_hasher = password_hasher

    def execute(self, request: LoginRequest) -> User:
        with self._uow_factory() as uow:
            user = uow.user_repository.get_by_username(request.username)
            if user is None or not self._password_hasher.verify(request.password, user.password_hash):
                raise AuthenticationError("Invalid username or password.")
            return user


class LogoutUseCase:
    def execute(self) -> None:
        return None
