# TCMS V2 — Team Execution Plan

**Status:** Approved execution baseline  
**Phase:** Post-Foundation / Pre-feature implementation  
**Team:** 5 developers  
**Target:** One-day delivery  

## 1. Objective

This document converts the approved Technical Design and Foundation Release into an executable team plan. The Foundation is treated as the protected baseline. Feature work starts from this state; developers do not redesign the architecture independently.

## 2. Foundation audit

The following placeholders were reviewed:

- `application/dto/requests.py` — shared DTO location; currently intentionally empty.
- `application/use_cases/*.py` — feature boundaries only; implementation belongs to Member 3.
- `application/services/authorization.py` — shared authorization primitives already exist; feature-specific scope checks remain in use cases.
- `application/services/course_progress.py` — course-progress calculation is already a stable shared service.
- `application/unit_of_work.py` — application contract exists.
- `presentation/cli/app.py`, `input.py`, `display.py` — presentation placeholders; implementation belongs to Member 4.
- `presentation/cli/session.py` — session state foundation exists.
- `bootstrap.py` — composition root exists; feature dependencies will be wired here after contracts stabilize.
- `presentation/cli/menus/` — intentionally empty; role menus are feature work.
- `tests/integration/` — intentionally reserved for integration scenarios.

### Foundation invariants

Do not rewrite or duplicate:

1. `BaseEntity -> Person -> Trainee/Trainer` inheritance.
2. Generic repository contract and JSON persistence model.
3. Serializer conventions.
4. Unit-of-Work transaction boundary.
5. Central authorization service concept.
6. Course progress as a derived value from reports.
7. Enrollment as the link between trainee and course.
8. Evaluation linked to enrollment.
9. One JSON database document.
10. No runtime third-party dependencies.

## 3. Dependency graph

```text
                    FOUNDATION
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
       DOMAIN      INFRASTRUCTURE   APP CONTRACTS
          │             │             │
          └─────────────┼─────────────┘
                        ▼
                   APPLICATION
                        │
                        ▼
                   PRESENTATION
                        │
                        ▼
                  INTEGRATION
                        │
                        ▼
                    FINAL DEMO
```

The practical dependency order is:

```text
Member 1 Domain contracts
        ↓
Member 2 Infrastructure implementation
        ↓
Member 3 Application use cases
        ↓
Member 4 CLI integration
        ↓
Member 5 integration/QA gates throughout
```

Members can work in parallel where contracts already exist, but merges follow the dependency order.

## 4. Team allocation

### Member 1 — Domain Engineer

**Owns:** `app/domain/**`

Tasks:

- Implement and validate all domain entities not already present in Foundation.
- Ensure entity invariants are small, deterministic, and free of I/O.
- Complete repository interfaces only where the approved design requires them.
- Review relationship fields and enum usage.
- Provide stable constructors and methods for Members 2–4.

**Must not:**

- Access JSON.
- Add CLI code.
- Put authorization decisions into entities.
- Add unnecessary patterns.

**Deliverable:** Domain layer complete and importable with focused unit tests.

### Member 2 — Infrastructure Engineer

**Owns:** `app/infrastructure/**`

Tasks:

- Finalize generic JSON repository implementation against Domain contracts.
- Implement specialized repository queries required by Application.
- Finalize Unit of Work repository exposure.
- Finalize password hashing and logging infrastructure.
- Add storage-focused tests.

**Must not:**

- Encode trainee/trainer business rules in repositories.
- Access CLI/session state.
- Create duplicate repository CRUD implementations.

**Deliverable:** Infrastructure can persist and query every Domain entity required by Application.

### Member 3 — Application Engineer

**Owns:** `app/application/**`

Tasks:

- Implement request DTOs where boundary separation is useful.
- Implement use cases for authentication, trainees, trainers, courses, enrollment, assignments, reports, and evaluations.
- Implement business authorization and scope rules.
- Use `CourseProgress` for report-driven progress.
- Use Unit of Work for multi-entity changes.
- Return domain/application results suitable for CLI display without printing from use cases.

**Must not:**

- Open files directly.
- Print CLI menus.
- Put persistence details into use cases.
- duplicate repository CRUD.

**Deliverable:** Complete application workflow independent of CLI presentation.

### Member 4 — Presentation Engineer

**Owns:** `app/presentation/**`

Tasks:

- Implement CLI app lifecycle.
- Implement input and display helpers.
- Implement session integration.
- Implement manager/trainer/trainee menus.
- Connect menu actions to Application use cases through injected dependencies.
- Provide clear success/error messages.

**Must not:**

- Implement business authorization as the only protection.
- Read/write `database.json` directly.
- Recalculate course progress locally.

**Deliverable:** Usable role-based CLI over the completed Application layer.

