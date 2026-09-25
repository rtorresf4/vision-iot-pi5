# TASK-007 — Core Foundation

## STATUS
READY

## MILESTONE
M1 — Core Foundation

## OBJECTIVE
Establish the minimum installable, importable, and quality-gated
Architecture-v2 Python package foundation using a `src` layout.

The task must provide:
- a valid `src/vision_iot/` Python package,
- setuptools package discovery using the `src` layout,
- deterministic installation/import verification,
- one minimal meaningful package-foundation test,
- blocking mypy coverage for both `apps/` and `src/`,
- preservation of every blocking quality gate established by TASK-006.

No application behavior or future Architecture-v2 behavioral contract is
introduced by this task.

## WHY
TASK-006 established the repository's blocking quality gate.

Architecture-v2 implementation is now entering M1 and requires a real
project-owned Python package under `src/vision_iot/`.

The package foundation must be introduced incrementally without performing
a big-bang migration of the existing pre-Architecture-v2 implementation and
without creating speculative empty architectural layers.

Because Architecture-v2 source code will now exist under `src/`, the existing
blocking mypy gate must be extended so both existing `apps/` code and new
`src/` code remain protected.

## ARCHITECTURE REFERENCES
- `docs/architecture.md`
- `docs/adr/009-testing-strategy.md`
- `docs/adr/012-target-repository-structure.md`
- `GEMINI.md`
- `.agent/rules/implementation.md`
- `.agent/rules/review.md`
- `docs/project-context.md`
- `.agent/tasks/TASK-006.md`

Relevant accepted principles:
- Architecture-v2 implementation progressively moves toward
  `src/vision_iot/`.
- Migration is incremental, not a big-bang rewrite.
- Tests should be deterministic and hardware-independent whenever possible.
- CI is a real blocking quality gate.
- Future architectural layers are created when required by real behavior or
  contracts, not as speculative empty scaffolding.
- No Architecture-v2 change, ADR, new architectural decision, or new
  dependency is required by this task.

## SCOPE
1. Create the minimum Architecture-v2 package layout:

       src/
       └── vision_iot/
           └── __init__.py

2. Configure `pyproject.toml` so the existing setuptools build system
   discovers `vision_iot` using the `src` layout.

3. Preserve the existing setuptools build backend.

4. Add exactly one package-foundation test:

       tests/test_package.py

5. The test must meaningfully verify that the package foundation is
   importable.

6. Extend blocking mypy validation so both existing `apps/` code and new
   `src/` code are checked.

7. Apply that mypy extension consistently to:
   - local validation through `Makefile`,
   - GitHub Actions CI.

8. Preserve all blocking quality gates established by TASK-006.

9. Validate installation and import using the repository's existing Python
   packaging mechanism.

## OUT OF SCOPE
- Camera abstraction.
- `FrameSource`.
- Frame acquisition.
- OpenCV migration.
- Preprocessing.
- Inference engines.
- ONNX Runtime work.
- NCNN work.
- YOLO26n work.
- Model loading.
- Model parsing.
- Postprocessing.
- Domain inspection logic.
- Inspection events.
- MQTT redesign.
- Event schemas.
- Dashboard or Streamlit changes.
- DHT22.
- PIR.
- Additional telemetry.
- Runtime configuration system.
- Raspberry Pi deployment.
- systemd changes.
- Benchmarking.
- Training.
- Dataset work.
- Legacy application migration.
- Legacy application refactoring.
- Removal or replacement of existing placeholder tests.
- Coverage thresholds.
- New quality tools.
- Python baseline changes.
- Dependency modernization.
- Architecture-v2 changes.
- ADR changes.

TASK-007 must not implement conceptual D4/D5 or future milestone contracts,
including:
- `Frame`
- `FrameSource`
- `ModelInput`
- `RawInference`
- `Detection`
- `InferenceResult`
- `InspectionEvent`
- `Preprocessor`
- `InferenceEngine`
- `Postprocessor`
- `InspectionLogic`
- `InspectionPipeline`
- `EventPublisher`
- `MqttPublisher`

