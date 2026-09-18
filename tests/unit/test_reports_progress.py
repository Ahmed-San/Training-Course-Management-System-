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