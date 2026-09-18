from __future__ import annotations

from dataclasses import dataclass

from app.domain.entities.person import Person
from app.domain.enums import Category, TrainingMethod
from app.domain.validation import validate_enum


@dataclass(slots=True)
class Trainer(Person):
    """A trainer who may work onsite, remotely, or administratively."""

    category: Category
    training_method: TrainingMethod

    def __post_init__(self) -> None:
        Person.__post_init__(self)
        self.category = validate_enum(self.category, Category, "category")
        self.training_method = validate_enum(
            self.training_method, TrainingMethod, "training_method"
        )

    def change_category(self, new_category: Category) -> None:
        self.category = validate_enum(new_category, Category, "category")

    def change_training_method(self, new_method: TrainingMethod) -> None:
        self.training_method = validate_enum(
            new_method, TrainingMethod, "training_method"
        )

