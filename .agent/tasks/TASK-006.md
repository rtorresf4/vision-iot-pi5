# TASK-006 — Baseline Tooling + Quality Gate

## STATUS

READY

## MILESTONE

M0 — Architecture Baseline

## OBJECTIVE

Establish a deterministic and reproducible baseline quality gate before Architecture v2 implementation proceeds into M1.

The repository must have a consistent local/CI validation baseline in which:

- Black formatting checks are blocking.
- Ruff lint checks are blocking.
- mypy type checks are blocking.
- pytest tests are blocking.

Existing baseline violations may be corrected only to the minimum extent required to make these quality gates pass.

## WHY

Repository inspection and a baseline assessment performed after TASK-005 identified that the existing quality tooling is present but does not currently form a clean, deterministic quality gate.

Observed repository state:

- Black is configured and used locally and in CI.
- Ruff is configured and used locally and in CI.
- mypy is configured but CI and `make lint` currently tolerate failure through `mypy apps || true`.
- pytest is configured as the current test runner.
- pre-commit includes Black, Ruff, isort, and mypy.
- CI runs on Python 3.11.
- `pyproject.toml` declares Python 3.11 targets for Black, Ruff, and mypy.
- Ruff reports deprecated top-level `select` and `ignore` configuration.
- Existing tests currently consist of two placeholder tests.

Baseline execution against clean `main` showed:

- `black --check .` fails because 8 existing files require formatting.
- `ruff check .` reports 12 fixable baseline violations.
- `pytest -q` passes with 2 tests.
- pre-commit Black/Ruff/isort can normalize the affected files.
- pre-commit mypy reports two blocking issues:
  - missing annotation for `msg_q` in the Streamlit dashboard,
  - missing PyYAML type stubs.
- direct `mypy apps` did not complete during the manual probe and was interrupted; therefore the Implementation Agent must validate the final direct mypy command explicitly.

During TASK-006 implementation, once the temporary mypy exclusion was
removed, full `mypy apps` validation discovered one additional existing
typing issue in `apps/tools/check_camera.py`:

- `Module has no attribute "VideoWriter_fourcc" [attr-defined]`

Because excluding existing application code would weaken the intended
quality gate, human review explicitly authorized `apps/tools/check_camera.py`
as an additional allowed change for minimal remediation of this finding.

Architecture v2 requires CI to act as the quality gate (ADR-009). Before M1 Core Foundation begins, the repository should therefore establish a clean baseline rather than continue accumulating tolerated quality debt.

## ARCHITECTURE REFERENCES

- `docs/architecture.md`
- `docs/adr/009-testing-strategy.md`
- `docs/adr/012-target-repository-structure.md`
- `GEMINI.md`
- `.agent/rules/implementation.md`
- `.agent/rules/review.md`
- `docs/project-context.md`

No Architecture v2 change is introduced by this task.

No ADR is required.

## SCOPE

1. Normalize the existing Python files demonstrated by the baseline probe to violate Black/Ruff formatting or lint rules.

2. Resolve the currently observed mypy baseline violations with the smallest correct changes.

3. Add PyYAML typing support as a development/CI dependency if required for deterministic mypy validation.

4. Modernize the existing Ruff configuration so currently deprecated top-level lint settings use the supported configuration structure without changing the intended lint rule set.

5. Make mypy a blocking local quality check.

6. Make mypy a blocking CI quality check.

7. Preserve Black and Ruff as blocking checks.

8. Preserve pytest as a blocking CI/test check.

9. Keep Python 3.11 as the declared CI/tooling baseline for this task.

10. Ensure local validation and CI enforce an equivalent core quality gate: formatting, linting, typing, and tests.

11. Keep changes limited to baseline normalization and tooling configuration. Do not refactor legacy/prototype code beyond what is necessary to satisfy the established gates.

## OUT OF SCOPE