### Member 5 — QA / Integration / Release Engineer

**Owns:** `tests/**`, `docs/**`, `screenshots/**`, `README.md`

Tasks from hour 1:

- Convert acceptance scenarios into test cases.
- Maintain integration test fixtures/isolation.
- Review every PR for scope, tests, and architecture boundaries.
- Manage merge order and GitHub integration.
- Run Linux verification.
- Maintain screenshots/evidence log.
- Run final end-to-end demo and release checklist.

**Must not:**

- Become a second implementation owner for another layer.
- Fix feature logic silently inside tests.

## 5. File ownership matrix

| Area | Owner | Review partner |
|---|---|---|
| `app/domain/**` | M1 | M3 |
| `app/infrastructure/**` | M2 | M1 |
| `app/application/**` | M3 | M1 + M2 |
| `app/presentation/**` | M4 | M3 |
| `tests/unit/**` | M5 | Layer owner |
| `tests/integration/**` | M5 | M3 + M2 |
| `docs/**` | M5 | All |
| `screenshots/**` | M5 | All |
| `README.md` | M5 | All |
| `main.py` | M5 | M3 + M4 |
| `app/bootstrap.py` | M5 | M2 + M3 + M4 |

Shared files are controlled files. Do not let multiple branches modify them casually.

## 6. Branch model

```text
main
 ├── feature/domain
 ├── feature/infrastructure
 ├── feature/application
 ├── feature/cli
 └── feature/testing-docs
```

Rules:

- No direct feature work on `main`.
- One logical responsibility per commit.
- Pull/rebase before opening a PR if the team workflow requires it.
- Every PR must pass tests before merge.
- Member 5 coordinates merges; layer owners approve technical changes.

## 7. Merge order

### Gate 0 — Foundation

Already complete.

Acceptance:

```text
pytest: 11 passed
compileall: pass
```

### Gate 1 — Domain

Merge `feature/domain` first.

Required before merge:

- Entities import correctly.
- Enums are used instead of magic strings.
- Domain has no infrastructure imports.
- Unit tests pass.

### Gate 2 — Infrastructure

Merge `feature/infrastructure` after Domain.

Required before merge:

- Generic repository works with every implemented entity.
- Specialized queries exist only where required.
- UoW supports atomic multi-collection workflows.
- Serializer round trips all supported types.
- No business rules in persistence.

### Gate 3 — Application

Merge `feature/application` after Domain + Infrastructure.

Required before merge:

- Authentication works.
- CRUD workflows work.
- Enrollment lifecycle works.
- Authorization scope works.
- Report workflow updates progress.
- Completion updates enrollment state.
- Evaluation locking rules work.

### Gate 4 — CLI

Merge `feature/cli` after Application.

Required before merge:

- Login works.
- Correct role menu appears.
- Menu actions call use cases.
- Application exceptions become readable CLI messages.
- CLI contains no business rules or file I/O.

### Gate 5 — Release

`feature/testing-docs` coordinates final integration.

Required:

- Unit + integration tests pass.
- Linux execution passes.
- Git history is understandable.
- Screenshots are complete.
- Final demo passes acceptance scenarios.

## 8. One-day execution schedule

| Time | Activity | Primary owner |
|---|---|---|
| 00:00–00:20 | Clone baseline, create branches, verify environment | All / M5 |
| 00:20–02:00 | Domain implementation | M1 |
| 00:20–02:00 | JSON/repository/UoW implementation | M2 |
| 00:20–01:00 | Test plan + fixtures + acceptance tests skeleton | M5 |
| 01:00–02:30 | Application contract preparation and early use cases | M3 |
| 02:00–03:30 | Domain + infrastructure integration gate | M1/M2/M5 |
| 02:30–05:00 | Application workflows | M3 |
| 04:00–06:00 | CLI implementation against stable use cases | M4 |
| 05:00–07:00 | Integration tests + bug fixing | M5 + M3 |
| 06:00–07:30 | CLI integration + end-to-end tests | M4 + M3 + M5 |
| 07:30–08:30 | Linux/GitHub/screenshots/documentation | M5 |
| 08:30–09:30 | Final demo, bug fixing, release gate | All |

If the available day is shorter, preserve the gates and reduce optional features rather than removing tests or architecture boundaries.

## 9. Contract-first integration points

### Domain → Infrastructure

Infrastructure consumes:

```text
Entity dataclasses
Repository[T] interfaces
Enums
Exceptions
```

### Infrastructure → Application

Application consumes:

```text
Repository objects
UnitOfWork
PasswordHasher
Logger
```

through constructor injection.

### Application → Presentation

Presentation consumes:

```text
Use Case objects
DTOs / request objects
Domain/application exceptions
```

The CLI should not know JSON implementation details.

## 10. Vibe Coding policy per member

