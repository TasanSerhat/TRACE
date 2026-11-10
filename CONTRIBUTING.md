# Contributing Guide

Read this once before you start. Read [ARCHITECTURE.md](ARCHITECTURE.md) for what we are building and
which requirements (FR-xx, NFR-xx, S-xx) belong to you.

## 1. Setup

```powershell
git clone https://github.com/TasanSerhat/TRACE.git
cd TRACE
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
pytest
```

## 2. Branches

We use a simple model: **`main` + short-lived feature branches**. There is no `development` branch.

- `main` is stable and is the default branch. Nobody pushes to it directly; changes arrive only via Pull Request.
- Each member works on one long-running feature branch for their area (see the table in the README).
Do not create extra branches per change; just keep committing to your own branch:
  - `feat/sim-and-integrity` (Member 1)
  - `feat/continuity-and-consistency` (Member 2)
  - `feat/ingestion-and-orchestrator` (Member 3)
- Need something small outside your area (a fix, docs)? Create a short branch from `main`:
  `fix/<topic>`, `docs/<topic>`, `test/<topic>`, `chore/<topic>`.

### Daily workflow
```powershell
git switch feat/your-branch
git pull origin main        # bring in the latest main so you do not drift away
# ... write code, run pytest ...
git add .
git commit -m "feat: add hash chain verification (FR-04)"
git push origin feat/your-branch
```
Then open a Pull Request into `main` on GitHub. Open PRs often (every finished piece of work),
not only once at the very end; small PRs are easier to review and cause fewer conflicts.
After your PR is merged, run `git pull origin main` on your branch again.

## 3. Commit messages

Format: `<type>: <what changed>` and add the requirement ID if there is one.

| Type | Use for |
|---|---|
| `feat` | new functionality |
| `fix` | bug fix |
| `test` | adding or changing tests |
| `docs` | documentation only |
| `chore` | setup, config, cleanup |

Examples: `feat: detect duplicate records (FR-06)`, `test: add scenario S-02 record deletion`.
Keep commits small and commit often.

## 4. Pull Requests

1. Open the PR from your branch into `main`; the template fills in automatically.
2. Fill in what you did and the related FR / scenario.
3. Make sure `pytest` passes and `ruff check .` is clean.
4. Ask at least one other member to review. Fix review comments by pushing to the same branch.
5. After approval, merge with **Squash and merge** (one clean commit per PR on `main`).

The project manager checks `main`'s history and the PRs to follow progress, so keep titles and descriptions meaningful.

## 5. Code rules (from ARCHITECTURE.md, Section 4)

**Start here:** [docs/SHARED_FORMATS.md](docs/SHARED_FORMATS.md) defines the hash rule, file formats and the
function each module must expose. Follow it exactly so our parts fit together.

- Folder layout is `src/trace_engine/<layer>/`. Layer order: `presentation` -> `application` -> `domain` -> `data`.
  A lower layer never imports an upper layer.
- Data moves between modules only as the objects in `contracts/models.py`
  (`InternalRecord`, `SignedCheckpoint`, `AuditFinding`, `AuditRules`). No global variables.
- Finding codes come only from `contracts/codes.py`. Do not invent new ones without agreement.
- `contracts/` is shared by everyone. Change it only in a dedicated PR that all members have approved.
- Cryptography: only `hashlib` (SHA-256) and the `cryptography` package (Ed25519).
- Audit order is fixed (Section 4.4): order/duplicate check first, then normalization, then gap analysis.
- Write tests for your module under `tests/unit/`; scenario tests S-01..S-07 go under `tests/scenarios/`.
- Repository content (code, comments, docs, commit messages, PRs) is written in English.

## 6. Useful commands

```powershell
pytest                 # run tests
pytest --cov=trace_engine   # with coverage
ruff check .           # lint
ruff format .          # auto-format
```
