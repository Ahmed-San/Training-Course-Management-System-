from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone

import pytest

from app.application.dto.requests import CreateDailyReportRequest, UpdateDailyReportRequest
from app.application.services.course_progress import calculate_course_progress
from app.application.use_cases.reports import (
    CreateDailyReportUseCase,
    DeleteDailyReportUseCase,
    ListDailyReportsUseCase,
    UpdateDailyReportUseCase,
)
from app.domain.entities.course import Course
from app.domain.entities.daily_report import DailyReport
from app.domain.entities.enrollment import Enrollment
from app.domain.entities.trainer import Trainer
from app.domain.entities.user import User
from app.domain.enums import Category, CourseStatus, EnrollmentStatus, Role, TrainingMethod
from app.domain.exceptions import AuthorizationError, BusinessRuleError, ValidationError


class MemoryRepository:
    def __init__(self, items=None):
        self.items = list(items or [])
        self.deleted = []

    def add(self, entity):
        self.items.append(entity)
        return entity

    def get_by_id(self, entity_id):
        return next((item for item in self.items if item.id == entity_id), None)

    def get_required(self, entity_id):
        entity = self.get_by_id(entity_id)
        if entity is None:
            raise AssertionError(f"Missing entity: {entity_id}")
        return entity

    def get_all(self):
        return list(self.items)

    def update(self, entity):
        for index, item in enumerate(self.items):
            if item.id == entity.id:
                self.items[index] = entity
                return entity
        raise AssertionError(f"Missing entity: {entity.id}")

    def delete(self, entity_id):
        self.items = [item for item in self.items if item.id != entity_id]
        self.deleted.append(entity_id)

    def exists(self, entity_id):
        return self.get_by_id(entity_id) is not None

    def count(self):
        return len(self.items)


class MemoryEnrollmentRepository(MemoryRepository):
    def get_by_course(self, course_id):
        return [item for item in self.items if item.course_id == course_id]

    def get_by_trainee(self, trainee_id):
        return [item for item in self.items if item.trainee_id == trainee_id]


class MemoryDailyReportRepository(MemoryRepository):
    def get_by_course(self, course_id):
        return [item for item in self.items if item.course_id == course_id]

    def get_by_trainer(self, trainer_id):
        return [item for item in self.items if item.trainer_id == trainer_id]

    def get_by_course_trainer_date(self, course_id, trainer_id, report_date):
        return next(
            (
                item
                for item in self.items
                if item.course_id == course_id
                and item.trainer_id == trainer_id
                and item.report_date == report_date
            ),
            None,
        )


class MemoryAssignmentRepository:
    def __init__(self, course_assignments=None):
        self.course_assignments = set(course_assignments or set())

    def is_trainer_assigned_to_course(self, trainer_id, course_id):
        return (trainer_id, course_id) in self.course_assignments


class FakeUow:
    def __init__(self, *, courses, trainers, enrollments, reports, assignments):
        self.course_repository = MemoryRepository(courses)
        self.trainer_repository = MemoryRepository(trainers)
        self.enrollment_repository = MemoryEnrollmentRepository(enrollments)
        self.daily_report_repository = MemoryDailyReportRepository(reports)
        self.assignment_repository = assignments
        self.commits = 0
        self.rollbacks = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.commits += 1
        else:
            self.rollbacks += 1
        return False


@dataclass
class Scenario:
    manager: User
    trainer_user: User
    trainer: Trainer
    course: Course
    enrollments: list[Enrollment]
    reports: list[DailyReport]
    uow: FakeUow


