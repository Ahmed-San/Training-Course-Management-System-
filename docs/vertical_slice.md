# TCMS V2 — First Vertical Slice

The team must prove the architecture with one small end-to-end workflow before implementing the whole system.

## Slice

```text
Create Trainee
   ↓
Trainee Use Case
   ↓
Repository[Trainee]
   ↓
Json Unit of Work
   ↓
database.json
   ↓
CLI success message
```

## Why this slice

It crosses Domain, Infrastructure, Application, and Presentation without depending on the hardest business rules. If this slice is clean, the team has evidence that dependency injection, repositories, serialization, UoW, and CLI integration are wired correctly.

## Required proof

- Valid trainee is persisted.
- Duplicate ID is rejected.
- JSON remains valid.
- CLI does not open the JSON file directly.
- Use case does not import presentation modules.
- Domain does not import infrastructure.
- Test runs against isolated data where appropriate.
