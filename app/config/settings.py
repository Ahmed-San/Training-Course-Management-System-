from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Settings:
    """Immutable application paths and environment settings."""

    project_root: Path
    data_path: Path
    log_path: Path
    app_name: str = "Training Course Management System"

    @classmethod
    def from_project_root(cls, project_root: Path) -> "Settings":
        root = project_root.resolve()
        return cls(
            project_root=root,
            data_path=root / "data" / "database.json",
            log_path=root / "logs" / "app.log",
        )


def default_settings() -> Settings:
    root = Path(__file__).resolve().parents[2]
    return Settings.from_project_root(root)
