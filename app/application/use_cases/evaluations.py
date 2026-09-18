from __future__ import annotations

from datetime import datetime, timezone

from app.application.dto.requests import CreateEvaluationRequest, UpdateEvaluationRequest
from app.application.use_cases.common import require_authenticated
from app.domain.entities.evaluation import Evaluation
from app.domain.enums import EnrollmentStatus, Role, TrainingMethod
from app.domain.exceptions import (
    AuthorizationError,
    BusinessRuleError,
    DuplicateError,
    ValidationError,
)


class _EvaluationScope:
    """Shared resource-scope checks for evaluation workflows."""

    def __init__(self, uow_factory) -> None:
        self._uow_factory = uow_factory

    @staticmethod
    def _manager_identity(user) -> str:
        return user.profile_id or user.id

    def _require_manager_scope(self, uow, user, course_id: str) -> None:
        course = uow.course_repository.get_required(course_id)
        if course.manager_id != self._manager_identity(user):
            raise AuthorizationError("مدير الدورة خارج نطاق هذه الدورة.")

    def _require_trainer_scope(
        self,
        uow,
        user,
        course_id: str,
        trainee_id: str,
        *,
        mutation: bool,
    ) -> str:
        if user.role is not Role.TRAINER or not user.profile_id:
            raise AuthorizationError("هذه العملية متاحة للمدرب ضمن نطاقه فقط.")

        trainer_id = user.profile_id
        trainer = uow.trainer_repository.get_required(trainer_id)
        if mutation and trainer.training_method is not TrainingMethod.ONSITE:
            raise AuthorizationError("المدرب عن بُعد لا يستطيع إنشاء أو تعديل التقييمات.")

        if not uow.assignment_repository.is_trainer_assigned_to_course(trainer_id, course_id):
            raise AuthorizationError("المدرب غير مسند إلى هذه الدورة.")

        if not uow.assignment_repository.is_trainer_assigned_to_trainee(
            trainer_id, trainee_id, course_id
        ):
            raise AuthorizationError("المدرب غير مسند إلى هذا المتدرب داخل هذه الدورة.")

        return trainer_id

    def _require_scope(
        self,
        uow,
        user,
        course_id: str,
        trainee_id: str,
        *,
        mutation: bool,
    ) -> str | None:
        if user.role is Role.COURSE_MANAGER:
            self._require_manager_scope(uow, user, course_id)
            return None
        return self._require_trainer_scope(
            uow, user, course_id, trainee_id, mutation=mutation
        )


class CreateEvaluationUseCase(_EvaluationScope):
    def execute(self, request: CreateEvaluationRequest, current_user) -> Evaluation:
        user = require_authenticated(current_user)
        if user.role is not Role.TRAINER:
            raise AuthorizationError("إنشاء التقييم متاح للمدرب فقط.")

        with self._uow_factory() as uow:
            enrollment = uow.enrollment_repository.get_required(request.enrollment_id)
            if enrollment.status is not EnrollmentStatus.ACTIVE:
                raise BusinessRuleError("لا يمكن إنشاء تقييم لتسجيل مكتمل.")

            self._require_trainer_scope(
                uow,
                user,
                enrollment.course_id,
                enrollment.trainee_id,
                mutation=True,
            )

            if uow.evaluation_repository.get_by_enrollment(enrollment.id) is not None:
                raise DuplicateError("يوجد تقييم مسبق لهذا التسجيل.")

            now = datetime.now(timezone.utc)
            evaluation = Evaluation(
                id=f"EVA-{enrollment.id}",
                enrollment_id=enrollment.id,
                trainer_id=user.profile_id,
                grade=request.grade,
                created_at=now,
                updated_at=now,
            )
            return uow.evaluation_repository.add(evaluation)


