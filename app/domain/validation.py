from __future__ import annotations

import re
from email.utils import parseaddr
from enum import Enum
from typing import TypeVar

from app.domain.exceptions import ValidationError

E = TypeVar("E", bound=Enum)
_EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def validate_name(value: str) -> str:
    if not isinstance(value, str):
        raise ValidationError("Name must be a string.")
    cleaned = value.strip()
    if not cleaned:
        raise ValidationError("Name must not be empty.")
    return cleaned


def validate_age(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError("Age must be an integer.")
    if not 1 <= value <= 120:
        raise ValidationError("Age must be between 1 and 120.")
    return value


def validate_phone(value: str) -> str:
    if not isinstance(value, str):
        raise ValidationError("Phone must be a string.")
    cleaned = value.strip()
    digits = re.sub(r"\D", "", cleaned)
    if len(digits) < 7 or len(digits) > 15:
        raise ValidationError("Phone must contain between 7 and 15 digits.")
    return cleaned


def validate_email(value: str) -> str:
    if not isinstance(value, str):
        raise ValidationError("Email must be a string.")
    cleaned = value.strip().lower()
    if not _EMAIL_PATTERN.fullmatch(cleaned):
        raise ValidationError("Email format is invalid.")
    parsed = parseaddr(cleaned)[1]
    if parsed != cleaned:
        raise ValidationError("Email format is invalid.")
    return cleaned


def validate_non_empty(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field_name} must not be empty.")
    return value.strip()


def validate_positive_int(value: int, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError(f"{field_name} must be an integer.")
    if value <= 0:
        raise ValidationError(f"{field_name} must be greater than zero.")
    return value


def validate_non_negative_int(value: int, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError(f"{field_name} must be an integer.")
    if value < 0:
        raise ValidationError(f"{field_name} must not be negative.")
    return value


def validate_enum(value: E, enum_type: type[E], field_name: str) -> E:
    if not isinstance(value, enum_type):
        raise ValidationError(f"{field_name} must be a valid {enum_type.__name__}.")
    return value