### M1

AI may help with repetitive dataclass boilerplate and tests. Human owns entity semantics and invariants.

### M2

AI is appropriate for bounded serializer/repository implementation after interfaces are frozen. Human verifies persistence semantics and rollback.

### M3

AI may generate repetitive CRUD use-case skeletons only after business rules are written by the team. Authorization and lifecycle logic require human review line-by-line.

### M4

AI may generate menu/display boilerplate. Human owns UX flow and confirms menus do not contain business rules.

### M5

AI may generate repetitive tests and README formatting. Human owns acceptance criteria, test meaning, merge decisions, and release approval.

## 11. Required AI prompt boundary

Use prompts with explicit scope:

```text
Implement only [specific file/module] according to the existing project contracts.
Do not modify other layers.
Do not add dependencies.
Do not introduce new design patterns.
Do not change business rules.
Return the complete changed file and explain assumptions briefly.
```

After generation:

```text
Read → compare against contract → run tests → review diff → commit
```

Never:

```text
Generate whole project → accept blindly → debug everything later
```

## 12. Integration checkpoints

Every member reports at checkpoints:

### Checkpoint A — Contracts

```text
What interface do I consume?
What interface do I expose?
What files do I modify?
```

### Checkpoint B — First vertical slice

Target slice:

```text
Create trainee
→ repository
→ JSON
→ use case
→ CLI
```

This proves the architecture before implementing every feature.

### Checkpoint C — Critical workflow

Target:

```text
Create report
→ calculate progress
→ complete course
→ complete enrollment
→ persist atomically
```

### Checkpoint D — Security/authorization

Target:

```text
onsite trainer allowed in scope
remote trainer read-only
trainee sees own completed evaluation only
trainer blocked after completion
manager can correct completed evaluation
```

## 13. Acceptance test ownership

M5 maintains the canonical list:

1. Create trainee.
2. Duplicate trainee ID rejected.
3. Create trainer.
4. Create course.
5. Assign trainer.
6. Assign trainee.
7. Enroll trainee.
8. Prevent second active enrollment.
9. Create daily report.
10. Remaining hours update automatically.
11. Excessive report rejected.
12. Course auto-completes.
13. Enrollment completes.
14. Evaluation created before completion.
15. Authorized onsite trainer edits evaluation before completion.
16. Trainer blocked after completion.
17. Manager corrects completed evaluation.
18. Trainee cannot see incomplete evaluation.
19. Trainee sees own completed evaluation.
20. Unauthorized operations rejected.

## 14. Definition of Ready for a feature

A feature may start only when:

- its entity/data contract is known;
- required repository query is identified;
- business rules are written in plain language;
- authorization scope is defined;
- expected errors are identified;
- acceptance test exists.

## 15. Definition of Done for a feature

A feature is done only when:

- implementation exists in the correct layer;
- no duplicated infrastructure logic was introduced;
- tests cover important rules;
- error behavior is intentional;
- logging is appropriate;
- no unauthorized cross-layer dependency exists;
- code has been reviewed by another member;
- branch passes tests;
- commit message describes the change.

## 16. Foundation-change protocol

The Foundation is protected. A developer may request a change only when one of these is true:

1. A concrete feature cannot be implemented correctly under the current contract.
2. Two approved components have an incompatible contract.
3. A verified defect exists in Foundation behavior.
4. The change removes duplication or ambiguity without broadening scope.

Procedure:

```text
Issue identified
   ↓
Document reason
   ↓
Impact analysis
   ↓
Discuss with affected owners
   ↓
Smallest safe change
   ↓
Add/regress tests
   ↓
Review
   ↓
Merge
```

No foundation rewrite during feature work.

## 17. Known review item before feature merge

The current role-permission foundation is intentionally coarse. `Role.TRAINER` currently has view permissions, while management permissions are enforced by the authorization/service/use-case layer and training method. Before Member 3 implements evaluation/report mutation, the team must confirm that the chosen authorization composition does not accidentally reject legitimate onsite-trainer operations when a permission check is used.

This is a **review item**, not permission to redesign the authorization system. The preferred correction, if needed, is the smallest contract-consistent change with a regression test.

## 18. Final release sequence

```text
Domain merged
   ↓
Infrastructure merged
   ↓
Application merged
   ↓
CLI merged
   ↓
Integration tests
   ↓
Linux verification
   ↓
GitHub final review
   ↓
Screenshots
   ↓
Final demo
   ↓
Release tag / submission
```

## 19. Management rule

The team optimizes for a complete vertical slice, not maximum number of files.

Priority order:

```text
Correctness
→ Business rules
→ Integration
→ Tests
→ CLI usability
→ Documentation/evidence
→ Optional polish
```

Optional polish is dropped before compromising business correctness or test coverage.