class UpdateEvaluationUseCase(_EvaluationScope):
    def execute(self, request: UpdateEvaluationRequest, current_user) -> Evaluation:
        user = require_authenticated(current_user)

        with self._uow_factory() as uow:
            evaluation = uow.evaluation_repository.get_required(request.evaluation_id)
            enrollment = uow.enrollment_repository.get_required(evaluation.enrollment_id)

            if user.role is Role.COURSE_MANAGER:
                self._require_manager_scope(uow, user, enrollment.course_id)
            elif user.role is Role.TRAINER:
                trainer_id = self._require_trainer_scope(
                    uow,
                    user,
                    enrollment.course_id,
                    enrollment.trainee_id,
                    mutation=True,
                )
                if evaluation.trainer_id != trainer_id:
                    raise AuthorizationError("يمكن للمدرب تعديل تقييماته التي أنشأها فقط.")
                if enrollment.status is not EnrollmentStatus.ACTIVE:
                    raise AuthorizationError("لا يمكن للمدرب تعديل التقييم بعد إكمال التسجيل.")
            else:
                raise AuthorizationError("لا تملك صلاحية تعديل التقييم.")

            evaluation.change_grade(request.grade)
            evaluation.updated_at = _next_timestamp(evaluation.updated_at)
            return uow.evaluation_repository.update(evaluation)


class ViewEvaluationUseCase(_EvaluationScope):
    def execute(
        self,
        current_user,
        *,
        evaluation_id: str | None = None,
        enrollment_id: str | None = None,
    ) -> Evaluation | None:
        user = require_authenticated(current_user)
        if not evaluation_id and not enrollment_id:
            raise ValidationError("يجب تحديد رقم التقييم أو رقم التسجيل.")

        with self._uow_factory() as uow:
            evaluation = (
                uow.evaluation_repository.get_required(evaluation_id)
                if evaluation_id
                else uow.evaluation_repository.get_by_enrollment(enrollment_id)
            )
            if evaluation is None:
                return None

            enrollment = uow.enrollment_repository.get_required(evaluation.enrollment_id)

            if user.role is Role.COURSE_MANAGER:
                self._require_manager_scope(uow, user, enrollment.course_id)
                return evaluation

            if user.role is Role.TRAINER:
                self._require_trainer_scope(
                    uow,
                    user,
                    enrollment.course_id,
                    enrollment.trainee_id,
                    mutation=False,
                )
                return evaluation

            if user.role is Role.TRAINEE and user.profile_id == enrollment.trainee_id:
                if enrollment.status is not EnrollmentStatus.COMPLETED:
                    raise AuthorizationError("يظهر تقييم المتدرب بعد إكمال التسجيل فقط.")
                return evaluation

            raise AuthorizationError("ليس لديك صلاحية عرض هذا التقييم.")


class ListEvaluationsUseCase(_EvaluationScope):
    def execute(self, current_user) -> list[Evaluation]:
        user = require_authenticated(current_user)

        with self._uow_factory() as uow:
            evaluations = uow.evaluation_repository.get_all()

            if user.role is Role.COURSE_MANAGER:
                managed_course_ids = {
                    course.id
                    for course in uow.course_repository.get_all()
                    if course.manager_id == self._manager_identity(user)
                }
                return [
                    evaluation
                    for evaluation in evaluations
                    if uow.enrollment_repository.get_required(evaluation.enrollment_id).course_id
                    in managed_course_ids
                ]

            if user.role is Role.TRAINER and user.profile_id:
                result: list[Evaluation] = []
                for evaluation in evaluations:
                    enrollment = uow.enrollment_repository.get_required(evaluation.enrollment_id)
                    if not uow.assignment_repository.is_trainer_assigned_to_course(
                        user.profile_id, enrollment.course_id
                    ):
                        continue
                    if not uow.assignment_repository.is_trainer_assigned_to_trainee(
                        user.profile_id,
                        enrollment.trainee_id,
                        enrollment.course_id,
                    ):
                        continue
                    result.append(evaluation)
                return result

            if user.role is Role.TRAINEE and user.profile_id:
                result = []
                for enrollment in uow.enrollment_repository.get_by_trainee(user.profile_id):
                    if enrollment.status is not EnrollmentStatus.COMPLETED:
                        continue
                    evaluation = uow.evaluation_repository.get_by_enrollment(enrollment.id)
                    if evaluation is not None:
                        result.append(evaluation)
                return result

            raise AuthorizationError("ليس لديك نطاق صالح لعرض التقييمات.")


def _next_timestamp(previous: datetime) -> datetime:
    tz = previous.tzinfo
    return datetime.now(tz) if tz is not None else datetime.now()
