from __future__ import annotations

from datetime import date

from app.domain.entities.daily_report import DailyReport
from app.domain.repositories.daily_report_repository import DailyReportRepository
from app.infrastructure.persistence.json_repository import JsonRepository


class JsonDailyReportRepository(JsonRepository[DailyReport], DailyReportRepository):
    """JSON adapter providing only daily-report-specific queries."""

    def get_by_course(self, course_id: str) -> list[DailyReport]:
        return [report for report in self.get_all() if report.course_id == course_id]

    def get_by_trainer(self, trainer_id: str) -> list[DailyReport]:
        return [report for report in self.get_all() if report.trainer_id == trainer_id]

    def get_by_course_trainer_date(
        self,
        course_id: str,
        trainer_id: str,
        report_date: date,
    ) -> DailyReport | None:
        for report in self.get_all():
            if (
                report.course_id == course_id
                and report.trainer_id == trainer_id
                and report.report_date == report_date
            ):
                return report
        return None