- Architecture v2 implementation.
- M1 Core Foundation implementation.
- Reorganizing code into `src/vision_iot/`.
- Replacing or redesigning the current application.
- Improving computer-vision functionality.
- MQTT redesign.
- Dashboard redesign.
- Runtime/model changes.
- Raspberry Pi deployment work.
- Benchmarking.
- Dataset/training work.
- Adding coverage thresholds.
- Introducing new quality tools.
- Broad dependency modernization.
- Changing the supported Python baseline away from 3.11.
- Replacing placeholder tests with future Architecture-v2 tests.
- General cleanup unrelated to failing quality gates.
- Refactoring code solely for style or preference.
- Modifying Architecture v2 or ADRs.

## INPUTS / CONTRACTS

Authoritative inputs:

- Current `main` repository state after TASK-005.
- `pyproject.toml`
- `.pre-commit-config.yaml`
- `Makefile`
- `.github/workflows/ci.yml`
- `requirements-dev.txt`
- existing application files identified by the baseline probe
- existing tests
- ADR-009 Testing Strategy
- ADS implementation/review rules

The baseline findings recorded in this TASK define the known remediation boundary. If implementation reveals materially broader failures, the agent must escalate instead of silently expanding scope.

## EXPECTED OUTPUT

The expected result is:

- existing affected Python files normalized to the configured formatter/linter,
- Ruff configuration using supported syntax,
- mypy baseline violations resolved,
- required typing dependency declared if necessary,
- `make lint` no longer suppressing mypy failures,
- CI no longer suppressing mypy failures,
- all required quality gates passing deterministically.

No new application feature is expected.

## ALLOWED CHANGES

The Implementation Agent may modify only:

- `pyproject.toml`
- `requirements-dev.txt`
- `.github/workflows/ci.yml`
- `Makefile`
- `.pre-commit-config.yaml` only if required to make the existing hooks consistent with the finalized baseline
- `apps/pi_detector/infer_onnx.py`
- `apps/pi_detector/main.py`
- `apps/pi_detector/mqtt_client.py`
- `apps/pi_detector/utils.py`
- `apps/streamlit_dashboard/Home.py`
- `apps/streamlit_dashboard/pages/01_Metrics.py`
- `apps/streamlit_dashboard/pages/02_History.py`
- `apps/tools/capture_dataset.py`
- `apps/tools/check_camera.py`

The task contract itself is human-controlled and must not be modified by the Implementation Agent.

## FORBIDDEN CHANGES

Do not modify:

- `.agent/tasks/TASK-006.md`
- other `.agent/tasks/`
- `.agent/rules/`
- `GEMINI.md`
- `docs/architecture.md`
- `docs/adr/`
- `docs/project-context.md`
- `README.md`
- `tests/`
- `training/`
- `deploy/`
- `models/`
- `data/`
- application files not explicitly listed under `ALLOWED CHANGES`

Also forbidden:

- adding runtime dependencies,
- adding quality tools other than the existing toolchain,
- changing Architecture v2,
- creating or modifying ADRs,
- weakening lint/type/test configuration merely to make validation pass,
- adding broad ignore rules,
- adding blanket mypy suppressions,
- adding `# type: ignore` solely to bypass a correctable baseline issue,
- reintroducing `|| true` or equivalent failure suppression,
- deleting or weakening tests,
- changing application behavior unnecessarily,
- broad refactoring,
- changing the Python baseline,
- silently expanding scope when new failures are discovered.

## ACCEPTANCE CRITERIA

1. Black reports no formatting violations.

2. Ruff reports no lint violations.

3. Ruff no longer reports the deprecated top-level `select`/`ignore` configuration warning.

4. The intended existing Ruff rule selection remains semantically equivalent after configuration modernization.

5. Direct `mypy apps` completes successfully without failure suppression.

6. The observed `msg_q` typing issue is resolved correctly.

7. PyYAML typing information is available to mypy through an explicitly declared development/CI dependency if required.

8. `make lint` treats mypy failure as blocking.

9. CI treats mypy failure as blocking.

10. CI continues to treat Black failure as blocking.

11. CI continues to treat Ruff failure as blocking.

12. CI continues to treat pytest failure as blocking.

13. `pytest -q` passes.

