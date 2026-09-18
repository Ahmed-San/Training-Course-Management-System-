from __future__ import annotations

from app.application.dto.requests import CreateTraineeRequest
from app.application.use_cases.common import require_manager
from app.domain.entities.trainee import Trainee
from app.domain.exceptions import NotFoundError


class CreateTraineeUseCase:
    def __init__(self, uow_factory) -> None:
        self._uow_factory = uow_factory

    def execute(self, request: CreateTraineeRequest, current_user=None) -> Trainee:
        require_manager(current_user)
        with self._uow_factory() as uow:
            trainee = Trainee(id=request.id, name=request.name, age=request.age, phone=request.phone, email=request.email, category=request.category)
            return uow.trainee_repository.add(trainee)


class UpdateTraineeUseCase:
    def __init__(self, uow_factory) -> None: self._uow_factory = uow_factory
    def execute(self, trainee_id: str, current_user, *, name=None, age=None, phone=None, email=None, category=None) -> Trainee:
        require_manager(current_user)
        with self._uow_factory() as uow:
            trainee = uow.trainee_repository.get_required(trainee_id)
            trainee.update_personal_info(name=name, age=age, phone=phone, email=email)
            if category is not None:
                trainee.change_category(category)
            return uow.trainee_repository.update(trainee)


class ViewTraineeUseCase:
    def __init__(self, uow_factory) -> None: self._uow_factory = uow_factory
    def execute(self, trainee_id: str, current_user) -> Trainee:
        with self._uow_factory() as uow:
            require_manager(current_user)
            return uow.trainee_repository.get_required(trainee_id)


class ListTraineesUseCase:
    def __init__(self, uow_factory) -> None: self._uow_factory = uow_factory
    def execute(self, current_user) -> list[Trainee]:
        require_manager(current_user)
        with self._uow_factory() as uow:
            return uow.trainee_repository.get_all()

