# Contributing

## Branches
- `main` is always working. Changes go in through a Pull Request.
- Branch name: `<type>/<short-topic>` with type `feat`, `fix`, `docs`, `test` or `chore`.

## Commits
Format: `<type>: <what changed>`, optionally with the requirement ID.
Example: `feat: add hash chain verification (FR-04)`

## Pull Requests
- One PR per branch into `main`, reviewed by at least one other member, then merged.
- Mention the related FR / scenario (e.g. FR-04, S-01) in the description.
- Changes to `src/trace_engine/contracts/` need agreement from all members.

## Architecture rules (see ARCHITECTURE.md, Section 4)
- Layers: presentation -> application -> domain -> data. A lower layer never imports an upper one.
- Data between layers is passed only as the objects in `contracts/models.py`; no global state.
- Finding codes come only from `contracts/codes.py`.
- Cryptography: only `hashlib` and `cryptography`.

## Setup
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
pytest
```
