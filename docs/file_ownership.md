# File Ownership and Readiness

This is the **Foundation Release**. It deliberately contains reusable infrastructure and contracts while leaving business-feature implementation to the five developers.

## Built and frozen in the foundation

| Path | Status | Purpose |
|---|---|---|
| `app/domain/entities/base_entity.py` | Built | Common identity |
| `app/domain/entities/person.py` | Built | Shared person fields + validation |
| `app/domain/enums.py` | Built | Categories, roles, permissions, states, grades |
| `app/domain/roles.py` | Built | Role-level permission mapping |
| `app/domain/exceptions.py` | Built | Shared exception taxonomy |
| `app/domain/validation.py` | Built | Shared validation helpers |
| `app/domain/repositories/base_repository.py` | Built | Generic repository contract |
| `app/application/unit_of_work.py` | Built | Application UoW contract |
| `app/application/services/authorization.py` | Built | Role-level authorization helpers |
| `app/application/services/course_progress.py` | Built | Pure course-progress calculation |
| `app/infrastructure/persistence/json_database.py` | Built | One-file JSON persistence |
| `app/infrastructure/persistence/json_repository.py` | Built | Generic CRUD implementation |
| `app/infrastructure/persistence/json_unit_of_work.py` | Built | Atomic working state + commit/rollback |
| `app/infrastructure/persistence/serializer.py` | Built | Entity/dict serialization |
| `app/infrastructure/auth/password_hasher.py` | Built | Password hashing adapter |
| `app/infrastructure/logging/app_logger.py` | Built | Central application logger |
| `app/config/settings.py` | Built | Central immutable settings |
| `app/bootstrap.py` | Built | Composition root / dependency wiring |
| `app/presentation/cli/session.py` | Built | Generic session state |
| `main.py` | Built | Foundation health-check entrypoint |

## Intentionally deferred to developers

| Path | Owner | Expected work |
|---|---|---|
| `app/domain/entities/trainee.py` | Member 1 | Trainee entity |
| `app/domain/entities/trainer.py` | Member 1 | Trainer entity |
| `app/domain/entities/course.py` | Member 1 | Course entity |
| `app/domain/entities/enrollment.py` | Member 1 | Enrollment entity |
| `app/domain/entities/evaluation.py` | Member 1 | Evaluation entity |
| `app/domain/entities/daily_report.py` | Member 1 | DailyReport entity |
| `app/domain/entities/user.py` | Member 1 | User entity |
| `app/domain/entities/assignments.py` | Member 1 | Assignment entities |
| `app/domain/repositories/*.py` except `base_repository.py` | Member 2 | Specialized repository contracts/queries |
| `app/application/use_cases/*.py` | Member 3 | Business workflows |
| `app/application/dto/requests.py` | Member 3 | Only boundary DTOs that are actually needed |
| `app/presentation/cli/app.py` | Member 4 | Final CLI application |
| `app/presentation/cli/input.py` | Member 4 | Input helpers |
| `app/presentation/cli/display.py` | Member 4 | Display/formatting |
| `app/presentation/cli/menus/*.py` | Member 4 | Role menus |
| `tests/integration/*` | Member 5 | End-to-end workflows |

## Important integration rule

Do not casually change frozen foundation contracts while feature work is underway. If a contract must change, document the reason and notify all affected members before merging.
