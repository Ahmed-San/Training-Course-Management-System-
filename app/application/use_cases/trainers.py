from __future__ import annotations

from app.application.dto.requests import CreateTrainerRequest
from app.application.use_cases.common import require_manager
from app.domain.entities.trainer import Trainer


class CreateTrainerUseCase:
    def __init__(self, uow_factory) -> None: self._uow_factory = uow_factory
    def execute(self, request: CreateTrainerRequest, current_user=None) -> Trainer:
        require_manager(current_user)
        with self._uow_factory() as uow:
            trainer = Trainer(id=request.id, name=request.name, age=request.age, phone=request.phone, email=request.email, category=request.category, training_method=request.training_method)
            return uow.trainer_repository.add(trainer)


class UpdateTrainerUseCase:
    def __init__(self, uow_factory) -> None: self._uow_factory = uow_factory
    def execute(self, trainer_id: str, current_user, *, name=None, age=None, phone=None, email=None, category=None, training_method=None) -> Trainer:
        require_manager(current_user)
        with self._uow_factory() as uow:
            trainer = uow.trainer_repository.get_required(trainer_id)
            trainer.update_personal_info(name=name, age=age, phone=phone, email=email)
            if category is not None: trainer.change_category(category)
            if training_method is not None: trainer.change_training_method(training_method)
            return uow.trainer_repository.update(trainer)


class ViewTrainerUseCase:
    def __init__(self, uow_factory) -> None: self._uow_factory = uow_factory
    def execute(self, trainer_id: str, current_user) -> Trainer:
        require_manager(current_user)
        with self._uow_factory() as uow:
            return uow.trainer_repository.get_required(trainer_id)


class ListTrainersUseCase:
    def __init__(self, uow_factory) -> None: self._uow_factory = uow_factory
    def execute(self, current_user) -> list[Trainer]:
        require_manager(current_user)
        with self._uow_factory() as uow:
            return uow.trainer_repository.get_all()
