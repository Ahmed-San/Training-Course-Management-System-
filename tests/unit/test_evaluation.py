from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import pytest

from app.application.dto.requests import CreateEvaluationRequest, UpdateEvaluationRequest
from app.application.use_cases.evaluations import (
    CreateEvaluationUseCase,
    ListEvaluationsUseCase,
    UpdateEvaluationUseCase,
    ViewEvaluationUseCase,
)
from app.domain.entities.course import Course
from app.domain.entities.enrollment import Enrollment
from app.domain.entities.evaluation import Evaluation
from app.domain.entities.trainer import Trainer
from app.domain.enums import Category, EnrollmentStatus, Grade, Role, TrainingMethod
from app.domain.entities.user import User
from app.domain.exceptions import (
    AuthorizationError,
    BusinessRuleError,
    DuplicateError,
    ValidationError,
)


class FakeRepository:
    def __init__(self, items=None):
        self.items = {item.id: item for item in (items or [])}

    def add(self, entity):
        if entity.id in self.items:
            raise DuplicateError("duplicate")
        self.items[entity.id] = entity
        return entity

    def get_required(self, entity_id):
        item = self.items.get(entity_id)
        if item is None:
            raise KeyError(entity_id)
        return item

    def get_all(self):
        return list(self.items.values())

    def get_by_id(self, entity_id):
        return self.items.get(entity_id)

    def update(self, entity):
        if entity.id not in self.items:
            raise KeyError(entity.id)
        self.items[entity.id] = entity
        return entity


class FakeEvaluationRepository(FakeRepository):
    def get_by_enrollment(self, enrollment_id):
        return next(
            (item for item in self.items.values() if item.enrollment_id == enrollment_id),
            None,
        )


class FakeAssignmentRepository:
    def __init__(self, course_assignments=None, trainee_assignments=None):
        self.course_assignments = set(course_assignments or [])
        self.trainee_assignments = set(trainee_assignments or [])

    def is_trainer_assigned_to_course(self, trainer_id, course_id):
        return (trainer_id, course_id) in self.course_assignments

    def is_trainer_assigned_to_trainee(self, trainer_id, trainee_id, course_id):
        return (trainer_id, trainee_id, course_id) in self.trainee_assignments


@dataclass
class FakeUow:
    course_repository: FakeRepository
    enrollment_repository: FakeRepository
    trainer_repository: FakeRepository
    evaluation_repository: FakeEvaluationRepository
    assignment_repository: FakeAssignmentRepository

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


def scenario(*, enrollment_status=EnrollmentStatus.ACTIVE, assigned=True, remote=False, with_evaluation=False):
    user = User("U-TR", "trainer", "hash", Role.TRAINER, profile_id="TR001")
    trainer = Trainer(
        "TR001", "Trainer", 30, "777111111", "tr@example.com", Category.A,
        TrainingMethod.REMOTE if remote else TrainingMethod.ONSITE,
    )
    course = Course("C001", "Python", 10, "Course", 1, "U-MGR")
    completed_at = datetime.now(timezone.utc) if enrollment_status is EnrollmentStatus.COMPLETED else None
    enrollment = Enrollment("ENR001", "T001", "C001", enrollment_status, completed_at)
    evaluation = (
        Evaluation(
            "EVA-ENR001", "ENR001", "TR001", Grade.A,
            datetime.now(timezone.utc), datetime.now(timezone.utc),
        )
        if with_evaluation else None
    )
    assignments = FakeAssignmentRepository(
        course_assignments={("TR001", "C001")} if assigned else set(),
        trainee_assignments={("TR001", "T001", "C001")} if assigned else set(),
    )
    uow = FakeUow(
        course_repository=FakeRepository([course]),
        enrollment_repository=FakeRepository([enrollment]),
        trainer_repository=FakeRepository([trainer]),
        evaluation_repository=FakeEvaluationRepository([evaluation] if evaluation else []),
        assignment_repository=assignments,
    )
    factory = lambda: uow
    return user, trainer, course, enrollment, evaluation, factory


