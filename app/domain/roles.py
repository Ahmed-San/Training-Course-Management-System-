from __future__ import annotations

from types import MappingProxyType
from typing import FrozenSet

from app.domain.enums import Permission, Role, TrainingMethod


ROLE_PERMISSIONS: dict[Role, FrozenSet[Permission]] = {
    Role.COURSE_MANAGER: frozenset(Permission),
    Role.TRAINER: frozenset(
        {
            Permission.VIEW_COURSE,
            Permission.VIEW_TRAINEE,
            Permission.VIEW_REPORT,
            Permission.VIEW_EVALUATION,
        }
    ),
    Role.TRAINEE: frozenset(
        {
            Permission.VIEW_COURSE,
            Permission.VIEW_REPORT,
        }
    ),
}
ROLE_PERMISSIONS = MappingProxyType(ROLE_PERMISSIONS)


def permissions_for_role(role: Role) -> FrozenSet[Permission]:
    return ROLE_PERMISSIONS[role]


def has_role_permission(role: Role, permission: Permission) -> bool:
    return permission in permissions_for_role(role)


def trainer_method_allows_management(training_method: TrainingMethod) -> bool:
    return training_method is TrainingMethod.ONSITE