def scenario(*, remote=False, assigned=True, completed=False, report_hours=0) -> Scenario:
    now = datetime.now(timezone.utc)
    manager = User("U-MGR", "manager", "hash", Role.COURSE_MANAGER, "U-MGR")
    trainer_user = User("U-TR", "trainer", "hash", Role.TRAINER, "TR001")
    trainer = Trainer(
        "TR001",
        "Trainer",
        30,
        "777333333",
        "trainer@example.com",
        Category.A,
        TrainingMethod.REMOTE if remote else TrainingMethod.ONSITE,
    )
    course = Course("C001", "Python", 10, "Course", 1, "U-MGR")
    completed_at = now if completed else None
    enrollment = Enrollment(
        "ENR001",
        "T001",
        "C001",
        EnrollmentStatus.COMPLETED if completed else EnrollmentStatus.ACTIVE,
        completed_at,
    )
    reports = []
    if report_hours:
        reports.append(
            DailyReport(
                "RPT-C001-TR001-2026-09-01",
                "C001",
                "TR001",
                date(2026, 9, 1),
                report_hours,
                "existing",
                now,
                now,
            )
        )
    assignments = MemoryAssignmentRepository({("TR001", "C001")} if assigned else set())
    uow = FakeUow(
        courses=[course],
        trainers=[trainer],
        enrollments=[enrollment],
        reports=reports,
        assignments=assignments,
    )
    return Scenario(
        manager=manager,
        trainer_user=trainer_user,
        trainer=trainer,
        course=course,
        enrollments=[enrollment],
        reports=reports,
        uow=uow,
    )


def factory_for(s):
    return lambda: s.uow


def test_daily_report_entity_validates_local_invariants():
    now = datetime.now(timezone.utc)
    report = DailyReport("R1", "C1", "TR1", date.today(), 2, "note", now, now)
    assert report.hours_done == 2


def test_daily_report_rejects_zero_hours():
    now = datetime.now(timezone.utc)
    with pytest.raises(ValidationError):
        DailyReport("R1", "C1", "TR1", date.today(), 0, "note", now, now)


def test_daily_report_rejects_datetime_as_report_date():
    now = datetime.now(timezone.utc)
    with pytest.raises(ValidationError):
        DailyReport("R1", "C1", "TR1", datetime.now(), 1, "note", now, now)


def test_daily_report_rejects_non_string_note():
    now = datetime.now(timezone.utc)
    with pytest.raises(ValidationError):
        DailyReport("R1", "C1", "TR1", date.today(), 1, 123, now, now)


def test_daily_report_rejects_invalid_timestamps():
    now = datetime.now(timezone.utc)
    with pytest.raises(ValidationError):
        DailyReport("R1", "C1", "TR1", date.today(), 1, "note", now, now - timedelta(seconds=1))


def test_progress_not_started_partial_exact_and_over():
    assert calculate_course_progress(total_hours=10, reported_hours=[]).status is CourseStatus.NOT_STARTED
    assert calculate_course_progress(total_hours=10, reported_hours=[3, 2]).completed_hours == 5
    assert calculate_course_progress(total_hours=10, reported_hours=[5, 5]).status is CourseStatus.COMPLETED
    progress = calculate_course_progress(total_hours=10, reported_hours=[7, 7])
    assert progress.remaining_hours == 0
    assert progress.status is CourseStatus.COMPLETED


def test_remote_trainer_cannot_create_report():
    s = scenario(remote=True)
    with pytest.raises(AuthorizationError):
        CreateDailyReportUseCase(factory_for(s)).execute(
            CreateDailyReportRequest("C001", date(2026, 9, 2), 2, "report"),
            s.trainer_user,
        )


def test_unassigned_trainer_cannot_create_report():
    s = scenario(assigned=False)
    with pytest.raises(AuthorizationError):
        CreateDailyReportUseCase(factory_for(s)).execute(
            CreateDailyReportRequest("C001", date(2026, 9, 2), 2, "report"),
            s.trainer_user,
        )


def test_manager_cannot_mutate_reports():
    s = scenario()
    with pytest.raises(AuthorizationError):
        CreateDailyReportUseCase(factory_for(s)).execute(
            CreateDailyReportRequest("C001", date(2026, 9, 2), 2, "report"),
            s.manager,
        )


def test_report_hours_cannot_exceed_remaining():
    s = scenario(report_hours=7)
    with pytest.raises(BusinessRuleError):
        CreateDailyReportUseCase(factory_for(s)).execute(
            CreateDailyReportRequest("C001", date(2026, 9, 2), 4, "too much"),
            s.trainer_user,
        )


