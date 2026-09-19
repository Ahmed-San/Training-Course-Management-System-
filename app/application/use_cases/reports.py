from __future__ import annotations

from datetime import datetime, timezone

from app.application.dto.requests import CreateDailyReportRequest, UpdateDailyReportRequest
from app.application.services.course_progress import CourseProgress, calculate_course_progress
from app.application.use_cases.common import require_authenticated
from app.domain.entities.daily_report import DailyReport
from app.domain.enums import CourseStatus, EnrollmentStatus, Role, TrainingMethod
from app.domain.exceptions import AuthorizationError, BusinessRuleError


class _ReportWorkflow:
    """Shared application rules for daily report workflows."""

    def __init__(self, uow_factory, authorization=None) -> None:
        # ``authorization`` is accepted for compatibility with the existing
        # bootstrap contract; M4 scope rules are enforced explicitly below.
        self._uow_factory = uow_factory
        self._authorization = authorization

    @staticmethod
    def _trainer_id(current_user) -> str:
        user = require_authenticated(current_user)
        if user.role is not Role.TRAINER or not user.profile_id:
            raise AuthorizationError("Daily report operations are available to trainers only.")
        return user.profile_id

    def _require_trainer_scope(self, uow, current_user, course_id: str) -> str:
        trainer_id = self._trainer_id(current_user)
        trainer = uow.trainer_repository.get_required(trainer_id)
        if trainer.training_method is not TrainingMethod.ONSITE:
            raise AuthorizationError("Remote trainers cannot mutate daily reports.")
        if not uow.assignment_repository.is_trainer_assigned_to_course(trainer_id, course_id):
            raise AuthorizationError("Trainer is not assigned to this course.")
        return trainer_id

    @staticmethod
    def _calculate_progress(uow, course) -> CourseProgress:
        reports = uow.daily_report_repository.get_by_course(course.id)
        return calculate_course_progress(
            total_hours=course.total_hours,
            reported_hours=reports,
        )

    @staticmethod
    def _complete_active_enrollments(uow, course, progress: CourseProgress) -> None:
        if progress.status is not CourseStatus.COMPLETED:
            return

        completed_at = datetime.now(timezone.utc)
        for enrollment in uow.enrollment_repository.get_by_course(course.id):
            if enrollment.status is EnrollmentStatus.ACTIVE:
                enrollment.complete(completed_at)
                uow.enrollment_repository.update(enrollment)


class CreateDailyReportUseCase(_ReportWorkflow):
    def execute(
        self,
        request: CreateDailyReportRequest,
        current_user,
    ) -> tuple[DailyReport, CourseProgress]:
        with self._uow_factory() as uow:
            trainer_id = self._require_trainer_scope(
                uow, current_user, request.course_id
            )
            course = uow.course_repository.get_required(request.course_id)
            progress = self._calculate_progress(uow, course)

            if progress.status is CourseStatus.COMPLETED:
                raise BusinessRuleError("The course is already completed.")
            if request.hours_done <= 0:
                raise BusinessRuleError("Reported hours must be greater than zero.")
            if request.hours_done > progress.remaining_hours:
                raise BusinessRuleError("Reported hours exceed the remaining course hours.")

            if (
                uow.daily_report_repository.get_by_course_trainer_date(
                    request.course_id,
                    trainer_id,
                    request.report_date,
                )
                is not None
            ):
                raise BusinessRuleError(
                    "A report already exists for this course, trainer, and date."
                )

            now = datetime.now(timezone.utc)
            report = DailyReport(
                id=f"RPT-{request.course_id}-{trainer_id}-{request.report_date.isoformat()}",
                course_id=request.course_id,
                trainer_id=trainer_id,
                report_date=request.report_date,
                hours_done=request.hours_done,
                note=request.note,
                created_at=now,
                updated_at=now,
            )
            saved = uow.daily_report_repository.add(report)
            new_progress = self._calculate_progress(uow, course)
            self._complete_active_enrollments(uow, course, new_progress)
            return saved, new_progress


