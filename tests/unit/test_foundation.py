from __future__ import annotations

from pathlib import Path

import pytest

from app.application.services.authorization import AuthorizationService
from app.application.services.course_progress import calculate_course_progress
from app.domain.enums import CourseStatus, Permission, Role, TrainingMethod
from app.domain.entities.person import Person
from app.domain.exceptions import AuthorizationError, ValidationError
from app.infrastructure.auth.password_hasher import PasswordHasher
from app.infrastructure.persistence.json_database import JsonDatabase


def test_person_reuses_common_validation() -> None:
    person = Person(
        id="P001",
        name="Ahmed",
        age=20,
        phone="777123456",
        email="ahmed@example.com",
    )
    assert person.name == "Ahmed"
    assert person.email == "ahmed@example.com"


def test_invalid_email_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Person(
            id="P001",
            name="Ahmed",
            age=20,
            phone="777123456",
            email="invalid",
        )


def test_course_progress_rules() -> None:
    progress = calculate_course_progress(total_hours=10, reported_hours=[4, 6])
    assert progress.completed_hours == 10
    assert progress.remaining_hours == 0
    assert progress.status is CourseStatus.COMPLETED


def test_authorization_rejects_remote_trainer_for_management() -> None:
    with pytest.raises(AuthorizationError):
        AuthorizationService.require_onsite_trainer(
            user_role=Role.TRAINER,
            training_method=TrainingMethod.REMOTE,
        )


def test_manager_has_edit_course_permission() -> None:
    AuthorizationService.require_permission(Role.COURSE_MANAGER, Permission.EDIT_COURSE)


def test_password_hash_round_trip() -> None:
    hasher = PasswordHasher()
    stored = hasher.hash("secret123")
    assert stored != "secret123"
    assert hasher.verify("secret123", stored) is True
    assert hasher.verify("wrong", stored) is False


def test_json_database_creates_expected_root(tmp_path: Path) -> None:
    path = tmp_path / "database.json"
    database = JsonDatabase(path)
    database.initialize()
    state = database.load()
    assert set(state) == {
        "users",
        "trainees",
        "trainers",
        "courses",
        "enrollments",
        "evaluations",
        "daily_reports",
        "course_trainer_assignments",
        "trainer_trainee_assignments",
    }
