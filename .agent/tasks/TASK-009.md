# TASK-009 — Tooling Import Conflict Fix

## STATUS

READY

## MILESTONE

M0 — Architecture & Engineering Foundation

## OBJECTIVE

Restore a deterministic and internally consistent Python quality gate by removing
the conflicting duplicate import-sorting responsibility between Ruff and isort.

Ruff remains the single authority for import sorting.

## WHY

TASK-008 exposed a pre-existing conflict in the quality gate established by
TASK-006.

The conflict was reproduced deterministically:

1. The Ruff pre-commit hook (`v0.5.6`, with `--fix`) removes the blank line
   between a third-party import and a first-party `vision_iot` import.
2. The isort pre-commit hook (`5.13.2`, `profile = "black"`) restores that
   blank line.
3. Running the complete pre-commit pipeline therefore reports both hooks as
   modifying the same file and cannot reach a stable passing state.

The issue belongs to the tooling baseline rather than to TASK-008 acquisition
logic.

## ARCHITECTURE REFERENCES

- TASK-006 — Baseline Tooling + Quality Gate
- `.pre-commit-config.yaml`
- `pyproject.toml`

No product architecture or ADR change is introduced by this task.

## SCOPE

- Remove the standalone isort pre-commit hook.
- Keep Ruff as the sole import-sorting authority through its existing `I`
  lint rules.
- Preserve the existing Ruff configuration and lint rule selection.
- Preserve Black, mypy, pytest, and all other quality-gate behavior.
- Verify that the complete quality gate reaches a stable passing state.
- Verify that running pre-commit repeatedly does not modify tracked files.

## OUT OF SCOPE

- Changes to product/application code.
- Changes to acquisition contracts or TASK-008 implementation.
- Changes to Ruff lint rules.
- Ruff version upgrades.
- Black, mypy, pytest, or other tooling upgrades.
- Changes to `pyproject.toml`.
- New dependencies.
- Architecture or ADR changes.
- General tooling cleanup or refactoring.

## INPUTS / CONTRACTS

- Existing TASK-006 quality-gate baseline.
- Existing `.pre-commit-config.yaml`.
- Existing Ruff configuration in `pyproject.toml`.
- Reproduced Ruff/isort import-sorting conflict discovered during TASK-008.

## EXPECTED OUTPUT

Modified:

~~~~text
.pre-commit-config.yaml
~~~~

Created:

~~~~text
.agent/tasks/TASK-009.md
~~~~

No other repository files are expected to change.

## ALLOWED CHANGES

- `.pre-commit-config.yaml`
- `.agent/tasks/TASK-009.md`

## FORBIDDEN CHANGES

- `pyproject.toml`
- `src/**`
- `apps/**`
- `tests/**`
- `docs/adr/**`
- Existing TASK contracts
- Dependency manifests or lock files
- CI workflow files
- Makefile

## ACCEPTANCE CRITERIA

1. The standalone isort pre-commit hook is removed.
2. Ruff remains configured as an active pre-commit hook.
3. Ruff continues to run with its existing `--fix` argument.
4. Ruff's existing `I` import-sorting rules remain unchanged.
5. Black remains configured and unchanged.
6. mypy remains configured and unchanged.
7. No Ruff version change is introduced.
8. No unrelated pre-commit hook is changed.
9. `pyproject.toml` is unchanged.
10. No product or test code is changed.
11. No dependency is added or removed.
12. `black --check .` passes.
13. `ruff check .` passes.
14. `mypy apps src` passes.
15. `pytest -q` passes.
16. `make lint` passes.
17. `make test` passes.
18. `pre-commit run --all-files` passes.
19. A second consecutive `pre-commit run --all-files` also passes without
    modifying repository files.
20. Post-validation `git status --short` contains only the files authorized
    by this TASK.
21. `git diff --check` passes.

## REQUIRED TESTS

No new automated product tests are required.

Regression evidence is provided by running the complete quality gate twice
consecutively and demonstrating that it reaches a stable state without file
modification.

## VALIDATION COMMANDS

~~~~bash
black --check .
ruff check .
mypy apps src
pytest -q
make lint
make test
pre-commit run --all-files
pre-commit run --all-files
git diff --check
git status --short
~~~~

If the project tools are available only from the repository virtual
environment, equivalent `.venv/bin/...` invocations are acceptable.

## DEPENDENCIES

- TASK-006 quality-gate baseline.
- Existing Ruff import-sorting rules (`I`) in `pyproject.toml`.

TASK-008 is not a dependency and remains suspended separately while this
tooling defect is corrected.

## BLOCKING CONDITIONS

Return `TASK_BLOCKED` if removing the standalone isort hook does not produce a
stable quality gate without requiring additional configuration or code changes.

Return `HUMAN_DECISION_REQUIRED` if resolving the conflict requires choosing
between alternative tooling strategies beyond the scope explicitly authorized
by this TASK.

Return `ARCHITECTURE_DECISION_REQUIRED` if the proposed fix unexpectedly
requires a product architecture or ADR change.

Do not broaden scope to repair additional tooling issues discovered during
validation.

## DELIVERABLES

The Implementation Agent must provide an Implementation Report containing:

### STATUS

`COMPLETED` or the appropriate escalation status.

### FILES CHANGED

List every created or modified file.

### IMPLEMENTATION SUMMARY

Concise description of what was implemented.

### TESTS ADDED / UPDATED

List new or modified tests, or explicitly state that none were required.

### VALIDATION RESULTS

Report each validation command and its result.

### DEVIATIONS

Any deviation from this TASK.

### BLOCKERS

Any unresolved blocker.

### OUT-OF-SCOPE OBSERVATIONS

Any issue discovered that is outside this TASK without modifying it.
