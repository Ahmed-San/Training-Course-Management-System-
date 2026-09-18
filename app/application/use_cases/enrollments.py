from __future__ import annotations

from datetime import datetime, timezone

from app.application.dto.requests import EnrollTraineeRequest
from app.application.use_cases.common import require_authenticated, require_manager
from app.domain.entities.enrollment import Enrollment
from app.domain.enums import CourseStatus, EnrollmentStatus, Role
from app.domain.exceptions import AuthorizationError, BusinessRuleError


class EnrollTraineeUseCase:
    def __init__(self, uow_factory) -> None: self._uow_factory = uow_factory
    def execute(self, request: EnrollTraineeRequest, current_user) -> Enrollment:
        require_manager(current_user)
        with self._uow_factory() as uow:
            uow.trainee_repository.get_required(request.trainee_id)
            course = uow.course_repository.get_required(request.course_id)
            from app.application.services.course_progress import calculate_course_progress
            progress = calculate_course_progress(
                total_hours=course.total_hours,
                reported_hours=[r.hours_done for r in uow.daily_report_repository.get_by_course(course.id)],
            )
            if progress.status is CourseStatus.COMPLETED:
                raise BusinessRuleError("Cannot enroll a trainee in a completed course.")
            active = uow.enrollment_repository.get_active_by_trainee(request.trainee_id)
            if active is not None:
                raise BusinessRuleError("Trainee already has an active enrollment.")
            enrollment = Enrollment(
                id=f"ENR-{request.trainee_id}-{request.course_id}",
                trainee_id=request.trainee_id,
                course_id=request.course_id,
                status=EnrollmentStatus.ACTIVE,
            )
            return uow.enrollment_repository.add(enrollment)


class CompleteEnrollmentUseCase:
    def __init__(self, uow_factory) -> None: self._uow_factory = uow_factory
    def execute(self, enrollment_id: str, current_user) -> Enrollment:
        require_manager(current_user)
        with self._uow_factory() as uow:
            enrollment = uow.enrollment_repository.get_required(enrollment_id)
            course = uow.course_repository.get_required(enrollment.course_id)
            from app.application.services.course_progress import calculate_course_progress
            progress = calculate_course_progress(
                total_hours=course.total_hours,
                reported_hours=[r.hours_done for r in uow.daily_report_repository.get_by_course(course.id)],
            )
            if progress.status is not CourseStatus.COMPLETED:
                raise BusinessRuleError("Enrollment cannot be completed before the course is completed.")
            enrollment.complete(datetime.now(timezone.utc))
            return uow.enrollment_repository.update(enrollment)


class ViewEnrollmentUseCase:
    def __init__(self, uow_factory) -> None: self._uow_factory = uow_factory
    def execute(self, enrollment_id: str, current_user) -> Enrollment:
        user = require_authenticated(current_user)
        with self._uow_factory() as uow:
            enrollment = uow.enrollment_repository.get_required(enrollment_id)
            if user.role is Role.COURSE_MANAGER: return enrollment
            if user.role is Role.TRAINEE and user.profile_id == enrollment.trainee_id: return enrollment
            if user.role is Role.TRAINER and user.profile_id and uow.assignment_repository.is_trainer_assigned_to_course(user.profile_id, enrollment.course_id): return enrollment
            raise AuthorizationError("You are outside this enrollment scope.")


class ListEnrollmentsUseCase:
    def __init__(self, uow_factory) -> None: self._uow_factory = uow_factory
    def execute(self, current_user) -> list[Enrollment]:
        user = require_authenticated(current_user)
        with self._uow_factory() as uow:
            if user.role is Role.COURSE_MANAGER: return uow.enrollment_repository.get_all()
            if user.role is Role.TRAINEE and user.profile_id: return uow.enrollment_repository.get_by_trainee(user.profile_id)
            if user.role is Role.TRAINER and user.profile_id:
                ids = {a.course_id for a in uow.assignment_repository.get_courses_by_trainer(user.profile_id)}
                return [e for e in uow.enrollment_repository.get_all() if e.course_id in ids]
            return []