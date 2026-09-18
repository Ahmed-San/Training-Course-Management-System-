from __future__ import annotations

from pathlib import Path
from datetime import date, datetime, timezone
from enum import StrEnum
from dataclasses import dataclass

from app.domain.entities.base_entity import BaseEntity
from app.domain.exceptions import ValidationError
from app.infrastructure.persistence.json_database import JsonDatabase
from app.infrastructure.persistence.json_repository import JsonRepository
from app.infrastructure.persistence.json_unit_of_work import JsonUnitOfWork


def test_generic_json_repository_crud(tmp_path: Path) -> None:
    database = JsonDatabase(tmp_path / "database.json", collections=("items",))
    database.initialize()

    with JsonUnitOfWork(database) as uow:
        repository = JsonRepository[BaseEntity](
            state=uow.state,
            collection_name="items",
            entity_type=BaseEntity,
        )
        item = BaseEntity(id="E001")
        repository.add(item)
        assert repository.exists("E001")
        assert repository.count() == 1
        assert repository.get_by_id("E001") == item

    assert database.load()["items"] == [{"id": "E001"}]


class _Level(StrEnum):
    HIGH = "high"


@dataclass(slots=True)
class _Record(BaseEntity):
    level: _Level
    when: datetime
    day: date


def test_serializer_round_trip_for_enum_and_dates() -> None:
    from app.infrastructure.persistence.serializer import entity_from_dict, entity_to_dict

    original = _Record(
        id="R001",
        level=_Level.HIGH,
        when=datetime(2026, 9, 18, 12, 30, tzinfo=timezone.utc),
        day=date(2026, 9, 18),
    )
    payload = entity_to_dict(original)
    restored = entity_from_dict(payload, _Record)
    assert restored == original
    assert payload["level"] == "high"
    assert payload["day"] == "2026-09-18"


@dataclass(slots=True)
class _OptionalRecord(BaseEntity):
    note: str | None


def test_serializer_round_trip_for_optional_field() -> None:
    from app.infrastructure.persistence.serializer import entity_from_dict, entity_to_dict

    original = _OptionalRecord(id="O001", note=None)
    restored = entity_from_dict(entity_to_dict(original), _OptionalRecord)
    assert restored == original


def test_unit_of_work_rolls_back_on_exception(tmp_path: Path) -> None:
    database = JsonDatabase(tmp_path / "database.json", collections=("items",))
    database.initialize()

    try:
        with JsonUnitOfWork(database) as uow:
            repository = JsonRepository[BaseEntity](
                state=uow.state,
                collection_name="items",
                entity_type=BaseEntity,
            )
            repository.add(BaseEntity(id="E002"))
            raise ValidationError("force rollback")
    except ValidationError:
        pass

    assert database.load()["items"] == []
