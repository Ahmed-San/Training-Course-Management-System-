from __future__ import annotations

from dataclasses import dataclass

from app.domain.entities.base_entity import BaseEntity
from app.domain.validation import validate_age, validate_email, validate_name, validate_phone


@dataclass(slots=True)
class Person(BaseEntity):
    """Common personal data shared by trainees and trainers."""

    name: str
    age: int
    phone: str
    email: str

    def __post_init__(self) -> None:
        BaseEntity.__post_init__(self)
        self.name = validate_name(self.name)
        self.age = validate_age(self.age)
        self.phone = validate_phone(self.phone)
        self.email = validate_email(self.email)

    def update_personal_info(
        self,
        *,
        name: str | None = None,
        age: int | None = None,
        phone: str | None = None,
        email: str | None = None,
    ) -> None:
        """Update common contact information while preserving invariants."""
        if name is not None:
            self.name = validate_name(name)
        if age is not None:
            self.age = validate_age(age)
        if phone is not None:
            self.phone = validate_phone(phone)
        if email is not None:
            self.email = validate_email(email)
