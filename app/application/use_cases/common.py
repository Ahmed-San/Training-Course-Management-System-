from __future__ import annotations

from app.application.services.authorization import AuthorizationService
from app.domain.entities.user import User
from app.domain.enums import Permission, Role
from app.domain.exceptions import AuthenticationError, AuthorizationError


def require_authenticated(user: User | None) -> User:
    if user is None:
        raise AuthenticationError("Authentication is required.")
    return user


def require_manager(user: User) -> None:
    AuthorizationService.require_role(user.role, Role.COURSE_MANAGER)


def require_permission(user: User, permission: Permission) -> None:
    AuthorizationService.require_permission(user.role, permission)


def trainer_id(user: User) -> str:
    if user.role is not Role.TRAINER or not user.profile_id:
        raise AuthorizationError("The current user is not a trainer profile.")
    return user.profile_id


def trainee_id(user: User) -> str:
    if user.role is not Role.TRAINEE or not user.profile_id:
        raise AuthorizationError("The current user is not a trainee profile.")
    return user.profile_id
