"""Isolated tests for the M3 enrollment and assignment feature slice.

The tests intentionally use in-memory fakes.  This keeps domain and
application behavior independent from the JSON file and makes failures
specific to the layer under test.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType
import sys
from typing import Any

import pytest

from app.domain.entities.assignments import (
    CourseTrainerAssignment,
    TrainerTraineeAssignment,
)
from app.domain.entities.enrollment import Enrollment
from app.domain.enums import CourseStatus, EnrollmentStatus, Role
from app.domain.exceptions import (
    BusinessRuleError,
    DuplicateError,
    NotFoundError,
)
from app.domain.repositories.assignment_repository import AssignmentRepository
from app.domain.repositories.enrollment_repository import EnrollmentRepository
from app.infrastructure.persistence.json_database import JsonDatabase
from app.infrastructure.persistence.json_unit_of_work import JsonUnitOfWork


@dataclass(slots=True)
class FakeUser:
    """Minimal authenticated user shape consumed by M3 authorization helpers."""

    role: Role
    profile_id: str | None = None


@dataclass(slots=True)
class FakeCourse:
    """Minimal course shape required by enrollment application rules."""

    id: str
    total_hours: int = 10


@dataclass(slots=True)
class FakeDailyReport:
    """Minimal report shape required by the course-progress calculation."""

    hours_done: int


class InMemoryEnrollmentRepository(EnrollmentRepository):
    """In-memory implementation of the enrollment query contract."""

    def __init__(self, items: list[Enrollment] | None = None) -> None:
        self.items = list(items or [])

    def add(self, entity: Enrollment) -> Enrollment:
        if self.exists(entity.id):
            raise DuplicateError(entity.id)
        self.items.append(entity)
        return entity

    def get_by_id(self, entity_id: str) -> Enrollment | None:
        return next((item for item in self.items if item.id == entity_id), None)

    def get_required(self, entity_id: str) -> Enrollment:
        item = self.get_by_id(entity_id)
        if item is None:
            raise NotFoundError(entity_id)
        return item

    def get_all(self) -> list[Enrollment]:
        return list(self.items)

    def update(self, entity: Enrollment) -> Enrollment:
        for index, item in enumerate(self.items):
            if item.id == entity.id:
                self.items[index] = entity
                return entity
        raise NotFoundError(entity.id)

    def delete(self, entity_id: str) -> None:
        item = self.get_required(entity_id)
        self.items.remove(item)

    def exists(self, entity_id: str) -> bool:
        return self.get_by_id(entity_id) is not None

    def count(self) -> int:
        return len(self.items)

    def get_active_by_trainee(self, trainee_id: str) -> Enrollment | None:
        return next(
            (
                item
                for item in self.items
                if item.trainee_id == trainee_id and item.is_active()
            ),
            None,
        )

    def get_by_course(self, course_id: str) -> list[Enrollment]:
        return [item for item in self.items if item.course_id == course_id]

    def get_by_trainee(self, trainee_id: str) -> list[Enrollment]:
        return [item for item in self.items if item.trainee_id == trainee_id]


class InMemoryAssignmentRepository(AssignmentRepository):
    """In-memory implementation of the assignment query contract."""

    def __init__(
        self,
        items: list[CourseTrainerAssignment | TrainerTraineeAssignment] | None = None,
    ) -> None:
        self.items = list(items or [])

    def add(
        self, entity: CourseTrainerAssignment | TrainerTraineeAssignment
    ) -> CourseTrainerAssignment | TrainerTraineeAssignment:
        if self.exists(entity.id):
            raise DuplicateError(entity.id)
        self.items.append(entity)
        return entity

    def get_by_id(
        self, entity_id: str
    ) -> CourseTrainerAssignment | TrainerTraineeAssignment | None:
        return next((item for item in self.items if item.id == entity_id), None)

    def get_required(
        self, entity_id: str
    ) -> CourseTrainerAssignment | TrainerTraineeAssignment:
        item = self.get_by_id(entity_id)
        if item is None:
            raise NotFoundError(entity_id)
        return item

    def get_all(
        self,
    ) -> list[CourseTrainerAssignment | TrainerTraineeAssignment]:
        return list(self.items)

    def update(
        self, entity: CourseTrainerAssignment | TrainerTraineeAssignment
    ) -> CourseTrainerAssignment | TrainerTraineeAssignment:
        for index, item in enumerate(self.items):
            if item.id == entity.id:
                self.items[index] = entity
                return entity
        raise NotFoundError(entity.id)

    def delete(self, entity_id: str) -> None:
        item = self.get_required(entity_id)
        self.items.remove(item)

    def exists(self, entity_id: str) -> bool:
        return self.get_by_id(entity_id) is not None

    def count(self) -> int:
        return len(self.items)

    def is_trainer_assigned_to_course(self, trainer_id: str, course_id: str) -> bool:
        return any(
            isinstance(item, CourseTrainerAssignment)
            and item.trainer_id == trainer_id
            and item.course_id == course_id
            for item in self.items
        )

    def is_trainer_assigned_to_trainee(
        self, trainer_id: str, trainee_id: str, course_id: str
    ) -> bool:
        return any(
            isinstance(item, TrainerTraineeAssignment)
            and item.trainer_id == trainer_id
            and item.trainee_id == trainee_id
            and item.course_id == course_id
            for item in self.items
        )

    def get_courses_by_trainer(self, trainer_id: str) -> list[CourseTrainerAssignment]:
        return [
            item
            for item in self.items
            if isinstance(item, CourseTrainerAssignment)
            and item.trainer_id == trainer_id
        ]

    def get_trainees_by_trainer(
        self, trainer_id: str, course_id: str
    ) -> list[TrainerTraineeAssignment]:
        return [
            item
            for item in self.items
            if isinstance(item, TrainerTraineeAssignment)
            and item.trainer_id == trainer_id
            and item.course_id == course_id
        ]


@dataclass
class FakeUnitOfWork:
    """Small UoW double exposing only the repositories used by M3."""

    enrollment_repository: InMemoryEnrollmentRepository
    assignment_repository: InMemoryAssignmentRepository
    courses: dict[str, FakeCourse] = field(default_factory=dict)
    trainees: set[str] = field(default_factory=set)
    trainers: set[str] = field(default_factory=set)
    reports: dict[str, list[FakeDailyReport]] = field(default_factory=dict)

    def __enter__(self) -> "FakeUnitOfWork":
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> bool:
        return False

    @property
    def course_repository(self) -> Any:
        return _RequiredLookup(self.courses)

    @property
    def trainee_repository(self) -> Any:
        return _RequiredLookup({item: item for item in self.trainees})

    @property
    def trainer_repository(self) -> Any:
        return _RequiredLookup({item: item for item in self.trainers})

    @property
    def daily_report_repository(self) -> Any:
        return _ReportsLookup(self.reports)


class _RequiredLookup:
    """Fake repository for existence checks performed by M3 use cases."""

    def __init__(self, values: dict[str, Any]) -> None:
        self.values = values

    def get_required(self, entity_id: str) -> Any:
        if entity_id not in self.values:
            raise NotFoundError(entity_id)
        return self.values[entity_id]


class _ReportsLookup:
    def __init__(self, reports: dict[str, list[FakeDailyReport]]) -> None:
        self.reports = reports

    def get_by_course(self, course_id: str) -> list[FakeDailyReport]:
        return list(self.reports.get(course_id, []))


def _load_m3_use_cases():
    """Load application use cases while documenting the current User contract gap.

    ``common.py`` imports a User entity that is not present in this foundation
    checkout.  A type-only test double lets the isolated application tests
    exercise M3 behavior without creating or modifying a production entity.
    """

    user_module = ModuleType("app.domain.entities.user")
    user_module.User = FakeUser
    sys.modules.setdefault("app.domain.entities.user", user_module)

    from app.application.dto.requests import (
        AssignTrainerRequest,
        AssignTraineeRequest,
        EnrollTraineeRequest,
    )
    from app.application.use_cases.assignments import (
        AssignTrainerToCourseUseCase,
        AssignTrainerToTraineeUseCase,
    )
    from app.application.use_cases.enrollments import (
        CompleteEnrollmentUseCase,
        EnrollTraineeUseCase,
    )

    return (
        AssignTrainerRequest,
        AssignTraineeRequest,
        EnrollTraineeRequest,
        AssignTrainerToCourseUseCase,
        AssignTrainerToTraineeUseCase,
        CompleteEnrollmentUseCase,
        EnrollTraineeUseCase,
    )


def test_enrollment_entity_lifecycle_and_duplicate_completion() -> None:
    enrollment = Enrollment(
        id="ENR-1",
        trainee_id="TRA-1",
        course_id="COURSE-1",
        status=EnrollmentStatus.ACTIVE,
    )
    completed_at = datetime.now(timezone.utc)

    assert enrollment.is_active()
    enrollment.complete(completed_at)
    assert enrollment.is_completed()
    assert enrollment.completed_at == completed_at

    with pytest.raises(BusinessRuleError):
        enrollment.complete(completed_at)


def test_assignment_entities_preserve_their_scope() -> None:
    course_assignment = CourseTrainerAssignment(
        id="CTA-1", course_id="COURSE-1", trainer_id="TRAINER-1"
    )
    trainee_assignment = TrainerTraineeAssignment(
        id="TTA-1",
        course_id="COURSE-1",
        trainer_id="TRAINER-1",
        trainee_id="TRAINEE-1",
    )

    assert course_assignment.course_id == trainee_assignment.course_id
    assert trainee_assignment.trainer_id == course_assignment.trainer_id


def test_enrollment_repository_queries_are_isolated() -> None:
    active = Enrollment(
        id="ENR-A",
        trainee_id="TRAINEE-1",
        course_id="COURSE-1",
        status=EnrollmentStatus.ACTIVE,
    )
    completed = Enrollment(
        id="ENR-C",
        trainee_id="TRAINEE-1",
        course_id="COURSE-2",
        status=EnrollmentStatus.COMPLETED,
        completed_at=datetime.now(timezone.utc),
    )
    repository = InMemoryEnrollmentRepository([active, completed])

    assert repository.get_active_by_trainee("TRAINEE-1") == active
    assert repository.get_by_course("COURSE-2") == [completed]
    assert repository.get_by_trainee("TRAINEE-1") == [active, completed]


def test_assignment_repository_queries_are_isolated() -> None:
    course_assignment = CourseTrainerAssignment(
        id="CTA-1", course_id="COURSE-1", trainer_id="TRAINER-1"
    )
    trainee_assignment = TrainerTraineeAssignment(
        id="TTA-1",
        course_id="COURSE-1",
        trainer_id="TRAINER-1",
        trainee_id="TRAINEE-1",
    )
    repository = InMemoryAssignmentRepository([course_assignment, trainee_assignment])

    assert repository.is_trainer_assigned_to_course("TRAINER-1", "COURSE-1")
    assert repository.is_trainer_assigned_to_trainee(
        "TRAINER-1", "TRAINEE-1", "COURSE-1"
    )
    assert repository.get_courses_by_trainer("TRAINER-1") == [course_assignment]
    assert repository.get_trainees_by_trainer("TRAINER-1", "COURSE-1") == [
        trainee_assignment
    ]


def test_json_uow_persists_m3_repositories_with_real_adapters(tmp_path: Path) -> None:
    database = JsonDatabase(tmp_path / "database.json")
    database.initialize()
    enrollment = Enrollment(
        id="ENR-REAL",
        trainee_id="TRAINEE-REAL",
        course_id="COURSE-REAL",
        status=EnrollmentStatus.ACTIVE,
    )
    course_assignment = CourseTrainerAssignment(
        id="CTA-REAL",
        course_id="COURSE-REAL",
        trainer_id="TRAINER-REAL",
    )
    trainee_assignment = TrainerTraineeAssignment(
        id="TTA-REAL",
        course_id="COURSE-REAL",
        trainer_id="TRAINER-REAL",
        trainee_id="TRAINEE-REAL",
    )

    with JsonUnitOfWork(database) as uow:
        assert uow.enrollment_repository is not None
        assert uow.assignment_repository is not None
        uow.enrollment_repository.add(enrollment)
        uow.assignment_repository.add(course_assignment)
        uow.assignment_repository.add(trainee_assignment)

    with JsonUnitOfWork(database) as uow:
        restored_enrollment = uow.enrollment_repository.get_active_by_trainee(
            "TRAINEE-REAL"
        )
        assert restored_enrollment == enrollment
        assert uow.assignment_repository.is_trainer_assigned_to_course(
            "TRAINER-REAL", "COURSE-REAL"
        )
        assert uow.assignment_repository.is_trainer_assigned_to_trainee(
            "TRAINER-REAL", "TRAINEE-REAL", "COURSE-REAL"
        )


def test_enroll_use_case_creates_one_active_enrollment_only() -> None:
    (
        _,
        _,
        EnrollTraineeRequest,
        _,
        _,
        _,
        EnrollTraineeUseCase,
    ) = _load_m3_use_cases()
    uow = FakeUnitOfWork(
        enrollment_repository=InMemoryEnrollmentRepository(),
        assignment_repository=InMemoryAssignmentRepository(),
        courses={"COURSE-1": FakeCourse("COURSE-1")},
        trainees={"TRAINEE-1"},
    )
    manager = FakeUser(Role.COURSE_MANAGER)
    use_case = EnrollTraineeUseCase(lambda: uow)
    request = EnrollTraineeRequest("TRAINEE-1", "COURSE-1")

    created = use_case.execute(request, manager)
    assert created.is_active()

    with pytest.raises(BusinessRuleError):
        use_case.execute(request, manager)


def test_enroll_use_case_rejects_missing_references() -> None:
    (
        _,
        _,
        EnrollTraineeRequest,
        _,
        _,
        _,
        EnrollTraineeUseCase,
    ) = _load_m3_use_cases()
    uow = FakeUnitOfWork(
        enrollment_repository=InMemoryEnrollmentRepository(),
        assignment_repository=InMemoryAssignmentRepository(),
        courses={},
        trainees={"TRAINEE-1"},
    )

    with pytest.raises(NotFoundError):
        EnrollTraineeUseCase(lambda: uow).execute(
            EnrollTraineeRequest("TRAINEE-1", "COURSE-MISSING"),
            FakeUser(Role.COURSE_MANAGER),
        )


def test_assignment_use_cases_require_course_trainer_and_scope() -> None:
    (
        AssignTrainerRequest,
        AssignTraineeRequest,
        _,
        AssignTrainerToCourseUseCase,
        AssignTrainerToTraineeUseCase,
        _,
        _,
    ) = _load_m3_use_cases()
    uow = FakeUnitOfWork(
        enrollment_repository=InMemoryEnrollmentRepository(),
        assignment_repository=InMemoryAssignmentRepository(),
        courses={"COURSE-1": FakeCourse("COURSE-1")},
        trainees={"TRAINEE-1"},
        trainers={"TRAINER-1"},
    )
    manager = FakeUser(Role.COURSE_MANAGER)

    AssignTrainerToCourseUseCase(lambda: uow).execute(
        AssignTrainerRequest("COURSE-1", "TRAINER-1"), manager
    )
    assignment_use_case = AssignTrainerToTraineeUseCase(lambda: uow)
    created = assignment_use_case.execute(
        AssignTraineeRequest("COURSE-1", "TRAINER-1", "TRAINEE-1"), manager
    )
    assert created.trainee_id == "TRAINEE-1"

    with pytest.raises(DuplicateError):
        assignment_use_case.execute(
            AssignTraineeRequest("COURSE-1", "TRAINER-1", "TRAINEE-1"), manager
        )


def test_assign_trainer_to_trainee_rejects_unscoped_trainer() -> None:
    (
        _,
        AssignTraineeRequest,
        _,
        _,
        AssignTrainerToTraineeUseCase,
        _,
        _,
    ) = _load_m3_use_cases()
    uow = FakeUnitOfWork(
        enrollment_repository=InMemoryEnrollmentRepository(),
        assignment_repository=InMemoryAssignmentRepository(),
        courses={"COURSE-1": FakeCourse("COURSE-1")},
        trainees={"TRAINEE-1"},
        trainers={"TRAINER-1"},
    )

    with pytest.raises(BusinessRuleError):
        AssignTrainerToTraineeUseCase(lambda: uow).execute(
            AssignTraineeRequest("COURSE-1", "TRAINER-1", "TRAINEE-1"),
            FakeUser(Role.COURSE_MANAGER),
        )


def test_complete_enrollment_requires_completed_course() -> None:
    (
        _,
        _,
        _,
        _,
        _,
        CompleteEnrollmentUseCase,
        _,
    ) = _load_m3_use_cases()
    enrollment = Enrollment(
        id="ENR-1",
        trainee_id="TRAINEE-1",
        course_id="COURSE-1",
        status=EnrollmentStatus.ACTIVE,
    )
    uow = FakeUnitOfWork(
        enrollment_repository=InMemoryEnrollmentRepository([enrollment]),
        assignment_repository=InMemoryAssignmentRepository(),
        courses={"COURSE-1": FakeCourse("COURSE-1", total_hours=10)},
        reports={"COURSE-1": [FakeDailyReport(5)]},
    )

    assert calculate_status(uow) is CourseStatus.IN_PROGRESS
    with pytest.raises(BusinessRuleError):
        CompleteEnrollmentUseCase(lambda: uow).execute(
            "ENR-1", FakeUser(Role.COURSE_MANAGER)
        )


def test_complete_enrollment_updates_status_after_course_completion() -> None:
    (
        _,
        _,
        _,
        _,
        _,
        CompleteEnrollmentUseCase,
        _,
    ) = _load_m3_use_cases()
    enrollment = Enrollment(
        id="ENR-1",
        trainee_id="TRAINEE-1",
        course_id="COURSE-1",
        status=EnrollmentStatus.ACTIVE,
    )
    uow = FakeUnitOfWork(
        enrollment_repository=InMemoryEnrollmentRepository([enrollment]),
        assignment_repository=InMemoryAssignmentRepository(),
        courses={"COURSE-1": FakeCourse("COURSE-1", total_hours=10)},
        reports={"COURSE-1": [FakeDailyReport(10)]},
    )

    completed = CompleteEnrollmentUseCase(lambda: uow).execute(
        "ENR-1", FakeUser(Role.COURSE_MANAGER)
    )

    assert completed.is_completed()
    assert completed.completed_at is not None


def calculate_status(uow: FakeUnitOfWork) -> CourseStatus:
    """Calculate the fake course status without reaching a production adapter."""

    completed_hours = sum(
        report.hours_done for report in uow.reports.get("COURSE-1", [])
    )
    if completed_hours == 0:
        return CourseStatus.NOT_STARTED
    if completed_hours < uow.courses["COURSE-1"].total_hours:
        return CourseStatus.IN_PROGRESS
    return CourseStatus.COMPLETED