14. Existing tests are not modified, removed, skipped, or weakened.

15. No runtime dependency is added.

16. No new quality tool is introduced.

17. No Architecture-v2 implementation is introduced.

18. Application behavior is unchanged except where a minimal semantically equivalent edit is required for typing/lint compliance.

19. Python 3.11 remains the declared CI/tooling baseline.

20. Local and CI core quality gates are consistent in enforcing formatting, linting, typing, and tests.

21. No failure-suppression mechanism remains around the required mypy gate.

22. All changes remain within `ALLOWED CHANGES`.

23. Architecture v2 and ADRs remain unchanged.

24. The final working tree contains no formatter-generated changes outside `ALLOWED CHANGES`.

25. The existing mypy error discovered in `apps/tools/check_camera.py`
    during TASK-006 implementation is resolved through a minimal,
    semantically equivalent code correction rather than a mypy exclusion,
    ignore, or suppression.
## REQUIRED TESTS

No new application tests are required by this task because TASK-006 establishes the tooling/quality baseline rather than new application behavior.

Existing tests must remain unchanged and must pass.

The Implementation Agent must validate all formatter, linter, type-checker, pre-commit, and pytest gates against the final implementation.

## VALIDATION COMMANDS

Run at minimum:

```bash
git status --short
git diff --check

black --check .
ruff check .
mypy apps
pytest -q

make lint
make test

pre-commit run --all-files

git diff --name-only
git diff -- pyproject.toml requirements-dev.txt .github/workflows/ci.yml Makefile .pre-commit-config.yaml apps/
```

Additionally:

```bash
grep -R "mypy apps || true" Makefile .github/workflows/ci.yml
```

must return no active failure-suppression configuration.

Additionally inspect the complete final contents of every modified file.

The Implementation Report must include actual validation evidence.

## DEPENDENCIES

Prerequisites:

- TASK-001 through TASK-005 completed and integrated.
- clean `main` baseline before TASK-006 branch creation.
- existing development toolchain from `requirements-dev.txt`.

The only new Python package authorized by this task is:

- `types-PyYAML`

and only as a development/CI typing dependency if required to satisfy the existing mypy configuration.

No runtime dependency changes are authorized.

## BLOCKING CONDITIONS

Stop and escalate if:

- satisfying mypy requires materially broader application refactoring,
- new type-check failures appear outside the known baseline and cannot be resolved with small semantically neutral changes,
- a required change falls outside `ALLOWED CHANGES`,
- application behavior must materially change to satisfy a quality tool,
- a new quality tool is required,
- runtime dependencies must change,
- Python baseline changes are required,
- Architecture v2 or an ADR must change,
- tests fail for reasons requiring application redesign,
- quality gates can pass only by weakening existing rules or suppressing failures.

Use:

- `TASK_BLOCKED`
- `ARCHITECTURE_DECISION_REQUIRED`
- `HUMAN_DECISION_REQUIRED`
- `RETRY_EXHAUSTED`

as appropriate.

Do not silently expand scope.

## DELIVERABLES

The Implementation Agent must provide an Implementation Report containing:

### STATUS

`COMPLETED` or the appropriate escalation status.

### FILES CHANGED

Exact list of every modified file.

### IMPLEMENTATION SUMMARY

Explain:

- baseline formatting/lint normalization,
- Ruff configuration modernization,
- mypy remediation,
- dependency changes, if any,
- local quality-gate changes,
- CI quality-gate changes.

### TESTS ADDED / UPDATED

Expected:

`None`

Existing tests must remain unchanged.

### VALIDATION RESULTS

Provide actual evidence for every command in `VALIDATION COMMANDS`.

Explicitly report results for:

- Black,
- Ruff,
- mypy,
- pytest,
- `make lint`,
- `make test`,
- pre-commit,
- scope/diff validation.

### DEVIATIONS

Expected:

`None`

### BLOCKERS

Expected:

`None`

### OUT-OF-SCOPE OBSERVATIONS

Report relevant observations discovered during implementation without implementing them.
