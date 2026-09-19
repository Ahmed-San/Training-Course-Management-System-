from __future__ import annotations

from abc import abstractmethod
from datetime import date

from app.domain.entities.daily_report import DailyReport
from app.domain.repositories.base_repository import Repository


class DailyReportRepository(Repository[DailyReport]):
    """Queries specific to daily reports."""

    @abstractmethod
    def get_by_course(self, course_id: str) -> list[DailyReport]:
        raise NotImplementedError

    @abstractmethod
    def get_by_trainer(self, trainer_id: str) -> list[DailyReport]:
        raise NotImplementedError

    @abstractmethod
    def get_by_course_trainer_date(
        self,
        course_id: str,
        trainer_id: str,
        report_date: date,
    ) -> DailyReport | None:
        raise NotImplementedError
