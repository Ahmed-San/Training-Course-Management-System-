from __future__ import annotations

from app.domain.enums import Permission, Role, TrainingMethod
from app.domain.exceptions import AuthorizationError
from app.domain.roles import has_role_permission, trainer_method_allows_management


class AuthorizationService:
    """Shared role-level authorization helpers.

    Resource-scope checks (assigned course/student, course state, etc.) belong
    to the feature-specific use cases and repositories that own those rules.
    """

    @staticmethod
    def require_role(user_role: Role, *allowed_roles: Role) -> None:
        if user_role not in allowed_roles:
            raise AuthorizationError("User role is not allowed to perform this action.")

    @staticmethod
    def require_permission(user_role: Role, permission: Permission) -> None:
        if not has_role_permission(user_role, permission):
            raise AuthorizationError("User role does not have this permission.")

    @staticmethod
    def require_onsite_trainer(
        *, user_role: Role, training_method: TrainingMethod
    ) -> None:
        if user_role is not Role.TRAINER or not trainer_method_allows_management(training_method):
            raise AuthorizationError("Only onsite trainers can perform this trainer operation.")