def test_duplicate_report_date_is_rejected():
    s = scenario(report_hours=3)
    with pytest.raises(BusinessRuleError):
        CreateDailyReportUseCase(factory_for(s)).execute(
            CreateDailyReportRequest("C001", date(2026, 9, 1), 2, "duplicate"),
            s.trainer_user,
        )


def test_create_five_hours_and_complete_course_and_active_enrollment():
    s = scenario(report_hours=5)
    report, progress = CreateDailyReportUseCase(factory_for(s)).execute(
        CreateDailyReportRequest("C001", date(2026, 9, 2), 5, "done"),
        s.trainer_user,
    )
    assert report.hours_done == 5
    assert progress.completed_hours == 10
    assert progress.remaining_hours == 0
    assert progress.status is CourseStatus.COMPLETED
    assert s.enrollments[0].status is EnrollmentStatus.COMPLETED
    assert s.enrollments[0].completed_at is not None


def test_create_on_already_completed_course_is_rejected():
    s = scenario(completed=True, report_hours=10)
    with pytest.raises(BusinessRuleError):
        CreateDailyReportUseCase(factory_for(s)).execute(
            CreateDailyReportRequest("C001", date(2026, 9, 3), 1, "late"),
            s.trainer_user,
        )


def test_update_uses_remaining_without_current_report():
    s = scenario(report_hours=3)
    s.reports.append(
        DailyReport(
            "RPT-C001-TR001-2026-09-02",
            "C001",
            "TR001",
            date(2026, 9, 2),
            2,
            "second",
            datetime.now(timezone.utc),
            datetime.now(timezone.utc),
        )
    )
    s.uow.daily_report_repository.items = list(s.reports)
    updated, progress = UpdateDailyReportUseCase(factory_for(s)).execute(
        UpdateDailyReportRequest(s.reports[0].id, hours_done=8),
        s.trainer_user,
    )
    assert updated.hours_done == 8
    assert progress.completed_hours == 10


def test_update_oversized_hours_is_rejected_before_mutation():
    s = scenario(report_hours=3)
    original = s.reports[0].hours_done
    with pytest.raises(BusinessRuleError):
        UpdateDailyReportUseCase(factory_for(s)).execute(
            UpdateDailyReportRequest(s.reports[0].id, hours_done=11),
            s.trainer_user,
        )
    assert s.reports[0].hours_done == original


def test_trainer_cannot_update_after_completion():
    s = scenario(completed=True, report_hours=10)
    with pytest.raises(AuthorizationError):
        UpdateDailyReportUseCase(factory_for(s)).execute(
            UpdateDailyReportRequest(s.reports[0].id, hours_done=9),
            s.trainer_user,
        )


def test_trainer_can_delete_owned_report_before_completion():
    s = scenario(report_hours=3)
    progress = DeleteDailyReportUseCase(factory_for(s)).execute(
        s.reports[0].id,
        s.trainer_user,
    )
    assert s.uow.daily_report_repository.deleted == [s.reports[0].id]
    assert progress.status is CourseStatus.NOT_STARTED


def test_list_scope_for_trainer_and_trainee_and_manager():
    s = scenario(report_hours=3)
    trainee = User("U-T", "trainee", "hash", Role.TRAINEE, "T001")
    trainer_reports = ListDailyReportsUseCase(factory_for(s)).execute(s.trainer_user)
    trainee_reports = ListDailyReportsUseCase(factory_for(s)).execute(trainee)
    manager_reports = ListDailyReportsUseCase(factory_for(s)).execute(s.manager)
    assert trainer_reports == s.reports
    assert trainee_reports == s.reports
    assert manager_reports == s.reports


def test_trainee_outside_enrollment_scope_is_rejected():
    s = scenario(report_hours=3)
    trainee = User("U-T2", "trainee2", "hash", Role.TRAINEE, "T002")
    with pytest.raises(AuthorizationError):
        ListDailyReportsUseCase(factory_for(s)).execute(trainee, course_id="C001")