These belong to future milestone/TASK work.

## INPUTS / CONTRACTS
TASK-007 starts from the clean post-TASK-006 baseline.

Relevant baseline commits:
- `295a32f` — `docs: checkpoint project context after TASK-006`
- `a41732e` — Merge `task/006-baseline-tooling-quality-gate`
- `8dadd1c` — `chore: establish baseline quality gate (TASK-006)`

TASK-006 established blocking quality gates for:
- Black
- Ruff
- mypy
- pytest

The existing mypy gate currently covers `apps/`.

TASK-007 must preserve that coverage and extend the blocking type-checking
invariant to include Architecture-v2 source under `src/`.

Conceptually:

    apps/
        +
    src/
        ↓
    blocking mypy gate

No dependency changes are required or authorized.

The existing toolchain remains:
- setuptools
- pytest
- Black
- Ruff
- mypy

## EXPECTED OUTPUT
The repository contains the minimum Architecture-v2 Python package foundation:

    src/
    └── vision_iot/
        └── __init__.py

The package is discoverable through the existing setuptools packaging
mechanism, installable, and importable.

A minimal deterministic test protects the package foundation.

Both:
- existing/pre-Architecture-v2 Python code under `apps/`, and
- Architecture-v2 Python code under `src/`

are covered by the blocking mypy quality gate locally and in CI.

No application behavior, behavioral contracts, future architectural layers,
or dependency changes are introduced.

## ALLOWED CHANGES
The Implementation Agent may modify or create only:

- `pyproject.toml`
- `Makefile`
- `.github/workflows/ci.yml`
- `src/vision_iot/__init__.py`
- `tests/test_package.py`

Creation of parent directories required for
`src/vision_iot/__init__.py` is naturally permitted.

No other implementation files are authorized.

`TASK-007.md` is human-authored and immutable during task execution.

## FORBIDDEN CHANGES
The Implementation Agent must not modify:

- `apps/`
- `training/`
- `deploy/`
- `models/`
- `data/`
- `README.md`
- `docs/`
- `GEMINI.md`
- `.agent/rules/`
- any other `.agent/tasks/`
- `requirements.txt`
- `requirements-dev.txt`
- `requirements-ci.txt`
- `requirements-train.txt`
- `.pre-commit-config.yaml`
- `tests/test_mqtt.py`
- `tests/test_perf.py`

The Implementation Agent must not create speculative Architecture-v2 layer
packages, including:

- `src/vision_iot/application/`
- `src/vision_iot/domain/`
- `src/vision_iot/vision/`
- `src/vision_iot/hardware/`
- `src/vision_iot/infrastructure/`
- `src/vision_iot/config/`

The Implementation Agent must not:
- modify `TASK-007.md`,
- add, remove, or modify dependencies,
- introduce Poetry, Hatch, PDM, alternative build backends, additional
  packaging tools, new test frameworks, or new quality tools,
- weaken, skip, ignore, or bypass an existing quality gate,
- introduce application behavior,
- introduce D4/D5 or future milestone contracts,
- change the Python 3.11 tooling/CI baseline,
- change Architecture v2 or any ADR.

## ACCEPTANCE CRITERIA
1. `src/vision_iot/` exists as a valid Python package.
2. `src/vision_iot/__init__.py` exists.
3. `pyproject.toml` configures setuptools to discover the package using the
   `src` layout.
4. The existing setuptools build backend is preserved.
5. The project package can be installed successfully using the repository's
   standard Python packaging mechanism.
6. `import vision_iot` succeeds after installation.
7. `tests/test_package.py` exists.
8. The new test meaningfully verifies that the package foundation is
   importable.
9. Existing tests remain unchanged.
10. The complete pytest suite passes.
11. Black reports no violations.
12. Ruff reports no violations.
13. mypy successfully checks both `apps` and `src`.
14. `make lint` includes Architecture-v2 `src` code in the blocking mypy gate.
15. GitHub Actions CI includes Architecture-v2 `src` code in the blocking
    mypy gate.
