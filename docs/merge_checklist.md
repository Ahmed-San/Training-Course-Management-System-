# TCMS V2 — PR / Merge Checklist

Before merging any feature branch:

- [ ] Branch contains one coherent responsibility.
- [ ] No unrelated formatting sweep.
- [ ] No changes to another member's layer without coordination.
- [ ] No new dependency unless explicitly approved.
- [ ] No business logic in CLI.
- [ ] No file I/O in Domain/Application.
- [ ] No duplicated generic CRUD.
- [ ] No magic strings for enum concepts.
- [ ] Type hints are present on important public methods.
- [ ] Tests added/updated for important behavior.
- [ ] Existing tests pass.
- [ ] `python -m compileall -q app main.py` passes.
- [ ] Git diff reviewed manually.
- [ ] Commit message follows project convention.
- [ ] Another member reviewed the PR.

## Commands

```bash
python -m pytest -q
python -m compileall -q app main.py
git status
git diff --check
```
