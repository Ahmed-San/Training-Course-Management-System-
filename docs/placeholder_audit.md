# TCMS V2 — Placeholder Audit

This audit records which files are foundations, which are extension points, and which are intentionally left to feature developers.

## Foundation already implemented

- Domain base entities and shared person model.
- Domain enums, roles, validation, exceptions.
- Repository contracts.
- JSON database and serializer.
- Generic JSON repository.
- Unit of Work implementation.
- Settings.
- Password hashing foundation.
- Logging foundation.
- Course-progress calculation foundation.
- Authorization primitives.
- Session foundation.
- Composition root foundation.

## Feature placeholders — do not pre-implement

| Path | Status | Owner | Reason |
|---|---|---|---|
| `app/application/dto/requests.py` | extension point | M3 | DTOs should follow actual use-case boundaries |
| `app/application/use_cases/auth.py` | placeholder | M3 | authentication workflow |
| `app/application/use_cases/trainees.py` | placeholder | M3 | trainee workflows |
| `app/application/use_cases/trainers.py` | placeholder | M3 | trainer workflows |
| `app/application/use_cases/courses.py` | placeholder | M3 | course workflows |
| `app/application/use_cases/enrollments.py` | placeholder | M3 | enrollment lifecycle |
| `app/application/use_cases/assignments.py` | placeholder | M3 | assignment workflows |
| `app/application/use_cases/reports.py` | placeholder | M3 | report transaction workflow |
| `app/application/use_cases/evaluations.py` | placeholder | M3 | evaluation lifecycle/locking |
| `app/presentation/cli/app.py` | placeholder | M4 | CLI lifecycle |
| `app/presentation/cli/input.py` | placeholder | M4 | input boundary |
| `app/presentation/cli/display.py` | placeholder | M4 | presentation formatting |
| `app/presentation/cli/menus/*` | empty | M4 | role menus |
| `tests/integration/*` | empty | M5 | feature integration scenarios |

## Important boundary

The existence of a placeholder does not mean its architecture is undecided. The approved Technical Design already defines its responsibility. The implementation owner should implement inside that responsibility rather than expanding the layer.
