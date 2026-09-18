from datetime import date, datetime

import pytest

from app.domain.entities.daily_report import DailyReport
from app.domain.exceptions import ValidationError


def make_report(hours: int = 2) -> DailyReport:
    now = datetime.now()

    return DailyReport(
        id="R001",
        course_id="C001",
        trainer_id="T001",
        report_date=date(2026, 9, 18),
        hours_done=hours,
        note="Python training",
        created_at=now,
        updated_at=now,
    )


def test_daily_report_accepts_valid_data():
    report = make_report(3)

    assert report.id == "R001"
    assert report.course_id == "C001"
    assert report.trainer_id == "T001"
    assert report.hours_done == 3


@pytest.mark.parametrize("hours", [0, -1, -5])
def test_daily_report_rejects_non_positive_hours(hours):
    with pytest.raises(ValidationError):
        make_report(hours)


def test_daily_report_rejects_empty_course_id():
    now = datetime.now()

    with pytest.raises(ValidationError):
        DailyReport(
            id="R001",
            course_id="",
            trainer_id="T001",
            report_date=date(2026, 9, 18),
            hours_done=2,
            note="Training",
            created_at=now,
            updated_at=now,
        )

    from app.application.services.course_progress import (
    calculate_course_progress,
)
from app.domain.enums import CourseStatus


def test_progress_not_started_when_no_reports():
    progress = calculate_course_progress(
        total_hours=10,
        reported_hours=[],
    )

    assert progress.completed_hours == 0
    assert progress.remaining_hours == 10
    assert progress.status is CourseStatus.NOT_STARTED


def test_progress_is_in_progress():
    progress = calculate_course_progress(
        total_hours=10,
        reported_hours=[3, 2],
    )

    assert progress.completed_hours == 5
    assert progress.remaining_hours == 5
    assert progress.status is CourseStatus.IN_PROGRESS


def test_progress_is_completed():
    progress = calculate_course_progress(
        total_hours=10,
        reported_hours=[5, 5],
    )

    assert progress.completed_hours == 10
    assert progress.remaining_hours == 0
    assert progress.status is CourseStatus.COMPLETED


def test_progress_never_has_negative_remaining_hours():
    progress = calculate_course_progress(
        total_hours=10,
        reported_hours=[6, 6],
    )

    assert progress.completed_hours == 12
    assert progress.remaining_hours == 0
    assert progress.status is CourseStatus.COMPLETED