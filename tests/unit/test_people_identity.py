import pytest
from app.domain.entities.trainee import Trainee
from app.domain.entities.trainer import Trainer
from app.domain.entities.user import User
from app.domain.enums import Category, TrainingMethod, Role
from app.domain.exceptions import ValidationError, DuplicateError, AuthenticationError, NotFoundError
from app.domain.repositories.base_repository import BaseRepository
from app.domain.repositories.user_repository import UserRepository
from app.application.dto.requests import CreateTraineeRequest, CreateTrainerRequest, LoginRequest
from app.application.use_cases.trainees import CreateTraineeUseCase, ViewTraineeUseCase
from app.application.use_cases.trainers import CreateTrainerUseCase
from app.application.use_cases.auth import LoginUseCase
from app.infrastructure.auth.password_hasher import PasswordHasher


# In-Memory Fakes for pure test isolation
class InMemoryRepository(BaseRepository):
    def __init__(self):
        self._items = {}

    def add(self, entity):
        if entity.id in self._items:
            raise DuplicateError(f"Entity {entity.id} already exists.")
        self._items[entity.id] = entity
        return entity

    def get_by_id(self, entity_id: str):
        return self._items.get(entity_id)

    def get_required(self, entity_id: str):
        item = self.get_by_id(entity_id)
        if item is None:
            raise NotFoundError(f"Entity {entity_id} not found.")
        return item

    def get_all(self):
        return list(self._items.values())

    def update(self, entity):
        self._items[entity.id] = entity
        return entity

    def delete(self, entity_id: str):
        if entity_id in self._items:
            del self._items[entity_id]

    def exists(self, entity_id: str) -> bool:
        return entity_id in self._items

    def count(self) -> int:
        return len(self._items)


class InMemoryUserRepository(InMemoryRepository, UserRepository):
    def get_by_username(self, username: str) -> User | None:
        for user in self._items.values():
            if user.username == username:
                return user
        return None


class FakeUnitOfWork:
    def __init__(self, user_repo=None, trainee_repo=None):
        self.user_repository = user_repo if user_repo is not None else InMemoryUserRepository()
        self.trainee_repository = trainee_repo if trainee_repo is not None else InMemoryRepository()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


# --- 1. Domain Entities Tests ---
def test_trainee_creation_and_category_change():
    trainee = Trainee(
        id="T001",
        name="Taha IT",
        age=23,
        phone="+967770000000",
        email="taha@example.com",
        category=Category.A,
    )
    assert trainee.category == Category.A
    trainee.change_category(Category.B)
    assert trainee.category == Category.B


def test_trainee_invalid_data():
    with pytest.raises(ValidationError):
        Trainee(
            id="T002",
            name="",
            age=25,
            phone="+967770000000",
            email="invalid_email",
            category=Category.A,
        )


def test_trainer_creation_and_method_change():
    trainer = Trainer(
        id="TR001",
        name="Ahmed Trainer",
        age=30,
        phone="+967771111111",
        email="trainer@example.com",
        category=Category.A,
        training_method=TrainingMethod.ONSITE,
    )
    assert trainer.training_method == TrainingMethod.ONSITE
    trainer.change_training_method(TrainingMethod.REMOTE)
    assert trainer.training_method == TrainingMethod.REMOTE


# --- 2. Use Cases & Business Rules Tests ---
def test_create_trainee_rejects_duplicate_id():
    uow = FakeUnitOfWork()
    uow_factory = lambda: uow
    use_case = CreateTraineeUseCase(uow_factory)
    req = CreateTraineeRequest(
        id="T100",
        name="Student 1",
        age=20,
        phone="+967772222222",
        email="student1@test.com",
        category=Category.A,
    )
    manager = User(id="M001", username="mgr", password_hash="pwd", role=Role.COURSE_MANAGER, profile_id="M001")
    use_case.execute(req, current_user=manager)

    with pytest.raises(DuplicateError):
        use_case.execute(req, current_user=manager)


def test_login_successful():
    user_repo = InMemoryUserRepository()
    hasher = PasswordHasher()
    hashed_pwd = hasher.hash("secret123")

    user = User(
        id="U001",
        username="taha_admin",
        password_hash=hashed_pwd,
        role=Role.COURSE_MANAGER,
        profile_id="M001",
    )
    user_repo.add(user)

    uow = FakeUnitOfWork(user_repo=user_repo)
    login_uc = LoginUseCase(lambda: uow, hasher)
    logged_in_user = login_uc.execute(LoginRequest(username="taha_admin", password="secret123"))
    assert logged_in_user.id == "U001"
    assert logged_in_user.username == "taha_admin"


def test_login_wrong_password_raises_authentication_error():
    user_repo = InMemoryUserRepository()
    hasher = PasswordHasher()
    hashed_pwd = hasher.hash("secret123")

    user = User(
        id="U002",
        username="trainer_user",
        password_hash=hashed_pwd,
        role=Role.TRAINER,
        profile_id="TR001",
    )
    user_repo.add(user)

    uow = FakeUnitOfWork(user_repo=user_repo)
    login_uc = LoginUseCase(lambda: uow, hasher)
    with pytest.raises(AuthenticationError):
        login_uc.execute(LoginRequest(username="trainer_user", password="wrongpassword"))


def test_login_non_existent_user_raises_authentication_error():
    user_repo = InMemoryUserRepository()
    hasher = PasswordHasher()
    uow = FakeUnitOfWork(user_repo=user_repo)
    login_uc = LoginUseCase(lambda: uow, hasher)

    with pytest.raises(AuthenticationError):
        login_uc.execute(LoginRequest(username="ghost_user", password="anypassword"))
