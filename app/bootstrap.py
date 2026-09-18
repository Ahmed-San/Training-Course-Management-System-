from __future__ import annotations

from dataclasses import dataclass
from logging import Logger
from pathlib import Path

from app.application.services.authorization import AuthorizationService
from app.config.settings import Settings, default_settings
from app.infrastructure.auth.password_hasher import PasswordHasher
from app.infrastructure.logging.app_logger import configure_logging
from app.infrastructure.persistence.json_database import JsonDatabase
from app.infrastructure.persistence.json_unit_of_work import JsonUnitOfWork


@dataclass(frozen=True, slots=True)
class AppContainer:
    """Central composition root for the foundation infrastructure."""

    settings: Settings
    database: JsonDatabase
    password_hasher: PasswordHasher
    authorization: AuthorizationService
    logger: Logger

    def new_unit_of_work(self) -> JsonUnitOfWork:
        return JsonUnitOfWork(self.database)


def create_container(project_root: Path | None = None) -> AppContainer:
    settings = (
        Settings.from_project_root(project_root)
        if project_root is not None
        else default_settings()
    )
    database = JsonDatabase(settings.data_path)
    database.initialize()
    logger = configure_logging(settings.log_path)
    return AppContainer(
        settings=settings,
        database=database,
        password_hasher=PasswordHasher(),
        authorization=AuthorizationService(),
        logger=logger,
    )
