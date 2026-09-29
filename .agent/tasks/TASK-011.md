# TASK-011 — Development Tool Version Alignment

## STATUS

READY

## MILESTONE

M2 Acquisition — Tooling prerequisite discovered during TASK-010 validation.

## OBJECTIVE

Restore deterministic and reproducible quality-gate behavior by aligning the
versions of development tools that are executed both from the project
environment/CI and from pre-commit.

TASK-010 exposed contradictory Ruff import-sorting behavior because the local/CI
toolchain and pre-commit were executing different Ruff versions.

Inspection showed that the same version drift also exists for Black and mypy.

This task MUST correct the tooling baseline only. It MUST NOT modify application
behavior, architecture, tests, or quality rules.

## PROBLEM STATEMENT

The current development dependency baseline leaves quality tools unpinned:

- black
- ruff
- mypy

Current installed project-environment versions:

- Black 25.1.0
- Ruff 0.12.12
- mypy 1.17.1

Current pre-commit versions:

- Black 24.4.2
- Ruff 0.5.6
- mypy 1.10.0

CI installs requirements-dev.txt and therefore follows the unpinned development
dependency versions, while pre-commit uses independently pinned hook versions.

This permits local/CI quality gates and pre-commit to apply different behavior
to the same working tree.

The defect was reproduced during TASK-010:

1. Ruff from the project virtual environment required a blank line between
   third-party and first-party imports.
2. The Ruff pre-commit hook removed that same blank line.
3. Re-running the project Ruff then rejected the pre-commit result.

Therefore a single working-tree state could not satisfy both quality paths.

## ALLOWED CHANGES

Only:

- .agent/tasks/TASK-011.md
- requirements-dev.txt
- .pre-commit-config.yaml

No other file may be modified.

## REQUIRED IMPLEMENTATION

Align the tools that are independently executed by both the project
environment/CI and pre-commit:

- Black
- Ruff
- mypy

Use one explicit version for each tool across both execution paths.

Target versions:

- black==25.1.0
- ruff==0.12.12
- mypy==1.17.1

The corresponding pre-commit hook revisions MUST use the equivalent versions.

Do not change existing quality rules, command-line arguments, lint selections,
formatter configuration, mypy configuration, or hook behavior except where
strictly required for version alignment.

The existing Ruff `--fix` pre-commit behavior MUST be preserved.

## OUT OF SCOPE

Do NOT:

- modify application or test code
- modify architecture or ADRs
- modify docs/project-context.md
- modify Makefile
- modify CI workflow
- add new tools
- remove existing tools
- clean up or remove isort
- change lint/type-check/formatting rules
- modify TASK-010
- restore the TASK-010 stash
- perform unrelated dependency upgrades
- redesign the quality gate

`isort` remaining in requirements-dev.txt is explicitly outside this task.

## REPRODUCIBILITY REQUIREMENT

A fresh installation from requirements-dev.txt and the pre-commit environment
MUST resolve the aligned Black, Ruff, and mypy versions intentionally specified
by this task.

Local/CI execution and pre-commit MUST no longer use independently drifting
versions of these tools.

## QUALITY GATE

After implementation, run:

black --version
ruff --version
mypy --version

black --check .
ruff check .
mypy apps src
pytest -q

make lint
make test

pre-commit run --all-files

Then run again:

make lint

The second `make lint` is mandatory. It verifies that pre-commit has not
transformed the repository into a state rejected by the project-environment
toolchain.

Finally run:

git diff --check
git status --short

If pre-commit modifies any file, inspect the modification and repeat the
relevant/full validation until a stable state is reached.

## ACCEPTANCE CRITERIA

1. requirements-dev.txt explicitly pins Black to 25.1.0.
2. requirements-dev.txt explicitly pins Ruff to 0.12.12.
3. requirements-dev.txt explicitly pins mypy to 1.17.1.
4. The Black pre-commit hook uses the equivalent 25.1.0 release.
5. The Ruff pre-commit hook uses the equivalent 0.12.12 release.
6. The mypy pre-commit hook uses the equivalent 1.17.1 release.
7. Ruff `--fix` hook behavior remains enabled.
8. No quality rules are changed.
9. No application code is changed.
10. No tests are changed.
11. No architecture or ADR files are changed.
12. No Makefile or CI workflow is changed.
13. No tools are added or removed.
14. isort is not modified as part of this task.
15. `make lint` passes before pre-commit.
16. `make test` passes.
17. `pre-commit run --all-files` reaches a stable passing state.
18. `make lint` still passes after pre-commit.
19. `git diff --check` passes.
20. Final working-tree changes are restricted to the authorized TASK-011 files.

## BLOCKING / ESCALATION CONDITIONS

Stop and escalate if:

- aligning versions requires changing quality rules;
- one of the target versions is incompatible with the current project;
- a hook cannot use the corresponding target version;
- application or test changes appear necessary;
- Makefile or CI changes appear necessary;
- dependency resolution requires unrelated upgrades;
- the aligned tools still produce contradictory transformations;
- any architectural or product behavior change becomes necessary.

## IMPLEMENTATION AGENT REPORT

The Implementation Agent MUST report:

- STATUS
- files changed
- exact versions established
- implementation summary
- exact result of every required validation command
- final `git status --short`
- deviations
- escalation, if any
