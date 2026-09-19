# Training Course Management System (TCMS)

Foundation release for a one-day team software-engineering project.

## Stack

- Python 3.11+
- CLI
- Clean Architecture
- One JSON file as persistence
- Python standard library for runtime
- pytest for development tests

## Run

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python main.py
python -m pytest -q
```

### Linux / Git Bash

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python main.py
python -m pytest -q
```

## Data

Persistence is intentionally one document: `data/database.json`. The root is a dictionary and every entity collection is a list of dictionaries.

## Foundation status

The first checkpoint implements the reusable architecture foundation. Feature implementation files are intentionally placeholders so they can be assigned to team members without overlap. See `docs/foundation.md`.

## Documentation

- `docs/technical_design.md` — frozen V2 technical design baseline.
- `docs/foundation.md` — what is implemented now and what is intentionally deferred.
- `docs/vibe_coding_guide.md` — bounded AI/Vibe Coding policy.
- `docs/implementation_checklist.md` — phase status.
- `docs/m3_enrollment_assignments.md` — M3 scope, rules, persistence, and validation evidence.

## Architecture

```text
Presentation / CLI
        ↓
Application / Use Cases + Services + UoW
        ↓
Domain / Entities + Enums + Repository Contracts
        ↓
Infrastructure / JSON + Serializer + Generic Repository + Auth + Logging
        ↓
data/database.json
```

## Execution Management

The approved post-foundation execution plan is documented in `docs/team_execution_plan.md`. Placeholder responsibilities are documented in `docs/placeholder_audit.md`. Use `docs/vertical_slice.md` for the first end-to-end integration slice and `docs/merge_checklist.md` before every merge.

طه محمد محمد ذياب  : branch/feature/m1-people-identity 
احمد عبد الرحمن السنباني : branch/feature/m3-Enrollment-Assignments
عبد الله اسعد محمد سامه : branch/feature/m5_Evaluation_CLI_Integration_Release
فوزي النصيري : branch/feature/m2-Course-Management
خالد اكرم الانسي :branch/feature/m4_Reports_Progress
