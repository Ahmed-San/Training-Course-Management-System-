from __future__ import annotations

from app.bootstrap import create_container


def main() -> None:
    container = create_container()
    container.logger.info("TCMS foundation initialized")
    print("Training Course Management System")
    print("Foundation initialized successfully.")
    print(f"Database: {container.settings.data_path}")
    print("Feature modules are intentionally left for the implementation phase.")


if __name__ == "__main__":
    main()
