from __future__ import annotations

from dataclasses import dataclass

from app.domain.entities.person import Person
from app.domain.enums import Category
from app.domain.exceptions import ValidationError
from app.domain.validation import validate_enum


@dataclass(slots=True)
class Trainee(Person):
    """A trainee enrolled in training courses."""

    category: Category

    def __post_init__(self) -> None:
        Person.__post_init__(self)
        self.category = validate_enum(self.category, Category, "category")

    def change_category(self, new_category: Category) -> None:
        self.category = validate_enum(new_category, Category, "category")


