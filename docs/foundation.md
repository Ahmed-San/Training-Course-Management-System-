# TCMS Foundation Release

This directory contains the first implementation checkpoint. The foundation is deliberately separated from feature work so five developers can work in parallel after the architecture is frozen.

## Implemented now

- `BaseEntity` identity contract.
- `Person` shared person fields and validation.
- Enumerations for roles, permissions, categories, methods, status, grades.
- Shared domain exceptions.
- Shared validation functions.
- Generic repository contract.
- JSON database with one root dictionary and list-of-dictionary collections.
- Generic JSON repository.
- General serializer for dataclasses, Enum, dates and datetimes.
- JSON Unit of Work with single commit and rollback behavior.
- Atomic JSON save.
- Password hashing adapter using the Python standard library.
- Central logger.
- Immutable settings and a composition root (`bootstrap.py`).
- Shared authorization helpers and course-progress calculation.
- Foundation tests.

## Intentionally not implemented

These files are placeholders for the next work phase:

- specialized entities (`Trainee`, `Trainer`, `Course`, etc.)
- specialized repository query contracts/implementations
- use cases
- CLI menus and handlers
- feature-specific integration tests

The placeholders exist only to freeze the architecture and namespace. Their implementations belong to the assigned developer.

## Dependency rule

`domain` must not import infrastructure or CLI code. `application` depends on domain contracts. `infrastructure` implements persistence/auth/logging. `presentation` calls application use cases rather than storage directly.

## Repository rule

Use `Repository[T]` for common CRUD. Add a specialized repository method only when the query is truly domain-specific. Never put business workflows in the generic JSON repository.

## JSON rule

`data/database.json` has one JSON object at the root. Entity collections are keys and each value is a list of dictionaries.

## Team-safe ownership map

| Area | Owner in implementation phase |
|---|---|
| Domain feature entities/contracts | Member 1 |
| Infrastructure feature integration | Member 2 |
| Use cases and application rules | Member 3 |
| CLI presentation | Member 4 |
| Tests, integration, Git/Linux/docs | Member 5 |

Shared foundation files should be changed only by agreement because downstream branches depend on their contracts.
