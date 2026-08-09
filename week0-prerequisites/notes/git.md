# P.7 — Git

## Important commands

git status

git add .

git commit -m "message"

git branch

git checkout branch_name

git push

git pull

git log --oneline

---


## Create a branch
    git branch feature-name
## Switch branches
git checkout feature-name
## Create and switch simultaneously
git checkout -b feature-name
## Why Git is important

- Version control
- Collaboration
- Rollback capability
- Branch management


# P.8 — .gitignore

## Purpose

Tells Git which files should not be tracked.

---

## Common entries

.venv/

__pycache__/

.env

.pytest_cache/

*.pyc

.vscode/