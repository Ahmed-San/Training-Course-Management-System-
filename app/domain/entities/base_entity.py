from __future__ import annotations

from dataclasses import dataclass

from app.domain.exceptions import ValidationError


@dataclass(slots=True)
class BaseEntity:
    """Base class shared by every domain entity.

    The entity owns only identity. Persistence and business workflows stay
    outside the entity.
    """

    id: str

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValidationError("Entity id must be a non-empty string.")
        self.id = self.id.strip()
