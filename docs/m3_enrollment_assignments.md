# M3 — Enrollment and Assignments

## Scope

M3 owns the relationship between trainees, courses, and trainers:

- `Enrollment` connects a trainee to a course.
- `CourseTrainerAssignment` connects a trainer to a course.
- `TrainerTraineeAssignment` connects a course trainer to an enrolled trainee.

The implementation follows the existing Clean Architecture boundaries:

```text
Use Cases → Repository Contracts → JSON Repository Adapters → JsonUnitOfWork
```

## Business rules

1. A trainee may have only one `ACTIVE` enrollment at a time.
2. An enrollment can transition to `COMPLETED` only once.
3. A course trainer assignment requires an existing course and trainer.
4. A trainer-to-trainee assignment requires:
   - an existing course, trainer, and trainee;
   - a trainer assignment for the course;
   - an enrollment for the trainee in the same course;
   - no duplicate assignment.
5. Enrollment and assignment mutations require a course manager.
6. Enrollment views are scoped to managers, the owning trainee, or an assigned trainer.

## Implemented surfaces

- Domain entities:
  - `app/domain/entities/enrollment.py`
  - `app/domain/entities/assignments.py`
- Repository contracts:
  - `app/domain/repositories/enrollment_repository.py`
  - `app/domain/repositories/assignment_repository.py`
- Application workflows:
  - `app/application/use_cases/enrollments.py`
  - `app/application/use_cases/assignments.py`
- JSON adapters:
  - `app/infrastructure/persistence/json_enrollment_repository.py`
  - `app/infrastructure/persistence/json_assignment_repository.py`
- Transaction wiring:
  - `app/infrastructure/persistence/json_unit_of_work.py`

## Persistence collections

The adapters use the existing database collections:

```text
enrollments
course_trainer_assignments
trainer_trainee_assignments
```

All repository mutations operate on the UoW working copy and are persisted once
when the UoW exits successfully. Exceptions roll back the working copy.

## Validation evidence

The isolated M3 test file is:

```text
tests/unit/test_enrollment_assignments.py
```

It verifies domain behavior, repository queries, application rules, authorization,
JSON adapter persistence, and UoW integration using temporary database state.

Recommended checks:

```powershell
python -m pytest -q tests/unit/test_enrollment_assignments.py
python -m compileall -q app main.py tests/unit/test_enrollment_assignments.py
git diff --check
```

## Boundary note

M3 does not create or own a DailyReport entity. Enrollment and assignment
workflows therefore depend only on the entities and repository contracts already
available in the project. Course progress and reporting remain separate feature
slices.
