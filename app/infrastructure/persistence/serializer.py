from __future__ import annotations

from dataclasses import fields, is_dataclass
from datetime import date, datetime
from enum import Enum
import types
from typing import Any, Union, get_args, get_origin, get_type_hints

from app.domain.exceptions import StorageError


def to_primitive(value: Any) -> Any:
    """Convert supported domain values into JSON-safe Python primitives."""
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if is_dataclass(value):
        return {field.name: to_primitive(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, list):
        return [to_primitive(item) for item in value]
    if isinstance(value, tuple):
        return [to_primitive(item) for item in value]
    if isinstance(value, dict):
        return {str(key): to_primitive(item) for key, item in value.items()}
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise StorageError(f"Unsupported value for serialization: {type(value).__name__}")


def entity_to_dict(entity: Any) -> dict[str, Any]:
    if not is_dataclass(entity):
        raise StorageError("Only dataclass entities can be serialized by the foundation serializer.")
    return to_primitive(entity)


def _from_primitive(value: Any, annotation: Any) -> Any:
    if annotation is Any:
        return value

    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin in (Union, types.UnionType):
        non_none = [arg for arg in args if arg is not type(None)]
        if value is None:
            return None
        if len(non_none) == 1:
            return _from_primitive(value, non_none[0])

    if origin is list:
        item_type = args[0] if args else Any
        return [_from_primitive(item, item_type) for item in value]

    if origin is dict:
        key_type, value_type = args if len(args) == 2 else (str, Any)
        return {
            _from_primitive(key, key_type): _from_primitive(item, value_type)
            for key, item in value.items()
        }

    if isinstance(annotation, type) and issubclass(annotation, Enum):
        return annotation(value)

    if annotation is datetime:
        return datetime.fromisoformat(value)
    if annotation is date:
        return date.fromisoformat(value)

    if isinstance(annotation, type) and is_dataclass(annotation):
        return entity_from_dict(value, annotation)

    return value


def entity_from_dict(data: dict[str, Any], entity_type: type[Any]) -> Any:
    if not is_dataclass(entity_type):
        raise StorageError(f"{entity_type.__name__} must be a dataclass.")
    try:
        hints = get_type_hints(entity_type)
        kwargs = {
            field.name: _from_primitive(data[field.name], hints.get(field.name, field.type))
            for field in fields(entity_type)
            if field.name in data
        }
        return entity_type(**kwargs)
    except (KeyError, TypeError, ValueError) as exc:
        raise StorageError(f"Unable to deserialize {entity_type.__name__}.") from exc