def test_evaluation_entity_rejects_invalid_timestamps():
    now = datetime.now(timezone.utc)
    with pytest.raises(ValidationError):
        Evaluation("E1", "ENR1", "TR1", Grade.A, now, now - timedelta(seconds=1))


def test_evaluation_entity_change_grade_does_not_change_timestamp():
    now = datetime.now(timezone.utc)
    evaluation = Evaluation("E1", "ENR1", "TR1", Grade.A, now, now)
    evaluation.change_grade(Grade.B)
    assert evaluation.grade is Grade.B
    assert evaluation.updated_at == now


def test_create_evaluation_success():
    user, _, _, enrollment, _, factory = scenario()
    created = CreateEvaluationUseCase(factory).execute(
        CreateEvaluationRequest(enrollment.id, Grade.A), user
    )
    assert created.enrollment_id == "ENR001"
    assert created.trainer_id == "TR001"
    assert created.grade is Grade.A


def test_create_duplicate_is_rejected_with_duplicate_error():
    user, _, _, enrollment, _, factory = scenario(with_evaluation=True)
    with pytest.raises(DuplicateError):
        CreateEvaluationUseCase(factory).execute(
            CreateEvaluationRequest(enrollment.id, Grade.B), user
        )


def test_create_evaluation_for_completed_enrollment_is_rejected():
    user, _, _, enrollment, _, factory = scenario(enrollment_status=EnrollmentStatus.COMPLETED)
    with pytest.raises(BusinessRuleError):
        CreateEvaluationUseCase(factory).execute(
            CreateEvaluationRequest(enrollment.id, Grade.A), user
        )


def test_remote_trainer_cannot_create_evaluation():
    user, _, _, enrollment, _, factory = scenario(remote=True)
    with pytest.raises(AuthorizationError):
        CreateEvaluationUseCase(factory).execute(
            CreateEvaluationRequest(enrollment.id, Grade.A), user
        )


def test_trainer_outside_assignment_cannot_create_evaluation():
    user, _, _, enrollment, _, factory = scenario(assigned=False)
    with pytest.raises(AuthorizationError):
        CreateEvaluationUseCase(factory).execute(
            CreateEvaluationRequest(enrollment.id, Grade.A), user
        )


def test_trainer_can_update_before_completion():
    user, _, _, _, evaluation, factory = scenario(with_evaluation=True)
    updated = UpdateEvaluationUseCase(factory).execute(
        UpdateEvaluationRequest(evaluation.id, Grade.B), user
    )
    assert updated.grade is Grade.B
    assert updated.updated_at >= updated.created_at


def test_trainer_cannot_update_after_completion():
    user, _, _, _, evaluation, factory = scenario(
        enrollment_status=EnrollmentStatus.COMPLETED,
        with_evaluation=True,
    )
    with pytest.raises(AuthorizationError):
        UpdateEvaluationUseCase(factory).execute(
            UpdateEvaluationRequest(evaluation.id, Grade.B), user
        )


def test_trainer_cannot_update_evaluation_created_by_another_trainer():
    user, _, _, _, evaluation, factory = scenario(with_evaluation=True)
    evaluation.trainer_id = "TR999"
    with pytest.raises(AuthorizationError):
        UpdateEvaluationUseCase(factory).execute(
            UpdateEvaluationRequest(evaluation.id, Grade.B), user
        )


def test_list_for_trainer_uses_course_and_trainee_scope():
    user, _, _, _, evaluation, factory = scenario(with_evaluation=True)
    result = ListEvaluationsUseCase(factory).execute(user)
    assert result == [evaluation]


def test_view_requires_scope():
    user, _, _, _, evaluation, factory = scenario(assigned=False, with_evaluation=True)
    with pytest.raises(AuthorizationError):
        ViewEvaluationUseCase(factory).execute(user, evaluation_id=evaluation.id)


def test_view_requires_an_identifier():
    user, _, _, _, _, factory = scenario()
    with pytest.raises(ValidationError):
        ViewEvaluationUseCase(factory).execute(user)
