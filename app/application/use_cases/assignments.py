from __future__ import annotations

from app.application.dto.requests import AssignTrainerRequest, AssignTraineeRequest
from app.application.use_cases.common import require_manager
from app.domain.entities.assignments import CourseTrainerAssignment, TrainerTraineeAssignment
from app.domain.exceptions import BusinessRuleError, DuplicateError
from app.domain.enums import Role


class AssignTrainerToCourseUseCase:
    def __init__(self, uow_factory) -> None: self._uow_factory = uow_factory
    def execute(self, request: AssignTrainerRequest, current_user) -> CourseTrainerAssignment:
        require_manager(current_user)
        with self._uow_factory() as uow:
            uow.course_repository.get_required(request.course_id)
            uow.trainer_repository.get_required(request.trainer_id)
            if uow.assignment_repository.is_trainer_assigned_to_course(request.trainer_id, request.course_id):
                raise DuplicateError("Trainer is already assigned to this course.")
            assignment = CourseTrainerAssignment(id=f"CTA-{request.trainer_id}-{request.course_id}", course_id=request.course_id, trainer_id=request.trainer_id)
            return uow.assignment_repository.add(assignment)


class AssignTrainerToTraineeUseCase:
    def __init__(self, uow_factory) -> None: self._uow_factory = uow_factory
    def execute(self, request: AssignTraineeRequest, current_user) -> TrainerTraineeAssignment:
        require_manager(current_user)
        with self._uow_factory() as uow:
            uow.course_repository.get_required(request.course_id)
            uow.trainer_repository.get_required(request.trainer_id)
            uow.trainee_repository.get_required(request.trainee_id)
            if not uow.assignment_repository.is_trainer_assigned_to_course(request.trainer_id, request.course_id):
                raise BusinessRuleError("Trainer must be assigned to the course before being assigned to a trainee.")
            if uow.assignment_repository.is_trainer_assigned_to_trainee(request.trainer_id, request.trainee_id, request.course_id):
                raise DuplicateError("Trainer is already assigned to this trainee in this course.")
            assignment = TrainerTraineeAssignment(id=f"TTA-{request.trainer_id}-{request.trainee_id}-{request.course_id}", course_id=request.course_id, trainer_id=request.trainer_id, trainee_id=request.trainee_id)
            return uow.assignment_repository.add(assignment)


class ListTrainerCourseAssignmentsUseCase:
    def __init__(self, uow_factory) -> None: self._uow_factory = uow_factory
    def execute(self, current_user) -> list[CourseTrainerAssignment | TrainerTraineeAssignment]:
        require_manager(current_user)
        with self._uow_factory() as uow:
            return uow.assignment_repository.get_all()


class ListTrainerTraineesUseCase:
    def __init__(self, uow_factory) -> None: self._uow_factory = uow_factory

    def execute(self, current_user, course_id: str) -> list[TrainerTraineeAssignment]:
        if current_user.role is not Role.TRAINER or not current_user.profile_id:
            from app.domain.exceptions import AuthorizationError
            raise AuthorizationError("Only trainers can use this view.")
        with self._uow_factory() as uow:
            uow.course_repository.get_required(course_id)
            if not uow.assignment_repository.is_trainer_assigned_to_course(current_user.profile_id, course_id):
                from app.domain.exceptions import AuthorizationError
                raise AuthorizationError("Trainer is not assigned to this course.")
            return uow.assignment_repository.get_trainees_by_trainer(current_user.profile_id, course_id)
