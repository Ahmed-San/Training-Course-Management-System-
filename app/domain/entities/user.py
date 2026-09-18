from __future__ import annotations

from dataclasses import dataclass

from app.domain.entities.base_entity import BaseEntity
from app.domain.enums import Role
from app.domain.validation import validate_enum, validate_non_empty


@dataclass(slots=True)
class User(BaseEntity):
    username: str
    password_hash: str
    role: Role
    profile_id: str | None = None

    def __post_init__(self) -> None:
        BaseEntity.__post_init__(self)
        self.username = validate_non_empty(self.username, "username")
        self.password_hash = validate_non_empty(self.password_hash, "password_hash")
        self.role = validate_enum(self.role, Role, "role")
        if self.profile_id is not None:
            self.profile_id = validate_non_empty(self.profile_id, "profile_id")

