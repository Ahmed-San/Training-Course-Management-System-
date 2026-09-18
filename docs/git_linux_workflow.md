# Git, GitHub and Linux Workflow

## Git initialization

```bash
git init -b main
git status
git add .
git commit -m "chore: initialize TCMS foundation"
```

## Remote and push

```bash
git remote add origin <GITHUB_REPOSITORY_URL>
git push -u origin main
```

## Feature branch

```bash
git switch -c feature/<name>
git status
git add <files>
git commit -m "feat(scope): clear message"
git push -u origin feature/<name>
```

No developer should push feature work directly to `main` during the team phase.

## Linux setup

```bash
pwd
ls -la
find app -type f | sort
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest -q
python main.py
```

## Evidence rule

Capture screenshots only after the command completes successfully. Keep terminal evidence readable: command, relevant output, and current path should be visible where possible.