16. Black remains blocking.
17. Ruff remains blocking.
18. mypy remains blocking.
19. pytest remains blocking.
20. `make lint` passes.
21. `make test` passes.
22. pre-commit passes.
23. No existing quality gate is weakened or bypassed.
24. No dependency is added, removed, or modified.
25. No application behavior is introduced.
26. No Architecture-v2 D4/D5 behavioral/domain/vision contracts are
    implemented.
27. No speculative empty Architecture-v2 layer packages are created.
28. Existing legacy/prototype application code remains unchanged.
29. Existing tests are not modified, removed, skipped, or weakened.
30. Python 3.11 remains the tooling/CI baseline.
31. Architecture v2 and ADRs remain unchanged.
32. All implementation changes remain within `ALLOWED CHANGES`.

## REQUIRED TESTS
Add exactly one new test file:

    tests/test_package.py

Its responsibility is limited to meaningfully verifying the package
foundation introduced by TASK-007.

Existing tests:

    tests/test_mqtt.py
    tests/test_perf.py

must remain unchanged and continue to pass.

No camera, MQTT, model, runtime, Raspberry Pi, hardware, domain, or
integration tests are required by TASK-007.

## VALIDATION COMMANDS
The Implementation Agent must execute and report actual evidence for:

    git status --short
    git diff --check

    black --check .
    ruff check .
    mypy apps src
    pytest -q

    make lint
    make test

    pre-commit run --all-files

Package installation/import validation:

    python -m pip install -e .
    python -c "import vision_iot"

Scope validation:

    git diff --name-only

    git diff -- \
      pyproject.toml \
      Makefile \
      .github/workflows/ci.yml \
      src/vision_iot/__init__.py \
      tests/test_package.py

Quality-gate inspection:

    grep -n "mypy" Makefile .github/workflows/ci.yml

New/untracked files must also be inspected directly because normal
`git diff` does not include untracked file contents.

The Implementation Report must contain actual validation evidence rather
than unsupported statements that validation passed.

## DEPENDENCIES
- TASK-001 completed.
- TASK-002 completed.
- TASK-003 completed.
- TASK-004 completed.
- TASK-005 completed.
- TASK-006 completed and integrated.
- `docs/project-context.md` updated after TASK-006.
- TASK-007 branch created from clean commit `295a32f`.

No new Python or tooling dependency is required by TASK-007.

## BLOCKING CONDITIONS
Stop and use the appropriate ADS escalation mechanism if:

1. New Python dependencies are required.
2. A different build backend or packaging tool appears necessary.
3. Existing code under `apps/` must be modified.
4. Existing tests must be modified to make the new foundation pass.
5. A required change falls outside `ALLOWED CHANGES`.
6. Architecture v2 or an ADR would need modification.
7. A D4/D5 contract must be designed or implemented to complete the task.
8. The full Architecture-v2 package hierarchy must be created for technical
   reasons not anticipated by this task.
9. A quality gate must be weakened, ignored, or bypassed.
10. mypy cannot cover `apps` and `src` without materially broader
    remediation.
11. Runtime, development, CI, or training dependencies must change.
12. The Python 3.11 baseline must change.
13. Existing legacy/prototype application behavior would need to change.
14. The task cannot be completed without materially expanding M1 scope.

Use the existing ADS escalation mechanisms as appropriate:
- `TASK_BLOCKED`
- `ARCHITECTURE_DECISION_REQUIRED`
- `HUMAN_DECISION_REQUIRED`
- `RETRY_EXHAUSTED`

Do not silently expand scope.

## DELIVERABLES
1. Minimum `src/vision_iot/` package foundation.
2. Setuptools `src`-layout package discovery configuration.
3. `tests/test_package.py`.
4. Extended blocking mypy coverage for `apps` and `src` locally and in CI.
5. Successful deterministic validation evidence.
6. Implementation Report containing:
   - STATUS
   - FILES CHANGED
   - IMPLEMENTATION SUMMARY
   - TESTS ADDED/UPDATED
   - VALIDATION RESULTS
   - DEVIATIONS
   - BLOCKERS