class UpdateDailyReportUseCase(_ReportWorkflow):
    def execute(
        self,
        request: UpdateDailyReportRequest,
        current_user,
    ) -> tuple[DailyReport, CourseProgress]:
        with self._uow_factory() as uow:
            report = uow.daily_report_repository.get_required(request.report_id)
            trainer_id = self._require_trainer_scope(uow, current_user, report.course_id)

            if report.trainer_id != trainer_id:
                raise AuthorizationError("Trainer can modify only their own reports.")

            course = uow.course_repository.get_required(report.course_id)
            current_progress = self._calculate_progress(uow, course)
            if current_progress.status is CourseStatus.COMPLETED:
                raise AuthorizationError("Completed course reports cannot be modified.")

            other_reports = [
                item
                for item in uow.daily_report_repository.get_by_course(course.id)
                if item.id != report.id
            ]
            remaining_without_current = max(
                course.total_hours
                - sum(item.hours_done for item in other_reports),
                0,
            )

            proposed_hours = (
                request.hours_done if request.hours_done is not None else report.hours_done
            )
            if proposed_hours <= 0:
                raise BusinessRuleError("Reported hours must be greater than zero.")
            if proposed_hours > remaining_without_current:
                raise BusinessRuleError("Updated hours exceed the remaining course hours.")

            new_date = request.report_date if request.report_date is not None else report.report_date
            duplicate = uow.daily_report_repository.get_by_course_trainer_date(
                report.course_id,
                report.trainer_id,
                new_date,
            )
            if duplicate is not None and duplicate.id != report.id:
                raise BusinessRuleError(
                    "A report already exists for this course, trainer, and date."
                )

            report.update(
                hours_done=request.hours_done,
                note=request.note,
                report_date=request.report_date,
            )
            saved = uow.daily_report_repository.update(report)
            new_progress = self._calculate_progress(uow, course)
            self._complete_active_enrollments(uow, course, new_progress)
            return saved, new_progress


class DeleteDailyReportUseCase(_ReportWorkflow):
    def execute(self, report_id: str, current_user) -> CourseProgress:
        with self._uow_factory() as uow:
            report = uow.daily_report_repository.get_required(report_id)
            trainer_id = self._require_trainer_scope(uow, current_user, report.course_id)

            if report.trainer_id != trainer_id:
                raise AuthorizationError("Trainer can delete only their own reports.")

            course = uow.course_repository.get_required(report.course_id)
            if self._calculate_progress(uow, course).status is CourseStatus.COMPLETED:
                raise AuthorizationError("Completed course reports cannot be deleted.")

            uow.daily_report_repository.delete(report_id)
            return self._calculate_progress(uow, course)


class ListDailyReportsUseCase(_ReportWorkflow):
    def execute(
        self,
        current_user,
        *,
        course_id: str | None = None,
    ) -> list[DailyReport]:
        user = require_authenticated(current_user)

        with self._uow_factory() as uow:
            if user.role is Role.COURSE_MANAGER:
                if course_id is None:
                    return uow.daily_report_repository.get_all()
                return uow.daily_report_repository.get_by_course(course_id)

            if user.role is Role.TRAINER and user.profile_id:
                trainer_id = self._trainer_id(user)
                if course_id is None:
                    return uow.daily_report_repository.get_by_trainer(trainer_id)
                if not uow.assignment_repository.is_trainer_assigned_to_course(
                    trainer_id, course_id
                ):
                    raise AuthorizationError("Trainer is not assigned to this course.")
                return [
                    report
                    for report in uow.daily_report_repository.get_by_course(course_id)
                    if report.trainer_id == trainer_id
                ]

            if user.role is Role.TRAINEE and user.profile_id:
                enrolled_course_ids = {
                    enrollment.course_id
                    for enrollment in uow.enrollment_repository.get_by_trainee(user.profile_id)
                }
                if course_id is not None and course_id not in enrolled_course_ids:
                    raise AuthorizationError("Trainee is not enrolled in this course.")

                reports = uow.daily_report_repository.get_all()
                if course_id is not None:
                    return [report for report in reports if report.course_id == course_id]
                return [report for report in reports if report.course_id in enrolled_course_ids]

            raise AuthorizationError("You do not have a valid scope for reports.")
